"""Bridge between MCP and AutoGen agents"""

import asyncio
import json
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

from autogen_core.tools import FunctionTool

from .mcp_client import MCPClientManager, MCPTool

logger = logging.getLogger(__name__)

# Type aliases
JsonValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
ToolExecutorReturn = Awaitable[str]
ToolExecutor = Callable[..., ToolExecutorReturn]


class MCPAutogenBridge:
    """Bridge that allows AutoGen agents to use MCP tools"""

    def __init__(self, mcp_client: MCPClientManager):
        """
        Initialize the bridge between MCP and AutoGen.

        Args:
            mcp_client: An initialized MCP client manager instance
        """
        self.mcp_client = mcp_client

    def get_autogen_tools(self) -> List[FunctionTool]:
        """
        Get all MCP tools as AutoGen FunctionTools.

        Returns:
            A list of AutoGen FunctionTool objects representing all available MCP tools
        """
        tools: List[FunctionTool] = []

        for tool_name, mcp_tool in self.mcp_client.tools.items():
            # Create a function that will execute the MCP tool
            def create_executor(tool_key: str) -> ToolExecutor:
                async def executor(**kwargs: Any) -> str:
                    try:
                        # Execute the MCP tool
                        result = await self.mcp_client.execute_tool(tool_key, kwargs)
                        # Convert result to string if it's not already
                        if isinstance(result, str):
                            return result
                        else:
                            return json.dumps(result, indent=2)
                    except Exception as e:  # pragma: no cover
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
        """
        Get AutoGen tools for a specific MCP server.

        Args:
            server_name: The name of the MCP server to get tools for

        Returns:
            A list of AutoGen FunctionTool objects for the specified server
        """
        all_tools = self.get_autogen_tools()
        server_tools: List[FunctionTool] = []

        for tool in all_tools:
            # Find the corresponding MCP tool
            mcp_tool: Optional[MCPTool] = None
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
        """
        Test execution of an MCP tool.

        Args:
            tool_name: The name of the tool to execute
            arguments: A dictionary of arguments to pass to the tool

        Returns:
            The result of executing the tool

        Raises:
            ValueError: If the tool is not found
        """
        # Find the MCP tool
        mcp_tool: Optional[MCPTool] = None
        full_tool_name: Optional[str] = None

        for name, tool in self.mcp_client.tools.items():
            if tool.name == tool_name:
                mcp_tool = tool
                full_tool_name = name
                break

        if not mcp_tool or not full_tool_name:
            raise ValueError(f"Tool not found: {tool_name}")

        # Execute the tool
        result = await self.mcp_client.execute_tool(full_tool_name, arguments)
        return result


async def example_bridge_usage() -> None:  # pragma: no cover
    """
    Example of using the MCP-AutoGen bridge.

    This demonstrates how to set up and use the bridge between MCP and AutoGen.
    """
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


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(example_bridge_usage())
