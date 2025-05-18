"""Tests for MCP integration"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from autogen_core.tools import FunctionTool
from mcp import types

from tools.mcp_autogen_bridge import MCPAutogenBridge
from tools.mcp_client import MCPClientManager, MCPServerConfig, MCPTool

# Mark all tests in this module for AutoGen mocking
pytestmark = pytest.mark.autogen_mock


# Helper functions for creating valid MCP protocol objects
def make_list_tools_request():
    """Create a valid ListToolsRequest object that will pass validation."""
    mock = MagicMock()
    mock.id = 1
    mock.method = "list_tools"
    mock.params = {}
    return mock


def make_list_tools_response(tools=None):
    """Create a valid response for list_tools with the given tools."""
    if tools is None:
        tools = []
    mock = MagicMock()
    mock.id = 1
    mock.tools = tools
    return mock


def make_call_tool_request(tool_name, arguments=None):
    """Create a valid CallToolRequest object that will pass validation."""
    if arguments is None:
        arguments = {}
    mock = MagicMock()
    mock.id = 1
    mock.method = "call_tool"
    mock.params = {"name": tool_name, "arguments": arguments}
    mock.name = tool_name  # For direct access by the client code
    mock.arguments = arguments  # For direct access by the client code
    return mock


def make_call_tool_response(content_text=None):
    """Create a valid response for call_tool with the given content."""
    mock = MagicMock()
    mock.id = 1

    if content_text is not None:
        content_mock = MagicMock()
        content_mock.text = content_text
        mock.content = [content_mock]
    else:
        mock.content = []

    return mock


# Skip all MCP tests in CI environments where they might hang
pytestmark = [
    pytest.mark.skipif(
        os.environ.get("CI") == "true",
        reason="MCP tests skipped in CI due to subprocess/stdio issues",
    ),
    pytest.mark.asyncio,  # Mark all test functions as asyncio tests
]


@pytest_asyncio.fixture
async def mcp_client():
    """Fixture for an MCP client manager with mocked connections."""
    client = MCPClientManager()
    return client


@pytest_asyncio.fixture
async def mock_session():
    """Fixture for a mocked MCP ClientSession."""
    mock = AsyncMock()
    mock.call = AsyncMock()
    return mock


@pytest_asyncio.fixture
async def mock_stdio_client():
    """Fixture for a mocked stdio client function."""
    # Create a session mock that can be awaited
    session_mock = AsyncMock()

    # Mock the response from listing tools
    tool1 = MagicMock()
    tool1.name = "read_file"
    tool1.description = "Read a file"
    tool1.inputSchema = MagicMock()
    tool1.inputSchema.model_dump.return_value = {
        "properties": {"path": {"type": "string"}}
    }

    tool2 = MagicMock()
    tool2.name = "write_file"
    tool2.description = "Write to a file"
    tool2.inputSchema = MagicMock()
    tool2.inputSchema.model_dump.return_value = {
        "properties": {"path": {"type": "string"}, "content": {"type": "string"}}
    }

    response_mock = MagicMock()
    response_mock.tools = [tool1, tool2]
    session_mock.call = AsyncMock(return_value=response_mock)

    # Create a mock for stdio_client that is an awaitable function that returns the session
    async def mock_stdio_client_func(*args, **kwargs):
        return session_mock

    with patch("tools.mcp_client.stdio_client", mock_stdio_client_func):
        yield mock_stdio_client_func


@pytest_asyncio.fixture
async def mock_http_client():
    """Fixture for a mocked HTTP client function."""
    # Create a session mock that can be awaited
    session_mock = AsyncMock()

    # Mock the response from listing tools
    tool1 = MagicMock()
    tool1.name = "http_tool1"
    tool1.description = "HTTP Tool 1"
    tool1.inputSchema = MagicMock()
    tool1.inputSchema.model_dump.return_value = {
        "properties": {"param": {"type": "string"}}
    }

    response_mock = MagicMock()
    response_mock.tools = [tool1]
    session_mock.call = AsyncMock(return_value=response_mock)

    # Create a mock for http_client that is an awaitable function that returns the session
    async def mock_http_client_func(*args, **kwargs):
        return session_mock

    with patch("tools.mcp_client.streamablehttp_client", mock_http_client_func):
        yield mock_http_client_func


class TestMCPClientManager:
    """Test MCP client and connection functionality"""

    async def test_start_stop(self, mcp_client):
        """Test starting and stopping the MCP client manager"""
        # Start the client manager
        await mcp_client.start()
        assert mcp_client.running is True

        # Stop the client manager
        await mcp_client.stop()
        assert mcp_client.running is False
        assert not mcp_client.connections
        assert not mcp_client.tools

    # Removed duplicate test_get_connected_servers method.
    # The same method is defined later in this file (around line 598)

    # Removed duplicate test_get_server_tools method.
    # The same method is defined later in this file (around line 628)

    async def test_connect_to_stdio_server(self, mcp_client):
        """Test connecting to a stdio server"""
        # Create a session mock
        session_mock = AsyncMock()

        # Create two tools for the response
        tool1 = MagicMock()
        tool1.name = "read_file"
        tool1.description = "Read a file"
        tool1.inputSchema = MagicMock()
        tool1.inputSchema.model_dump.return_value = {
            "properties": {"path": {"type": "string"}}
        }

        tool2 = MagicMock()
        tool2.name = "write_file"
        tool2.description = "Write to a file"
        tool2.inputSchema = MagicMock()
        tool2.inputSchema.model_dump.return_value = {
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}}
        }

        # Create a valid list_tools response
        tools_response = make_list_tools_response([tool1, tool2])

        # Configure the session to return the tools response for call
        async def mock_call(*args, **kwargs):
            return tools_response

        session_mock.call = mock_call

        # Create an awaitable stdio_client mock
        async def mock_stdio_client(*args, **kwargs):
            return session_mock

        # Create a config for stdio server
        config = MCPServerConfig(
            name="test_stdio",
            type="stdio",
            script_path="/path/to/script.py",
            description="Test stdio server",
        )

        # Patch the stdio_client and connect to the server
        with patch("tools.mcp_client.stdio_client", mock_stdio_client):
            # Also patch the ListToolsRequest to return a valid request object
            with patch.object(
                types, "ListToolsRequest", return_value=make_list_tools_request()
            ):
                result = await mcp_client.connect_to_server(config)

        # Verify the result
        assert result is True
        assert "test_stdio" in mcp_client.connections
        assert "test_stdio" in mcp_client.server_configs
        assert len(mcp_client.tools) == 2
        assert "test_stdio.read_file" in mcp_client.tools
        assert "test_stdio.write_file" in mcp_client.tools

        # Verify the tools were registered correctly
        read_tool = mcp_client.tools["test_stdio.read_file"]
        assert read_tool.name == "read_file"
        assert read_tool.description == "Read a file"
        assert read_tool.server_name == "test_stdio"

    async def test_connect_to_stdio_server_missing_script_path(self, mcp_client):
        """Test that connecting to a stdio server fails when script_path is missing"""
        # Create a config for stdio server without script_path
        config = MCPServerConfig(
            name="test_stdio", type="stdio", description="Test stdio server"
        )

        # The connect_to_server method catches exceptions and returns False
        # So we should test for the return value, not the exception
        with patch(
            "tools.mcp_client.stdio_client",
            side_effect=ValueError("script_path required for stdio servers"),
        ):
            result = await mcp_client.connect_to_server(config)

        # Verify the result is False (connection failed)
        assert result is False

        # Verify the connection was not added
        assert "test_stdio" not in mcp_client.connections
        assert len(mcp_client.connections) == 0

    async def test_connect_to_http_server(self, mcp_client):
        """Test connecting to an HTTP server"""
        # Create a session mock
        session_mock = AsyncMock()

        # Create a tool for the response
        tool1 = MagicMock()
        tool1.name = "http_tool1"
        tool1.description = "HTTP Tool 1"
        tool1.inputSchema = MagicMock()
        tool1.inputSchema.model_dump.return_value = {
            "properties": {"param": {"type": "string"}}
        }

        # Create a valid list_tools response
        tools_response = make_list_tools_response([tool1])

        # Configure the session to return the tools response
        async def mock_call(*args, **kwargs):
            return tools_response

        session_mock.call = mock_call

        # Create an awaitable http_client mock
        async def mock_http_client(*args, **kwargs):
            return session_mock

        # Create a config for HTTP server
        config = MCPServerConfig(
            name="test_http",
            type="http",
            url="https://example.com/mcp",
            description="Test HTTP server",
            timeout_seconds=5,
            max_retries=2,
        )

        # Patch the http_client and connect to the server
        with patch("tools.mcp_client.streamablehttp_client", mock_http_client):
            # Also patch the ListToolsRequest to return a valid request object
            with patch.object(
                types, "ListToolsRequest", return_value=make_list_tools_request()
            ):
                result = await mcp_client.connect_to_server(config)

        # Verify the result
        assert result is True
        assert "test_http" in mcp_client.connections
        assert "test_http" in mcp_client.server_configs
        assert len(mcp_client.tools) == 1
        assert "test_http.http_tool1" in mcp_client.tools

        # Verify the tool was registered correctly
        http_tool = mcp_client.tools["test_http.http_tool1"]
        assert http_tool.name == "http_tool1"
        assert http_tool.description == "HTTP Tool 1"
        assert http_tool.server_name == "test_http"

    async def test_connect_to_http_server_missing_url(self, mcp_client):
        """Test that connecting to an HTTP server fails when URL is missing"""
        # Create a config for HTTP server without URL
        config = MCPServerConfig(
            name="test_http", type="http", description="Test HTTP server"
        )

        # The connect_to_server method catches exceptions and returns False
        # So we should test for the return value, not the exception
        with patch(
            "tools.mcp_client.streamablehttp_client",
            side_effect=ValueError("url required for HTTP servers"),
        ):
            result = await mcp_client.connect_to_server(config)

        # Verify the result is False (connection failed)
        assert result is False

        # Verify the connection was not added
        assert "test_http" not in mcp_client.connections
        assert len(mcp_client.connections) == 0

    async def test_connect_to_http_server_with_retry(self, mcp_client):
        """Test HTTP connection with retry logic"""
        # Session mock for successful connection
        success_session_mock = AsyncMock()
        response_mock = MagicMock()
        response_mock.tools = []
        success_session_mock.call = AsyncMock(return_value=response_mock)

        # Create a mock for http client with retry behavior
        retry_count = 0

        async def mock_http_retry(*args, **kwargs):
            nonlocal retry_count
            if retry_count == 0:
                retry_count += 1
                raise RuntimeError("Connection failed")
            else:
                return success_session_mock

        # Create a config for HTTP server with retries
        config = MCPServerConfig(
            name="test_http_retry",
            type="http",
            url="https://example.com/mcp",
            description="Test HTTP server with retry",
            timeout_seconds=1,
            max_retries=2,
            retry_delay_seconds=0.1,  # Short delay for tests
        )

        # Connect to the server
        with patch("tools.mcp_client.streamablehttp_client", mock_http_retry):
            with patch("asyncio.sleep", AsyncMock()) as mock_sleep:
                result = await mcp_client.connect_to_server(config)

        # Verify the result
        assert result is True
        assert "test_http_retry" in mcp_client.connections
        assert mock_sleep.called  # Verify sleep was called for retry

    async def test_connect_to_unknown_server_type(self, mcp_client):
        """Test that connecting to an unknown server type fails"""
        # Create a config with unknown server type
        config = MCPServerConfig(
            name="test_unknown", type="unknown", description="Test unknown server type"
        )

        # For simplicity, directly test the return value
        # The connect_to_server method catches exceptions and returns False
        result = await mcp_client.connect_to_server(config)

        # Verify the result is False (connection failed)
        assert result is False

        # Verify the connection was not added
        assert "test_unknown" not in mcp_client.connections
        assert len(mcp_client.connections) == 0

    async def test_disconnect_from_server(self, mcp_client):
        """Test disconnecting from a server"""
        # Manually add a connection and tools
        session_mock = AsyncMock()

        # Add a connection directly
        mcp_client.connections["test_disconnect"] = session_mock
        mcp_client.server_configs["test_disconnect"] = MCPServerConfig(
            name="test_disconnect",
            type="stdio",
            script_path="/path/to/script.py",
            description="Test disconnect server",
        )

        # Add a tool
        tool = MCPTool(
            name="read_file",
            description="Read a file",
            server_name="test_disconnect",
            schema={},
        )
        mcp_client.tools["test_disconnect.read_file"] = tool

        # Verify connection exists
        assert "test_disconnect" in mcp_client.connections

        # Now disconnect
        result = await mcp_client.disconnect_from_server("test_disconnect")

        # Verify the result
        assert result is True
        assert "test_disconnect" not in mcp_client.connections
        assert "test_disconnect" not in mcp_client.server_configs

        # Verify that tools were removed
        for tool_name in mcp_client.tools:
            assert not tool_name.startswith("test_disconnect.")

    async def test_disconnect_nonexistent_server(self, mcp_client):
        """Test disconnecting from a server that doesn't exist"""
        result = await mcp_client.disconnect_from_server("nonexistent")
        assert result is False

    async def test_list_available_tools(self, mcp_client):
        """Test listing available tools"""
        # Add tools manually to the client manager
        tool1 = MCPTool(
            name="read_file",
            description="Read a file",
            server_name="test_tools",
            schema={"properties": {"path": {"type": "string"}}},
        )

        tool2 = MCPTool(
            name="write_file",
            description="Write to a file",
            server_name="test_tools",
            schema={
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                }
            },
        )

        mcp_client.tools["test_tools.read_file"] = tool1
        mcp_client.tools["test_tools.write_file"] = tool2

        # List tools
        tools = await mcp_client.list_available_tools()

        # Verify the tools
        assert len(tools) == 2
        tool_names = [tool.name for tool in tools]
        assert "read_file" in tool_names
        assert "write_file" in tool_names

    async def test_execute_tool(self, mcp_client):
        """Test executing a tool"""
        # Create a session mock
        session_mock = AsyncMock()

        # Create a response with content
        tool_response = make_call_tool_response("File content goes here")

        # Configure the session to return the tool response - use AsyncMock
        mock_call = AsyncMock(return_value=tool_response)
        session_mock.call = mock_call

        # Manually add tool and connection to the client manager
        tool = MCPTool(
            name="read_file",
            description="Read a file",
            server_name="test_execute",
            schema={"properties": {"path": {"type": "string"}}},
        )

        mcp_client.tools["test_execute.read_file"] = tool
        mcp_client.connections["test_execute"] = session_mock
        mcp_client.server_configs["test_execute"] = MCPServerConfig(
            name="test_execute",
            type="stdio",
            script_path="/path/to/script.py",
            description="Test execute server",
        )

        # Execute a tool with patched CallToolRequest
        with patch.object(
            types,
            "CallToolRequest",
            return_value=make_call_tool_request(
                "read_file", {"path": "/path/to/file.txt"}
            ),
        ):
            result = await mcp_client.execute_tool(
                "test_execute.read_file", {"path": "/path/to/file.txt"}
            )

        # Verify the result
        assert result == "File content goes here"

        # Verify the call was made correctly
        assert mock_call.call_count == 1

    async def test_execute_nonexistent_tool(self, mcp_client):
        """Test executing a tool that doesn't exist"""
        with pytest.raises(ValueError, match="Tool not found"):
            await mcp_client.execute_tool("nonexistent.tool", {})

    async def test_execute_tool_on_disconnected_server(self, mcp_client):
        """Test executing a tool on a disconnected server"""
        # Manually add a tool to the tools dictionary
        tool = MCPTool(
            name="read_file",
            description="Read a file",
            server_name="test_disconnect_exec",
            schema={},
        )

        # Add directly to tools collection
        mcp_client.tools["test_disconnect_exec.read_file"] = tool

        # Try to execute the tool without the corresponding connection
        with pytest.raises(ValueError, match="Server not connected"):
            await mcp_client.execute_tool(
                "test_disconnect_exec.read_file", {"path": "/path/to/file.txt"}
            )

    async def test_get_connected_servers(self, mcp_client):
        """Test getting connected servers"""
        # Add some server configs
        config1 = MCPServerConfig(
            name="server1",
            type="stdio",
            script_path="/path/to/script1.py",
            description="Server 1",
        )

        config2 = MCPServerConfig(
            name="server2",
            type="http",
            url="https://example.com/mcp",
            description="Server 2",
        )

        mcp_client.server_configs["server1"] = config1
        mcp_client.server_configs["server2"] = config2

        # Get connected servers
        servers = mcp_client.get_connected_servers()

        # Verify the servers
        assert len(servers) == 2
        server_names = [server.name for server in servers]
        assert "server1" in server_names
        assert "server2" in server_names

    async def test_get_server_tools(self, mcp_client):
        """Test getting tools for a specific server"""
        # Add some tools
        tool1 = MCPTool(
            name="tool1", description="Tool 1", server_name="server1", schema={}
        )

        tool2 = MCPTool(
            name="tool2", description="Tool 2", server_name="server1", schema={}
        )

        tool3 = MCPTool(
            name="tool3", description="Tool 3", server_name="server2", schema={}
        )

        mcp_client.tools["server1.tool1"] = tool1
        mcp_client.tools["server1.tool2"] = tool2
        mcp_client.tools["server2.tool3"] = tool3

        # Get tools for server1
        tools = mcp_client.get_server_tools("server1")

        # Verify the tools
        assert len(tools) == 2
        tool_names = [tool.name for tool in tools]
        assert "tool1" in tool_names
        assert "tool2" in tool_names
        assert "tool3" not in tool_names


