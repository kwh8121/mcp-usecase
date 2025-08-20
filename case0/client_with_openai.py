import asyncio, json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from fastmcp import Client as FastMCPClient
from typing import Any, Dict, List, Optional
from langchain_teddynote import logging

# 프로젝트 이름을 입력합니다.
load_dotenv()

logging.langsmith("mcp-server")


llm_client = AsyncOpenAI()
fastmcp_client = FastMCPClient("server.py")


# MCP -> OpenAI 툴 스키마 변환
def to_openai_schema(tool) -> Dict[str, Any]:

    # 입력 스키마 추출 ( 다양한 속성명 시도 )
    raw_schema = (
        getattr(tool, "inputSchema", None)
        or getattr(tool, "input_schema", None)
        or getattr(tool, "parameters", None)
    )

    # 다양한 형태를 dict(JSON-Schema) 로 통일
    if raw_schema is None:
        schema: Dict[str, Any] = {
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }

    elif isinstance(raw_schema, dict):
        schema = raw_schema

    elif hasattr(raw_schema, "model_json_schema"):  # Pydantic v2 모델
        schema = raw_schema.model_json_schema()

    elif isinstance(raw_schema, list):  # list[dict]
        props, required = {}, []
        for p in raw_schema:
            props[p["name"]] = {
                "type": p["type"],
                "description": p.get("description", ""),
            }
            if p.get("required", True):
                required.append(p["name"])
        schema = {"type": "object", "properties": props}
        if required:
            schema["required"] = required

    else:  # 알 수 없는 형식
        schema = {"type": "object", "properties": {}, "additionalProperties": True}

    # 필수 키 보강
    schema.setdefault("type", "object")
    schema.setdefault("properties", {})
    if "required" not in schema:
        schema["required"] = list(
            schema["properties"].keys()
        )  # 모두 optional 로 두고 싶다면 []

    # OpenAI 툴 JSON 반환
    return {
        "type": "function",
        "name": tool.name,
        "description": getattr(tool, "description", ""),
        "parameters": schema,
    }


async def query_llm(question: str, tool_schemas: List[Dict[str, Any]]) -> str:

    ########## 1차 요청 ##########
    resp = await llm_client.responses.create(
        model="gpt-4o",
        input=[{"role": "user", "content": question}],
        tools=tool_schemas,
    )

    ##### 툴 호출이 없을 때 #####
    tool_calls = [o for o in resp.output if getattr(o, "type", "") == "function_call"]
    if not tool_calls:
        print("툴 호출 없음, 바로 답변 반환")
        return resp.output_text

    ##### 결과를 담을 next_input 에 user 질문 유지 #####
    next_input: List[Any] = [{"role": "user", "content": question}]

    ########## 각 툴 호출 처리 ##########
    for call in tool_calls:
        # MCP 서버 실행 (arguments 는 str일 수도 dict일 수도 있음)
        print(f"call.name: {call.name}, call.id: {call.call_id}")
        args = call.arguments
        if isinstance(args, str):
            args = json.loads(args)
            print(f"args (str): {args}")
        result = await fastmcp_client.call_tool(call.name, args)

        # 호출 자체를 메시지 배열에 추가
        next_input.append(call)
        # 실행 결과를 function_call_output 형식으로 추가
        next_input.append(
            {
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": str(result),
            }
        )

    print(f"next_input: {next_input}")

    ########## 2차 호출 -> 최종 답변 ##########
    final = await llm_client.responses.create(
        model="gpt-4o",
        input=next_input,
    )
    return final.output_text


async def main():

    async with fastmcp_client:

        print(f"Client connected: {fastmcp_client.is_connected()}")

        tools = await fastmcp_client.list_tools()

        # MCP 도구를 OpenAI 툴 스키마로 변환
        tool_schemas = [to_openai_schema(tool) for tool in tools]

        # print(f"{'++'*50}\n")
        # print(f"tool_schemas: {tool_schemas}")
        # tool_schemas: [
        # <coroutine object to_openai_schema at 0x0000024DC03C97A0>,
        # <coroutine object to_openai_schema at 0x0000024DC03C9690>,
        # <coroutine object to_openai_schema at 0x0000024DC03C9580>,
        # <coroutine object to_openai_schema at 0x0000024DC03C99C0>]
        # print(f"\n{'++'*50}\n")

        while True:
            question = input("질문을 입력하세요: ")
            if question.strip().lower() == "exit":
                break

            result = await query_llm(question, tool_schemas)

            print(f"결과: {result}")

    print(f"\nMCP connected → {fastmcp_client.is_connected()}")


if __name__ == "__main__":
    asyncio.run(main())
