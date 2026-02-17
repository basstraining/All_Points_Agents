"""Quick test: connect to the Arcade Gateway and list tools."""

import asyncio
import yaml
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

GATEWAY_URL = "https://api.arcade.dev/mcp/allpoints-demo"

async def main():
    # Load access token from Arcade CLI credentials
    with open("/Users/nathanbass/.arcade/credentials.yaml") as f:
        creds = yaml.safe_load(f)
    token = creds["cloud"]["auth"]["access_token"]

    print(f"Gateway: {GATEWAY_URL}")
    print(f"Token: {token[:20]}...{token[-10:]}")
    print()

    http_client = httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"},
        timeout=30.0,
    )

    async with http_client:
        async with streamable_http_client(GATEWAY_URL, http_client=http_client) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                print(f"Connected! Found {len(result.tools)} tools:\n")
                for tool in result.tools:
                    print(f"  - {tool.name}")

                # Test one tool
                print("\n--- Testing get_exception_summary ---")
                test = await session.call_tool("get_exception_summary", {})
                for block in test.content:
                    text = getattr(block, "text", str(block))
                    print(text[:500])

if __name__ == "__main__":
    asyncio.run(main())