class TestMCPAutogenBridge:
    """Test MCP-AutoGen bridge functionality"""

    async def test_bridge_initialization(self, mcp_client):
        """Test initializing the bridge"""
        bridge = MCPAutogenBridge(mcp_client)
        assert bridge.mcp_client == mcp_client

    async def test_get_autogen_tools(self, mcp_client):
        """Test getting AutoGen tools from MCP tools"""
        # Add some MCP tools
        tool1 = MCPTool(
            name="tool1",
            description="Tool 1",
            server_name="server1",
            schema={"properties": {"param1": {"type": "string"}}},
        )

        tool2 = MCPTool(
            name="tool2",
            description="Tool 2",
            server_name="server1",
            schema={"properties": {"param2": {"type": "number"}}},
        )

        mcp_client.tools["server1.tool1"] = tool1
        mcp_client.tools["server1.tool2"] = tool2

        # Create the bridge and get AutoGen tools
        bridge = MCPAutogenBridge(mcp_client)
        tools = bridge.get_autogen_tools()

        # Verify the tools
        assert len(tools) == 2

        # Verify tools are FunctionTool instances
        for tool in tools:
            assert isinstance(tool, FunctionTool)

        # Verify tool names
        tool_names = [tool.name for tool in tools]
        assert "tool1" in tool_names
        assert "tool2" in tool_names

    async def test_get_tools_for_server(self, mcp_client):
        """Test getting AutoGen tools for a specific server"""
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

        mcp_client.tools["server1.tool1"] = tool1
        mcp_client.tools["server1.tool2"] = tool2
        mcp_client.tools["server2.tool3"] = tool3

        # Create the bridge
        bridge = MCPAutogenBridge(mcp_client)

        # Get tools for server1
        with patch.object(bridge, "get_autogen_tools") as mock_get_tools:
            # Create mock AutoGen tools
            mock_tool1 = MagicMock(spec=FunctionTool)
            mock_tool1.name = "tool1"

            mock_tool2 = MagicMock(spec=FunctionTool)
            mock_tool2.name = "tool2"

            mock_tool3 = MagicMock(spec=FunctionTool)
            mock_tool3.name = "tool3"

            mock_get_tools.return_value = [mock_tool1, mock_tool2, mock_tool3]

            # Get tools for server1
            server1_tools = bridge.get_tools_for_server("server1")

            # Verify the tools
            assert len(server1_tools) == 2
            tool_names = [tool.name for tool in server1_tools]
            assert "tool1" in tool_names
            assert "tool2" in tool_names
            assert "tool3" not in tool_names

    async def test_test_tool_execution(self, mcp_client):
        """Test the test_tool_execution method"""
        # Add a tool
        tool = MCPTool(
            name="test_tool",
            description="Test Tool",
            server_name="test_server",
            schema={},
        )

        mcp_client.tools["test_server.test_tool"] = tool

        # Mock the execute_tool method
        mock_execute = AsyncMock(return_value="Tool execution result")
        mcp_client.execute_tool = mock_execute

        # Create the bridge
        bridge = MCPAutogenBridge(mcp_client)

        # Test tool execution
        result = await bridge.test_tool_execution("test_tool", {"param": "value"})

        # Verify the result
        assert result == "Tool execution result"

        # Verify the execute_tool was called correctly
        mock_execute.assert_awaited_once_with(
            "test_server.test_tool", {"param": "value"}
        )

    async def test_test_tool_execution_not_found(self, mcp_client):
        """Test test_tool_execution with a nonexistent tool"""
        bridge = MCPAutogenBridge(mcp_client)

        # Try to test a nonexistent tool
        with pytest.raises(ValueError, match="Tool not found"):
            await bridge.test_tool_execution("nonexistent", {})

    async def test_create_executor(self, mcp_client):
        """Test the executor function created by create_executor"""
        # Mock a tool in the client
        tool1 = MCPTool(
            name="test_tool",
            description="Test Tool",
            server_name="test_server",
            schema={},
        )
        mcp_client.tools["test_server.test_tool"] = tool1

        # Mock the execute_tool method to return a test result
        mcp_client.execute_tool = AsyncMock(return_value="Test result")

        # Create bridge
        bridge = MCPAutogenBridge(mcp_client)

        # Get the tools
        tools = bridge.get_autogen_tools()

        # Find our test tool
        test_tool = None
        for tool in tools:
            if tool.name == "test_tool":
                test_tool = tool
                break

        assert test_tool is not None

        # Get the executor function from the private _func attribute
        executor_func = getattr(test_tool, "_func")

        # Call the executor function
        result = await executor_func(param1="value1", param2="value2")

        # Verify execute_tool was called correctly
        mcp_client.execute_tool.assert_awaited_once_with(
            "test_server.test_tool", {"param1": "value1", "param2": "value2"}
        )
        assert result == "Test result"

    async def test_executor_error_handling(self, mcp_client):
        """Test error handling in the executor function"""
        # Mock a tool in the client
        tool1 = MCPTool(
            name="error_tool",
            description="Tool that raises an error",
            server_name="test_server",
            schema={},
        )
        mcp_client.tools["test_server.error_tool"] = tool1

        # Mock execute_tool to raise an exception
        error_message = "Boom! Test error"
        mcp_client.execute_tool = AsyncMock(side_effect=ValueError(error_message))

        # Create bridge
        bridge = MCPAutogenBridge(mcp_client)

        # Get the tools
        tools = bridge.get_autogen_tools()

        # Find our error tool
        error_tool = None
        for tool in tools:
            if tool.name == "error_tool":
                error_tool = tool
                break

        assert error_tool is not None

        # Get the executor function
        executor_func = getattr(error_tool, "_func")

        # Call the executor - it should handle the error
        result = await executor_func(param="value")

        # Verify the error was handled properly
        assert f"Error: {error_message}" in result


