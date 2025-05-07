"""Tests for MCP integration"""

import asyncio
import os
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from tools.mcp_autogen_bridge import MCPAutogenBridge
from tools.mcp_client import MCPClientManager, MCPServerConfig


class TestMCPIntegration:
    """Test MCP client and bridge functionality"""

    @pytest.fixture
    async def mcp_client(self):
        """Create an MCP client for testing"""
        client = MCPClientManager()
        await client.start()
        yield client
        await client.stop()

    @pytest.fixture
    def filesystem_server_path(self):
        """Get the path to the filesystem server script"""
        return str(
            Path(__file__).parent.parent / "mcp_servers" / "filesystem_server.py"
        )

    @pytest.mark.asyncio
    async def test_mcp_client_start_stop(self, mcp_client):
        """Test starting and stopping the MCP client"""
        assert mcp_client.running

        # Stop and start again
        await mcp_client.stop()
        assert not mcp_client.running

        await mcp_client.start()
        assert mcp_client.running

    @pytest.mark.asyncio
    async def test_connect_to_filesystem_server(
        self, mcp_client, filesystem_server_path
    ):
        """Test connecting to the filesystem MCP server"""
        config = MCPServerConfig(
            name="test_filesystem",
            type="stdio",
            script_path=filesystem_server_path,
            description="Test filesystem server",
        )

        success = await mcp_client.connect_to_server(config)
        assert success

        # Check that the server is connected
        connected_servers = mcp_client.get_connected_servers()
        assert len(connected_servers) == 1
        assert connected_servers[0].name == "test_filesystem"

    @pytest.mark.asyncio
    async def test_list_tools(self, mcp_client, filesystem_server_path):
        """Test listing tools from connected server"""
        config = MCPServerConfig(
            name="test_filesystem", type="stdio", script_path=filesystem_server_path
        )

        await mcp_client.connect_to_server(config)

        # List available tools
        tools = await mcp_client.list_available_tools()
        assert len(tools) > 0

        # Check that expected tools are present
        tool_names = [tool.name for tool in tools]
        assert "read_file" in tool_names
        assert "write_file" in tool_names
        assert "list_directory" in tool_names

    @pytest.mark.asyncio
    async def test_execute_tool(self, mcp_client, filesystem_server_path, tmp_path):
        """Test executing a tool"""
        config = MCPServerConfig(
            name="test_filesystem", type="stdio", script_path=filesystem_server_path
        )

        await mcp_client.connect_to_server(config)

        # Test file creation
        test_file = tmp_path / "test.txt"
        test_content = "Hello, MCP!"

        result = await mcp_client.execute_tool(
            "test_filesystem.write_file",
            {"path": str(test_file), "content": test_content},
        )

        assert "Successfully wrote" in result
        assert test_file.exists()

        # Test file reading
        result = await mcp_client.execute_tool(
            "test_filesystem.read_file", {"path": str(test_file)}
        )

        assert result == test_content

    @pytest.mark.asyncio
    async def test_mcp_autogen_bridge(self, mcp_client, filesystem_server_path):
        """Test the MCP-AutoGen bridge"""
        config = MCPServerConfig(
            name="test_filesystem", type="stdio", script_path=filesystem_server_path
        )

        await mcp_client.connect_to_server(config)

        # Create the bridge
        bridge = MCPAutogenBridge(mcp_client)

        # Get AutoGen tools
        tools = bridge.get_autogen_tools()
        assert len(tools) > 0

        # Test tool execution through bridge
        result = await bridge.test_tool_execution("get_current_directory", {})

        assert isinstance(result, str)
        assert result  # Should return a valid directory path

    @pytest.mark.asyncio
    async def test_disconnect_server(self, mcp_client, filesystem_server_path):
        """Test disconnecting from a server"""
        config = MCPServerConfig(
            name="test_filesystem", type="stdio", script_path=filesystem_server_path
        )

        await mcp_client.connect_to_server(config)

        # Disconnect
        success = await mcp_client.disconnect_from_server("test_filesystem")
        assert success

        # Check that the server is no longer connected
        connected_servers = mcp_client.get_connected_servers()
        assert len(connected_servers) == 0

        # Check that tools are also removed
        tools = await mcp_client.list_available_tools()
        assert len(tools) == 0


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
