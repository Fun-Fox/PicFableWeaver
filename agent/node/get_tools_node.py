from pocketflow import Node

from agent.utils.mcp_client import mcp_get_tools


class GetToolsNode(Node):
    def prep(self, shared):
        """Initialize and get tools"""
        print("🔍 Getting available tools...")
        return

    def exec(self):
        """Retrieve tools from the MCP server"""
        tools = mcp_get_tools()
        return tools

    def post(self, shared, prep_res, exec_res):
        """Store tools and process to decision node"""
        tools = exec_res
        shared["tools"] = tools

        # Format tool information for later use
        tool_info = []
        for i, tool in enumerate(tools, 1):
            properties = tool.inputSchema.get('properties', {})
            required = tool.inputSchema.get('required', [])

            params = []
            for param_name, param_info in properties.items():
                param_type = param_info.get('type', 'unknown')
                req_status = "(Required)" if param_name in required else "(Optional)"
                params.append(f"    - {param_name} ({param_type}): {req_status}")

            tool_info.append(
                f"[{i}] {tool.name}\n  Description: {tool.description}\n  Parameters:\n" + "\n".join(params))

        shared["tool_info"] = "\n".join(tool_info)
        return "decide"