class TestMCPClientAdvanced:
    """Additional tests for MCPClientManager to improve coverage"""

    async def test_client_empty_tools_list(self):
        """Test listing tools when no tools are available"""
        client = MCPClientManager()
        tools = await client.list_available_tools()
        assert tools == []
        assert isinstance(tools, list)

    async def test_connect_invalid_config(self):
        """Test connecting with invalid config returns False"""
        client = MCPClientManager()

        # Invalid config (missing required fields)
        config = MCPServerConfig(
            name="invalid_server",
            type="unknown_type",
        )

        result = await client.connect_to_server(config)
        assert result is False

    async def test_execute_tool_no_connection(self):
        """Test executing tool without connected server raises ValueError"""
        client = MCPClientManager()

        # Directly add a tool without connection
        tool = MCPTool(
            name="test_tool",
            description="Test tool",
            server_name="no_server",
            schema={},
        )
        client.tools["no_server.test_tool"] = tool

        with pytest.raises(ValueError, match="Server not connected"):
            await client.execute_tool("no_server.test_tool", {"param": "value"})

    async def test_http_connect_success(self):
        """Test successful HTTP connection path"""
        client = MCPClientManager()

        # Create a mock session
        mock_session = AsyncMock()

        # Create a tool for the response
        tool = MagicMock()
        tool.name = "http_tool"
        tool.description = "HTTP Tool"
        tool.inputSchema = MagicMock()
        tool.inputSchema.model_dump.return_value = {
            "properties": {"param": {"type": "string"}}
        }

        # Mock response from list_tools
        mock_response = MagicMock()
        mock_response.tools = [tool]
        mock_session.call = AsyncMock(return_value=mock_response)

        # Create mock for streamablehttp_client
        mock_http_client = AsyncMock(return_value=mock_session)

        # Create a valid HTTP config
        config = MCPServerConfig(
            name="test_http",
            type="http",
            url="https://example.com/mcp",
            description="Test HTTP server",
        )

        # Patch streamablehttp_client and ListToolsRequest
        with patch("tools.mcp_client.streamablehttp_client", mock_http_client):
            with patch.object(
                types, "ListToolsRequest", return_value=make_list_tools_request()
            ):
                result = await client.connect_to_server(config)

        # Verify the connection was successful
        assert result is True
        assert "test_http" in client.connections
        assert "test_http" in client.server_configs
        assert "test_http.http_tool" in client.tools

        # Now test execute_tool with this connection
        tool_request = make_call_tool_request("http_tool", {"param": "value"})
        tool_response = make_call_tool_response("Tool executed successfully")

        # Configure mock session to return tool response
        mock_session.call = AsyncMock(return_value=tool_response)

        # Test executing the tool
        with patch.object(types, "CallToolRequest", return_value=tool_request):
            result = await client.execute_tool(
                "test_http.http_tool", {"param": "value"}
            )

        # Verify the result
        assert result == "Tool executed successfully"
        assert mock_session.call.call_count == 1

    async def test_http_connect_with_retry(self):
        """Test HTTP connection with retry logic"""
        client = MCPClientManager()

        # Create a mock session for success
        mock_session = AsyncMock()
        mock_session.call = AsyncMock(return_value=make_list_tools_response([]))

        # Create a retry function that fails twice then succeeds
        connect_count = 0

        async def mock_connect_with_retry(*args, **kwargs):
            nonlocal connect_count
            connect_count += 1
            if connect_count <= 2:
                raise ConnectionRefusedError("Connection refused")
            return mock_session

        # Create config with retries
        config = MCPServerConfig(
            name="test_http_retry",
            type="http",
            url="https://example.com/mcp",
            description="Test HTTP server with retry",
            max_retries=3,
            retry_delay_seconds=0.1,
        )

        # Patch streamablehttp_client, asyncio.sleep, and ListToolsRequest
        with patch("tools.mcp_client.streamablehttp_client", mock_connect_with_retry):
            with patch("asyncio.sleep", AsyncMock()) as mock_sleep:
                with patch.object(
                    types, "ListToolsRequest", return_value=make_list_tools_request()
                ):
                    result = await client.connect_to_server(config)

        # Verify the connection was successful after retries
        assert result is True
        assert connect_count == 3  # Initial failure + 2 retries before success
        assert (
            mock_sleep.call_count == 2
        )  # Should sleep twice (after first and second failures)
        assert "test_http_retry" in client.connections


