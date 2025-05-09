"""Bridge between MCP and AutoGen agents"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List

from autogen_core.tools import FunctionTool

from .mcp_client import MCPClientManager, MCPTool

logger = logging.getLogger(__name__)


class MCPAutogenBridge:
    """Bridge that allows AutoGen agents to use MCP tools"""

    def __init__(self, mcp_client: MCPClientManager):
        self.mcp_client = mcp_client

    def get_autogen_tools(self) -> List[FunctionTool]:
        """Get all MCP tools as AutoGen FunctionTools"""
        tools = []

        for tool_name, mcp_tool in self.mcp_client.tools.items():
            # Create a function that will execute the MCP tool
            def create_executor(tool_key: str):
                async def executor(**kwargs) -> str:
                    try:
                        # Execute the MCP tool
                        result = await self.mcp_client.execute_tool(tool_key, kwargs)
                        # Convert result to string if it's not already
                        if isinstance(result, str):
                            return result
                        else:
                            return json.dumps(result, indent=2)
                    except Exception as e:
                        logger.error(f"Error executing MCP tool {tool_key}: {e}")
                        return f"Error: {str(e)}"

                return executor

            # Create the AutoGen function tool
            func = create_executor(tool_name)

            # Add function metadata
            func.__name__ = mcp_tool.name
            func.__doc__ = mcp_tool.description

            # Create the FunctionTool
            tool = FunctionTool(
                func=func,
                name=mcp_tool.name,
                description=mcp_tool.description or "MCP Tool",
            )

            tools.append(tool)

        return tools

    def get_tools_for_server(self, server_name: str) -> List[FunctionTool]:
        """Get AutoGen tools for a specific MCP server"""
        all_tools = self.get_autogen_tools()
        server_tools = []

        for tool in all_tools:
            # Find the corresponding MCP tool
            mcp_tool = None
            for name, tool_obj in self.mcp_client.tools.items():
                if tool_obj.name == tool.name:
                    mcp_tool = tool_obj
                    break

            if mcp_tool and mcp_tool.server_name == server_name:
                server_tools.append(tool)

        return server_tools

    async def test_tool_execution(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Any:
        """Test execution of an MCP tool"""
        # Find the MCP tool
        mcp_tool = None
        for name, tool in self.mcp_client.tools.items():
            if tool.name == tool_name:
                mcp_tool = tool
                break

        if not mcp_tool:
            raise ValueError(f"Tool not found: {tool_name}")

        # Execute the tool
        result = await self.mcp_client.execute_tool(name, arguments)
        return result


async def example_bridge_usage():
    """Example of using the MCP-AutoGen bridge"""
    from .mcp_client import MCPServerConfig, mcp_client

    # Initialize MCP client
    await mcp_client.start()

    # Connect to filesystem server
    config = MCPServerConfig(
        name="filesystem",
        type="stdio",
        script_path="/Users/dustinkirby/dev/luca-dev-assistant/mcp_servers/filesystem_server.py",
    )

    await mcp_client.connect_to_server(config)

    # Create the bridge
    bridge = MCPAutogenBridge(mcp_client)

    # Get AutoGen tools
    tools = bridge.get_autogen_tools()
    for tool in tools:
        print(f"Tool: {tool.name} - {tool.description}")

    # Test tool execution
    try:
        result = await bridge.test_tool_execution("list_directory", {"path": "."})
        print(f"Directory listing:\n{result}")
    except Exception as e:
        print(f"Error: {e}")

    # Stop the MCP client
    await mcp_client.stop()


if __name__ == "__main__":
    asyncio.run(example_bridge_usage())
