from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message, PromptMessage, TextContent
import asyncio

mcp = FastMCP(name="PromptServer")


# 기본 문자열을 반환하는 프롬프트
@mcp.prompt
def ask_about_topic(topic: str) -> str:
    """Generates a user message asking for an explanation of a topic."""
    return f"'{topic}' 개념을 쉽게 설명해 주세요."


# 특정 메시지 형식을 반환하는 프롬프트
@mcp.prompt
def generate_code_request(language: str, task_description: str) -> PromptMessage:
    """Generates a user message requesting code generation."""
    content = (
        f"{language}로 다음 작업을 수행하는 함수를 작성해 주세요.: {task_description}"
    )
    return PromptMessage(role="user", content=TextContent(type="text", text=content))


# 메시지 리스트를 반환하는 프롬프트
@mcp.prompt
def roleplay_scenario(character: str, situation: str) -> list[Message]:
    """Sets up a roleplaying scenario with initial messages."""
    return [
        Message(f"역할극입니다. 당신은 {character}이고 상황은 {situation}입니다."),
        Message(
            "알겠습니다. 준비가 완료되었습니다. 다음으로 뭘 할까요?", role="assistant"
        ),
    ]


SAMPLE_DATA = {
    "001": {
        "content": "『노르웨이의 숲』, 무라카미 하루키, 1987년, 현대문학, 사랑과 상실"
    },
    "002": {"content": "『데미안』, 헤르만 헤세, 1919년, 성장소설, 자아 발견"},
    "003": {
        "content": "『어린 왕자』, 앙투안 드 생텍쥐페리, 1943년, 우화, 순수와 인간관계"
    },
}


# 비동기 프롬프트 함수
@mcp.prompt
async def data_based_prompt(book_id: str) -> str:
    """Generates a prompt based on book data."""
    await asyncio.sleep(0)

    data = SAMPLE_DATA.get(
        book_id,
        {"content": f"도서 ID '{book_id}'에 해당하는 정보가 없습니다."},
    )
    return f"다음 책 정보를 바탕으로 간단한 리뷰를 작성해 줘: {data['content']}"


if __name__ == "__main__":
    mcp.run()
