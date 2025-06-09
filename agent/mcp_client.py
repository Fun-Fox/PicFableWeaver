import asyncio
from fastmcp import Client
from loguru import logger

config = {
    "mcpServers": {
        "caption": {
            "url": "http://127.0.0.1:8000/mcp",
            "transport": "streamable-http"
        }
    }
}

client = Client(config)


def mcp_get_tools():
    """从MCP服务器获取可用工具。
    """

    async def _get_tools():
        async with client:
            logger.info(f"客户端已连接: {client.is_connected()}")
            # 在上下文中调用MCP方法
            tools = await client.list_tools()
            logger.info(f"可用工具: {tools}")
            return tools

    return asyncio.run(_get_tools())


def mcp_call_tool(tool_name=None, arguments=None):
    """调用MCP服务器上的工具。
    """

    async def _call_tool():
        async with client:
            logger.info(f"客户端已连接: {client.is_connected()}")
            # tools = await client.list_tools()
            # if any(tool.name == tool_name for tool in tools):
            result = await client.call_tool(name=tool_name, arguments=arguments)
            print(f"调用结果: {result}")
            return result

    return asyncio.run(_call_tool())


if __name__ == "__main__":
    tools_info = mcp_get_tools()
    print(tools_info)
    # mcp_call_tool(tool_name="hello", arguments={"name": "World"})