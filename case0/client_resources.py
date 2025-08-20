import asyncio, json
from fastmcp import Client

client = Client("server_resources.py")


async def main():
    async with client:
        # 연결 상태
        print("connected:", client.is_connected())

        # 사용할 수 있는 리소스 목록
        resources = await client.list_resources()
        print("resources:", [r.uri for r in resources])

        # 사용할 수 있는 리소스 템플릿 목록
        templates = await client.list_resource_templates()
        print("templates:", [t.uriTemplate for t in templates])

        # 1) 단순 리소스
        greet = await client.read_resource("resource://greeting")
        print("greeting:", greet[0].text)

        # 2) JSON 리소스
        cfg_raw = await client.read_resource("data://config")
        cfg = json.loads(cfg_raw[0].text)
        print("config.version:", cfg["version"])

        # 3) 파라미터 들어가는 템플릿형 리소스
        repo_raw = await client.read_resource("repos://openai/gpt-4/info")
        repo_info = json.loads(repo_raw[0].text)
        print("stars:", repo_info["stars"])

    print("connected:", client.is_connected())


if __name__ == "__main__":
    asyncio.run(main())
