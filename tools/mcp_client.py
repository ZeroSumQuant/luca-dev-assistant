"""MCP Client Manager for LUCA Dev Assistant"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypeVar, Union

from mcp import ClientSession, types
from mcp.client.stdio import StdioServerParameters, stdio_client

logger = logging.getLogger(__name__)

# Type aliases
T = TypeVar("T")
ToolResult = Optional[Union[str, Dict[str, Any], List[Any]]]


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server connection"""

    name: str
    type: str  # "stdio" or "http"
    script_path: Optional[str] = None  # For stdio servers
    url: Optional[str] = None  # For HTTP servers
    description: Optional[str] = None


@dataclass
class MCPTool:
    """Represents an MCP tool"""

    name: str
    description: str
    server_name: str
    schema: Dict[str, Any]


class MCPClientManager:
    """Manages connections to MCP servers and tool execution"""

    def __init__(self) -> None:
        """Initialize the MCP client manager with empty connections and tools."""
        self.connections: Dict[str, ClientSession] = {}
        self.server_configs: Dict[str, MCPServerConfig] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.running: bool = False

    async def start(self) -> None:
        """
        Start the MCP client manager.

        Sets the running flag to True and logs the startup event.
        """
        self.running = True
        logger.info("MCP Client Manager started")

    async def stop(self) -> None:
        """
        Stop the MCP client manager and close all connections.

        Closes all active sessions, clears internal state, and logs the shutdown event.
        """
        self.running = False
        for session in self.connections.values():
            await session.close()
        self.connections.clear()
        self.tools.clear()
        logger.info("MCP Client Manager stopped")

    async def connect_to_server(self, config: MCPServerConfig) -> bool:
        """
        Connect to an MCP server.

        Args:
            config: The server configuration to use for the connection

        Returns:
            True if connection was successful, False otherwise

        Raises:
            ValueError: If required configuration is missing or an unknown server type is specified
            NotImplementedError: For server types that are not yet implemented
        """
        try:
            if config.type == "stdio":
                if not config.script_path:
                    raise ValueError("script_path required for stdio servers")

                # Create server parameters for stdio connection
                server_params = StdioServerParameters(
                    command="python", args=[config.script_path]
                )

                # Connect to the server
                session = await stdio_client(server_params)

            elif config.type == "http":
                # TODO: Implement HTTP connection
                raise NotImplementedError(
                    "HTTP connections not yet implemented"
                )
            else:
                raise ValueError(f"Unknown server type: {config.type}")

            # Store the connection
            self.connections[config.name] = session
            self.server_configs[config.name] = config

            # Fetch and register tools from this server
            await self._register_server_tools(config.name)

            logger.info(f"Connected to MCP server: {config.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to server {config.name}: {e}")
            return False

    async def disconnect_from_server(self, server_name: str) -> bool:
        """
        Disconnect from an MCP server.

        Args:
            server_name: The name of the server to disconnect from

        Returns:
            True if disconnection was successful, False if the server wasn't connected

        Raises:
            Exception: Any exception that occurs during disconnection will be logged and re-raised
        """
        try:
            if server_name in self.connections:
                await self.connections[server_name].close()
                del self.connections[server_name]
                del self.server_configs[server_name]

                # Remove tools from this server
                tools_to_remove = [
                    name
                    for name, tool in self.tools.items()
                    if tool.server_name == server_name
                ]
                for tool_name in tools_to_remove:
                    del self.tools[tool_name]

                logger.info(f"Disconnected from MCP server: {server_name}")
                return True
            return False

        except Exception as e:
            logger.error(
                f"Failed to disconnect from server {server_name}: {e}"
            )
            return False

    async def _register_server_tools(self, server_name: str) -> None:
        """
        Register tools from a connected server.

        Args:
            server_name: The name of the server to register tools from

        Raises:
            Exception: Any exception during tool registration will be caught and logged
        """
        session = self.connections.get(server_name)
        if not session:
            return

        try:
            # List tools from the server
            response = await session.call(types.ListToolsRequest())

            # Register each tool
            for tool in response.tools:
                mcp_tool = MCPTool(
                    name=tool.name,
                    description=tool.description or "",
                    server_name=server_name,
                    schema=(
                        tool.inputSchema.model_dump()
                        if tool.inputSchema
                        else {}
                    ),
                )
                self.tools[f"{server_name}.{tool.name}"] = mcp_tool

            logger.info(
                f"Registered {len(response.tools)} tools from {server_name}"
            )

        except Exception as e:
            logger.error(f"Failed to register tools from {server_name}: {e}")

    async def list_available_tools(self) -> List[MCPTool]:
        """
        List all available tools from connected servers.

        Returns:
            A list of all registered MCPTool objects
        """
        return list(self.tools.values())

    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> ToolResult:
        """
        Execute a tool on the appropriate server.

        Args:
            tool_name: The fully qualified name of the tool (server.tool_name)
            arguments: A dictionary of arguments to pass to the tool

        Returns:
            The result of the tool execution, which could be a string, dictionary, list, or None

        Raises:
            ValueError: If the tool or server is not found
            Exception: Any exception during tool execution will be logged and re-raised
        """
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")

        session = self.connections.get(tool.server_name)
        if not session:
            raise ValueError(f"Server not connected: {tool.server_name}")

        try:
            # Extract the actual tool name (remove server prefix)
            actual_tool_name = tool.name

            # Create and send the tool call request
            request = types.CallToolRequest(
                name=actual_tool_name, arguments=arguments
            )

            response = await session.call(request)

            # Extract the result
            if response.content:
                return response.content[0].text if response.content else None
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to execute tool {tool_name}: {e}")
            raise

    def get_connected_servers(self) -> List[MCPServerConfig]:
        """
        Get list of connected servers.

        Returns:
            A list of MCPServerConfig objects for all connected servers
        """
        return list(self.server_configs.values())

    def get_server_tools(self, server_name: str) -> List[MCPTool]:
        """
        Get tools for a specific server.

        Args:
            server_name: The name of the server to get tools for

        Returns:
            A list of MCPTool objects that belong to the specified server
        """
        return [
            tool
            for tool in self.tools.values()
            if tool.server_name == server_name
        ]


# Global MCP client manager instance
mcp_client = MCPClientManager()


async def initialize_default_servers() -> None:
    """
    Initialize default MCP servers if they exist.

    This function will eventually load server configurations from a config file.
    """
    # TODO: Load from config file
    pass


# Example of how to use the client manager
async def example_usage() -> None:
    """
    Example of using the MCP client manager.

    This demonstrates a typical workflow for connecting to a server,
    listing tools, executing a tool, and shutting down.
    """
    # Start the manager
    await mcp_client.start()

    # Connect to a server
    config = MCPServerConfig(
        name="filesystem",
        type="stdio",
        script_path="/path/to/filesystem_server.py",
        description="Access local filesystem",
    )

    await mcp_client.connect_to_server(config)

    # List available tools
    tools = await mcp_client.list_available_tools()
    for tool in tools:
        print(f"Tool: {tool.name} - {tool.description}")

    # Execute a tool
    try:
        result = await mcp_client.execute_tool(
            "filesystem.read_file", {"path": "/path/to/file.txt"}
        )
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

    # Stop the manager
    await mcp_client.stop()


if __name__ == "__main__":
    asyncio.run(example_usage())
