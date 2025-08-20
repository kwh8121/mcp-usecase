import asyncio
from fastmcp import Client
from fastmcp.prompts.prompt import PromptMessage

client = Client("server_prompts.py")


# --------------------- 서버에서 반환한 프롬프트를 보기 좋게 출력하는 함수 ---------------------
def show(title: str, result) -> None:
    messages = getattr(result, "messages", result)

    print(f"\n── {title} ({len(messages)} msg) ──")
    for m in messages:
        role = getattr(m, "role", "user")
        content = getattr(m, "content", m)
        text = getattr(content, "text", content)
        print(f"[{role}] {text}")


async def main() -> None:
    async with client:
        print("connected:", client.is_connected())

        # 프롬프트 목록 가져오기
        print("prompts on server:", [p.name for p in await client.list_prompts()])

        # ask_about_topic - 기본 문자열을 반환
        r1 = await client.get_prompt("ask_about_topic", {"topic": "MCP"})
        show("ask_about_topic", r1)

        # generate_code_request - 특정 메시지 형식을 반환
        r2 = await client.get_prompt(
            "generate_code_request",
            {
                "language": "Python",
                "task_description": "반복문으로 피보나치 수열을 계산",
            },
        )
        show("generate_code_request", r2)

        # roleplay_scenario - 메시지 리스트를 반환
        r3 = await client.get_prompt(
            "roleplay_scenario",
            {
                "character": "홍길동",
                "situation": "현시대에 시민을 돕는 상황",
            },
        )
        show("roleplay_scenario", r3)

        # data_based_prompt - 비동기 프롬프트 함수
        r4 = await client.get_prompt("data_based_prompt", {"book_id": "003"})
        show("data_based_prompt", r4)

    print("\nconnected:", client.is_connected())


if __name__ == "__main__":
    asyncio.run(main())
