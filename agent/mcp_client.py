import os

from dotenv import load_dotenv
from fastmcp import Client
from loguru import logger
import asyncio
import websockets
import json

load_dotenv()

caption_mcp_server_url = os.getenv("CAPTION_MCP_SERVER_URL")
config = {
    "mcpServers": {
        "caption": {
            "url": f"{caption_mcp_server_url}",
            "transport": "streamable-http"
        }
    },
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


async def mcp_call_tool(tool_name=None, arguments=None):
    try:
        async with client:
            logger.info(f"客户端已连接: {client.is_connected()}")
            tools = await client.list_tools()
            if any(tool.name == tool_name for tool in tools):
                print(f"调用工具: {tool_name}")
                result = await client.call_tool(name=tool_name, arguments=arguments)
                if result:
                    content = result[0].text
                    logger.info("调用结果文本内容：{}", content)
                    return content
                logger.warning("MCP 工具调用返回空结果")
                return ""
    except Exception as e:
        logger.error(f"MCP 调用失败: {e}", exc_info=True)
        raise

async def fancy_feast_mcp_server(payload):
    uri = os.getenv("FAMCY_MS_MCP_SERVER_URL")
    try:
        async with websockets.connect(uri) as ws:
            print("已连接到MCP服务器")
            await ws.send(json.dumps(payload))
            response = await ws.recv()
            print("来自服务器的响应:")
            print(json.dumps(json.loads(response), indent=2, ensure_ascii=False))
            return json.loads(response)
    except Exception as e:
        print(f"WebSocket错误: {e}")


async def comfyui_mcp_server(payload):
    uri = os.getenv("COMFYUI_MS_MCP_SERVER_URL")
    try:
        async with websockets.connect(uri) as ws:
            print("已连接到MCP服务器")
            await ws.send(json.dumps(payload))
            response = await ws.recv()
            print("来自服务器的响应:")
            print(json.dumps(json.loads(response), indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"WebSocket错误: {e}")


if __name__ == "__main__":
    tools_info = mcp_get_tools()
    payload = {
        "tool": "generate_image_to_video",
        "params": json.dumps({
            "prompt": "an english mastiff dog sitting on a large boulder, bright shiny day",
            "image_path": "../../example/2 (1).jpg",
            "workflow_id": "hy_image_to_video_api"
        })
    }
    asyncio.run(comfyui_mcp_server(payload))
    print(tools_info)
    # mcp_call_tool(tool_name="hello", arguments={"name": "World"})
