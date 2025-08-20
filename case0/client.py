import asyncio
from fastmcp import Client


client = Client("server.py")


async def main():
    async with client:
        print(f"Client connected: {client.is_connected()}")

        tools = await client.list_tools()
        print(f"Available tools: {tools}")

        if any(tool.name == "get_multiplication" for tool in tools):
            result = await client.call_tool("get_multiplication", {"a": 3, "b": 7})
            print(f"get_multiplication result: {result}")

    print(f"Client connected: {client.is_connected()}")


if __name__ == "__main__":
    asyncio.run(main())