# Special integration test that actually runs the filesystem server
@pytest.mark.skipif(
    os.environ.get("RUN_MCP_INTEGRATION") != "1",
    reason="Full integration test requires actual filesystem server and RUN_MCP_INTEGRATION=1",
)
class TestMCPFullIntegration:
    """Full integration test with actual MCP server"""

    async def test_filesystem_server_integration(self, tmp_path):
        """Test integration with the filesystem server"""
        # Import only needed in the test function
        import asyncio  # noqa: needed for async context

        # Path to the filesystem server script
        server_script = str(
            os.path.join(
                os.path.dirname(__file__), "..", "mcp_servers", "filesystem_server.py"
            )
        )

        # Create a temporary file for testing
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("Test content")

        # Initialize the client manager
        client = MCPClientManager()
        await client.start()

        try:
            # Connect to filesystem server
            config = MCPServerConfig(
                name="filesystem",
                type="stdio",
                script_path=server_script,
                description="Filesystem server",
            )

            result = await client.connect_to_server(config)
            assert result is True

            # List tools
            tools = await client.list_available_tools()
            assert len(tools) > 0

            # Find read_file tool
            read_tool_name = None
            for tool_name in client.tools:
                if client.tools[tool_name].name == "read_file":
                    read_tool_name = tool_name
                    break

            assert read_tool_name is not None

            # Execute read_file tool
            result = await client.execute_tool(read_tool_name, {"path": str(test_file)})

            assert result == "Test content"

        finally:
            # Stop the client manager
            await client.stop()
