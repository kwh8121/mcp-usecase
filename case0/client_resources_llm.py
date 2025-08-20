from dotenv import load_dotenv
load_dotenv()

import asyncio, json
from typing import Any, Dict

# --------------------- 클라이언트 초기화 ---------------------
from openai import AsyncOpenAI
from fastmcp import Client as MCPClient

llm_client = AsyncOpenAI()  # OpenAI LLM 클라이언트
mcp_client = MCPClient("server_resources.py")   # FastMCP 리소스 서버 클라이언트


# --------------------- read_resource 함수 정의 ---------------------
# LLM이 사용할 수 있는 가상 함수 스키마 정의
READ_RESOURCE_SCHEMA: Dict[str, Any] = {
    "type": "function",
    "name": "read_resource",
    "description": (
        "Read a FastMCP resource and return its content as a string. "
        "Example URIs: resource://greeting, data://config, "
        "repos://{owner}/{repo}/info"
        "You must use each URI exactly as it is registered on the server."
        "When extracting fields from a JSON object, do not append a slash to the URI."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "uri": {
                "type": "string",
                "description": "Full resource URI to fetch.",
            },
            "params": {
                "type": "object",
                "description": "Optional parameters for templated resources.",
                "additionalProperties": True,
            },
        },
        "required": ["uri"],
    },
}

# --------------------- LLM 질의 함수 ---------------------
async def query_llm(question: str) -> str:
    # 1단계: MCP 서버에서 사용 가능한 리소스 목록 가져오기
    fixed   = await mcp_client.list_resources()            # 고정 URI
    templs  = await mcp_client.list_resource_templates()   # 템플릿 URI

    # 시스템 메시지로 사용할 리소스 목록 문서 생성
    resource_doc = (
        "### Available resources\n"
        + "\n".join(f"- {r.uri}" for r in fixed) + "\n"
        + "### Available templates\n"
        + "\n".join(f"- {t.uriTemplate}" for t in templs)
    )

    print(f"resource_doc:\n{resource_doc}\n")

    # 2단계: LLM에 첫 번째 질의 전송
    first = await llm_client.responses.create(
        model="gpt-4o",
        input=[
            {"role": "system", "content": resource_doc},
            {"role": "user",   "content": question},
        ],
        tools=[READ_RESOURCE_SCHEMA],
    )

    # 함수 호출이 없으면 바로 답변 반환
    calls = [o for o in first.output if getattr(o, "type", "") == "function_call"]
    if not calls:
        return first.output_text


    # 3단계: 함수 호출이 있다면 → 해당 리소스 읽어서 함수 결과로 제공
    next_input = [
        # 시스템 메시지로 리소스 목록 추가
        {"role": "system", "content": resource_doc},
        {"role": "user",   "content": question},
    ]

    for call in calls:
        # resource 예제여서 read_resource 함수만 처리
        if call.name != "read_resource":
            continue

        # 함수 인자 추출: 문자열(JSON) 또는 dict 형태일 수 있음
        args = call.arguments
        if isinstance(args, str):
            args = json.loads(args)

        uri    = args["uri"]
        params = args.get("params") or {}

        # MCP에서 실제 리소스 값 읽기
        res    = await mcp_client.read_resource(uri, **params)
        output = res[0].text  # bytes 리소스일 땐 .bytes

        # 함수 호출 및 결과(서버에서 resource를 통해 제공한 데이터)를 LLM에 다시 전달
        next_input.append(call)
        next_input.append(
            {
                "type":   "function_call_output",
                "call_id": call.call_id,
                "output": str(output),
            }
        )

    # 4단계: LLM에 결과 반영 후 최종 답변 요청
    final = await llm_client.responses.create(
        model="gpt-4o",
        input=next_input,
    )
    return final.output_text


# --------------------- 메인 루프 ---------------------
async def main():
    async with mcp_client:
        print("MCP connected:", mcp_client.is_connected())

        while True:
            question = input("\n질문을 입력하세요 (exit 입력 시 종료): ")
            if question.strip().lower() == "exit":
                break

            answer = await query_llm(question)
            print(f"\nLLM 답변 ▶ {answer}")            

    print("MCP connected:", mcp_client.is_connected())


if __name__ == "__main__":
    asyncio.run(main())
