"""Tests for the MCP client."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from tools.mcp_client import (
    MCPClientManager,
    MCPServerConfig,
    MCPTool,
)


class TestMCPTool:
    """Test the MCPTool class."""

    def test_init(self):
        """Test MCPTool initialization."""
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            server_name="test_server",
            schema={"type": "object"},
        )

        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.server_name == "test_server"
        assert tool.schema == {"type": "object"}


class TestMCPServerConfig:
    """Test the MCPServerConfig class."""

    def test_init_stdio(self):
        """Test MCPServerConfig initialization for stdio type."""
        config = MCPServerConfig(
            name="test_server",
            type="stdio",
            script_path="/path/to/script.py",
        )

        assert config.name == "test_server"
        assert config.type == "stdio"
        assert config.script_path == "/path/to/script.py"
        assert config.url is None
        assert config.description is None
        assert config.timeout_seconds == 30
        assert config.max_retries == 3
        assert config.retry_delay_seconds == 1

    def test_init_http(self):
        """Test MCPServerConfig initialization for http type."""
        config = MCPServerConfig(
            name="test_server",
            type="http",
            url="http://localhost:8080",
            description="Test HTTP server",
        )

        assert config.name == "test_server"
        assert config.type == "http"
        assert config.url == "http://localhost:8080"
        assert config.script_path is None
        assert config.description == "Test HTTP server"


class TestMCPClientManager:
    """Test the MCPClientManager class."""

    def test_init(self):
        """Test MCPClientManager initialization."""
        manager = MCPClientManager()

        assert manager.connections == {}
        assert manager.server_configs == {}
        assert manager.tools == {}
        assert manager.running is False

    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test start and stop methods."""
        manager = MCPClientManager()

        await manager.start()
        assert manager.running is True

        await manager.stop()
        assert manager.running is False
        assert manager.connections == {}
        assert manager.tools == {}

    @pytest.mark.asyncio
    async def test_connect_to_server_stdio(self):
        """Test connecting to a stdio server."""
        manager = MCPClientManager()
        config = MCPServerConfig(
            name="test_server",
            type="stdio",
            script_path="/path/to/script.py",
        )

        with patch(
            "tools.mcp_client.stdio_client", new_callable=AsyncMock
        ) as mock_client:
            # Create a properly mocked session
            mock_session = MagicMock()
            mock_session.call = AsyncMock()

            # Mock tool listing
            mock_response = Mock()
            mock_response.tools = []
            mock_session.call.return_value = mock_response

            # Make stdio_client return the mock session
            mock_client.return_value = mock_session

            # Mock the validate_file_path function
            with patch("tools.mcp_client.validate_file_path") as mock_validate:
                mock_validate.return_value = Path("/path/to/script.py")

                result = await manager.connect_to_server(config)

                assert result is True
                assert "test_server" in manager.connections
                assert mock_client.called

    @pytest.mark.asyncio
    async def test_connect_to_server_stdio_no_path(self):
        """Test connecting to stdio server without script path."""
        manager = MCPClientManager()
        config = MCPServerConfig(
            name="test_server",
            type="stdio",
        )

        result = await manager.connect_to_server(config)
        assert result is False

    @pytest.mark.asyncio
    async def test_connect_to_server_http(self):
        """Test connecting to an HTTP server."""
        manager = MCPClientManager()
        config = MCPServerConfig(
            name="test_server",
            type="http",
            url="http://localhost:8080",
        )

        with patch(
            "tools.mcp_client.streamablehttp_client", new_callable=AsyncMock
        ) as mock_client:
            # Create a properly mocked session
            mock_session = MagicMock()
            mock_session.call = AsyncMock()

            # Mock tool listing
            mock_response = Mock()
            mock_response.tools = []
            mock_session.call.return_value = mock_response

            # Make streamablehttp_client return the mock session
            mock_client.return_value = mock_session

            result = await manager.connect_to_server(config)

            assert result is True
            assert "test_server" in manager.connections
            assert mock_client.called

    @pytest.mark.asyncio
    async def test_connect_to_server_http_no_url(self):
        """Test connecting to HTTP server without URL."""
        manager = MCPClientManager()
        config = MCPServerConfig(
            name="test_server",
            type="http",
        )

        result = await manager.connect_to_server(config)
        assert result is False

    @pytest.mark.asyncio
    async def test_connect_to_server_unknown_type(self):
        """Test connecting to server with unknown type."""
        manager = MCPClientManager()
        config = MCPServerConfig(
            name="test_server",
            type="unknown",
        )

        result = await manager.connect_to_server(config)
        assert result is False

    @pytest.mark.asyncio
    async def test_disconnect_from_server(self):
        """Test disconnecting from a server."""
        manager = MCPClientManager()

        # Setup mock connection
        mock_session = AsyncMock()
        manager.connections["test_server"] = mock_session
        manager.server_configs["test_server"] = MCPServerConfig(
            name="test_server", type="stdio"
        )

        # Add a tool
        manager.tools["test_server.tool1"] = MCPTool(
            name="tool1",
            description="Tool 1",
            server_name="test_server",
            schema={},
        )

        result = await manager.disconnect_from_server("test_server")

        assert result is True
        assert "test_server" not in manager.connections
        assert "test_server" not in manager.server_configs
        assert "test_server.tool1" not in manager.tools
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_from_nonexistent_server(self):
        """Test disconnecting from a nonexistent server."""
        manager = MCPClientManager()

        result = await manager.disconnect_from_server("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_register_server_tools(self):
        """Test registering tools from a server."""
        manager = MCPClientManager()

        # Setup mock connection
        mock_session = AsyncMock()
        manager.connections["test_server"] = mock_session

        # Mock tool response
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "Test tool"
        mock_tool.inputSchema = Mock()
        mock_tool.inputSchema.model_dump.return_value = {"type": "object"}

        mock_response = Mock()
        mock_response.tools = [mock_tool]
        mock_session.call.return_value = mock_response

        await manager._register_server_tools("test_server")

        assert "test_server.test_tool" in manager.tools
        tool = manager.tools["test_server.test_tool"]
        assert tool.name == "test_tool"
        assert tool.description == "Test tool"
        assert tool.server_name == "test_server"
        assert tool.schema == {"type": "object"}

    @pytest.mark.asyncio
    async def test_list_available_tools(self):
        """Test listing available tools."""
        manager = MCPClientManager()

        # Add tools
        tool1 = MCPTool(
            name="tool1",
            description="Tool 1",
            server_name="server1",
            schema={},
        )
        tool2 = MCPTool(
            name="tool2",
            description="Tool 2",
            server_name="server2",
            schema={},
        )

        manager.tools = {
            "server1.tool1": tool1,
            "server2.tool2": tool2,
        }

        tools = await manager.list_available_tools()

        assert len(tools) == 2
        assert tool1 in tools
        assert tool2 in tools

    @pytest.mark.asyncio
    async def test_execute_tool(self):
        """Test executing a tool."""
        manager = MCPClientManager()

        # Setup mock connection
        mock_session = AsyncMock()
        manager.connections["test_server"] = mock_session

        # Register the tool
        tool = MCPTool(
            name="test_tool",
            description="Test tool",
            server_name="test_server",
            schema={"type": "object"},
        )
        manager.tools["test_server.test_tool"] = tool

        # Mock tool execution response
        mock_content = Mock()
        mock_content.type = "text"
        mock_content.text = "Success"
        mock_response = Mock()
        mock_response.content = [mock_content]

        # Mock the call method to return expected structure
        async def mock_call(request):
            # Ensure request has the right structure
            if hasattr(request, "method"):
                assert request.method == "tools/call"
            return mock_response

        mock_session.call = mock_call

        result = await manager.execute_tool("test_server.test_tool", {"arg": "value"})

        assert result == "Success"

    @pytest.mark.asyncio
    async def test_execute_tool_not_found(self):
        """Test executing a non-existent tool."""
        manager = MCPClientManager()

        with pytest.raises(ValueError, match="Tool not found: nonexistent"):
            await manager.execute_tool("nonexistent", {})

    @pytest.mark.asyncio
    async def test_execute_tool_no_connection(self):
        """Test executing a tool when server is not connected."""
        manager = MCPClientManager()

        # Register tool but no connection
        tool = MCPTool(
            name="test_tool",
            description="Test tool",
            server_name="test_server",
            schema=None,
        )
        manager.tools["test_server.test_tool"] = tool

        with pytest.raises(ValueError, match="Server not connected: test_server"):
            await manager.execute_tool("test_server.test_tool", {})

    @pytest.mark.asyncio
    async def test_execute_tool_with_empty_content(self):
        """Test executing a tool that returns empty content."""
        manager = MCPClientManager()

        # Setup mock connection
        mock_session = AsyncMock()
        manager.connections["test_server"] = mock_session

        # Register the tool
        tool = MCPTool(
            name="test_tool",
            description="Test tool",
            server_name="test_server",
            schema=None,
        )
        manager.tools["test_server.test_tool"] = tool

        # Mock empty response
        mock_response = Mock()
        mock_response.content = []

        # Mock the call method
        async def mock_call(request):
            return mock_response

        mock_session.call = mock_call

        result = await manager.execute_tool("test_server.test_tool", {})

        assert result is None

    @pytest.mark.asyncio
    async def test_disconnect_exception_handling(self):
        """Test disconnect exception handling."""
        manager = MCPClientManager()

        # Setup mock connection that raises exception on close
        mock_session = AsyncMock()
        mock_session.close.side_effect = Exception("Close failed")

        manager.connections["test_server"] = mock_session
        manager.server_configs["test_server"] = MCPServerConfig(
            name="test_server", type="stdio"
        )

        result = await manager.disconnect_from_server("test_server")
        assert result is False

    @pytest.mark.asyncio
    async def test_register_server_tools_exception(self):
        """Test registering tools exception handling."""
        manager = MCPClientManager()

        # Setup mock connection that raises exception
        mock_session = AsyncMock()
        mock_session.call.side_effect = Exception("Registration failed")

        manager.connections["test_server"] = mock_session

        # Should catch exception without raising
        await manager._register_server_tools("test_server")

        # No tools should be registered
        assert "test_server.tool" not in manager.tools

    @pytest.mark.asyncio
    async def test_register_server_tools_no_session(self):
        """Test registering tools with no session."""
        manager = MCPClientManager()

        # Call without a connection
        await manager._register_server_tools("nonexistent")

        # Should return without error
        assert "nonexistent.tool" not in manager.tools

    @pytest.mark.asyncio
    async def test_get_connected_servers(self):
        """Test getting connected servers."""
        manager = MCPClientManager()

        # Add some server configs
        config1 = MCPServerConfig(name="server1", type="stdio")
        config2 = MCPServerConfig(name="server2", type="http", url="http://example.com")

        manager.server_configs["server1"] = config1
        manager.server_configs["server2"] = config2

        servers = manager.get_connected_servers()

        assert len(servers) == 2
        assert config1 in servers
        assert config2 in servers

    @pytest.mark.asyncio
    async def test_get_server_tools(self):
        """Test getting tools for a specific server."""
        manager = MCPClientManager()

        # Add tools for different servers
        tool1 = MCPTool(
            name="tool1", description="Tool 1", server_name="server1", schema={}
        )
        tool2 = MCPTool(
            name="tool2", description="Tool 2", server_name="server1", schema={}
        )
        tool3 = MCPTool(
            name="tool3", description="Tool 3", server_name="server2", schema={}
        )

        manager.tools = {
            "server1.tool1": tool1,
            "server1.tool2": tool2,
            "server2.tool3": tool3,
        }

        server1_tools = manager.get_server_tools("server1")

        assert len(server1_tools) == 2
        assert tool1 in server1_tools
        assert tool2 in server1_tools
        assert tool3 not in server1_tools

    @pytest.mark.asyncio
    async def test_http_connection_final_failure(self):
        """Test HTTP connection failing after all retries."""
        manager = MCPClientManager()
        config = MCPServerConfig(
            name="test_server",
            type="http",
            url="http://localhost:8080",
            max_retries=3,
            retry_delay_seconds=0.01,
        )

        with patch("tools.mcp_client.streamablehttp_client") as mock_client:
            # Make all attempts fail
            mock_client.side_effect = Exception("Connection failed")

            result = await manager.connect_to_server(config)

            assert result is False
            assert mock_client.call_count == 3


# Additional edge case tests
@pytest.mark.asyncio
async def test_mcp_client_exception_handling():
    """Test exception handling in MCP client methods."""
    manager = MCPClientManager()

    # Test connection exception
    config = MCPServerConfig(
        name="test_server",
        type="stdio",
        script_path="/path/to/script.py",
    )

    with patch("tools.mcp_client.stdio_client") as mock_client:
        mock_client.side_effect = Exception("Connection failed")

        result = await manager.connect_to_server(config)
        assert result is False

    # Test tool execution with validation error
    mock_session = AsyncMock()
    manager.connections["test_server"] = mock_session
    manager.tools["test_server.test_tool"] = MCPTool(
        name="test_tool",
        description="Test tool",
        server_name="test_server",
        schema=None,
    )

    # Mock to raise an exception on tool execution
    async def mock_call_with_error(request):
        raise Exception("Tool execution failed")

    mock_session.call = mock_call_with_error

    with pytest.raises(Exception, match="Tool execution failed"):
        await manager.execute_tool("test_server.test_tool", {})


@pytest.mark.asyncio
async def test_mcp_retry_logic():
    """Test retry logic for HTTP connections."""
    manager = MCPClientManager()
    config = MCPServerConfig(
        name="retry_server",
        type="http",
        url="http://localhost:8080",
        max_retries=3,
        retry_delay_seconds=0.01,  # Very short for testing
    )

    with patch(
        "tools.mcp_client.streamablehttp_client", new_callable=AsyncMock
    ) as mock_client:
        # Make it fail twice then succeed
        attempts = 0

        def side_effect(*args, **kwargs):
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise Exception(f"Attempt {attempts} failed")
            # Return a properly mocked session after retries
            mock_session = MagicMock()
            mock_session.call = AsyncMock()
            # Mock empty tools response
            mock_response = Mock()
            mock_response.tools = []
            mock_session.call.return_value = mock_response
            return mock_session

        mock_client.side_effect = side_effect

        result = await manager.connect_to_server(config)

        # Should succeed after retries
        assert result is True
        assert attempts == 3


@pytest.mark.asyncio
async def test_stop_with_multiple_connections():
    """Test stopping manager with multiple connections."""
    manager = MCPClientManager()
    manager.running = True

    # Add multiple mock connections
    mock_sessions = [AsyncMock() for _ in range(3)]
    manager.connections = {
        f"server{i}": session for i, session in enumerate(mock_sessions)
    }

    await manager.stop()

    assert manager.running is False
    assert manager.connections == {}

    # All sessions should be closed
    for session in mock_sessions:
        session.close.assert_called_once()
