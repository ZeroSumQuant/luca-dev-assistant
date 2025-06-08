"""Tests to improve coverage for MCP AutoGen bridge."""

import asyncio
import os
import sys
import unittest.mock as mock

import pytest

from tools.mcp_autogen_bridge import MCPAutogenBridge

# Production-grade fix: Ensure consistent event loop policy
if sys.platform.startswith("linux") and os.environ.get("CI"):
    # GitHub Actions runs on Linux and might have different default policy
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())


class TestMCPBridgeCoverage:
    """Test MCP bridge edge cases for coverage."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(5)
    async def test_bridge_tool_wrapper_string_result(self):
        """Test that string results are returned as-is - Integration test."""
        # Create bridge with mock client
        mock_client = mock.MagicMock()
        mock_tool = mock.Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "Test tool"
        mock_tool.parameters = []

        mock_client.tools = {"test_tool": mock_tool}

        bridge = MCPAutogenBridge(mock_client)

        # Mock execute_tool to return a string
        async def mock_execute_tool(tool_name, kwargs):
            # Simulate some async work
            await asyncio.sleep(0)
            return "string result"

        mock_client.execute_tool = mock_execute_tool

        # Get autogen tools
        tools = bridge.get_autogen_tools()
        assert len(tools) > 0

        # Get the wrapped function from autogen FunctionTool
        wrapped_func = tools[0]._func

        # Call with test arguments - this covers line 50
        result = await wrapped_func(arg1="value1")

        # Verify string result is returned as-is
        assert result == "string result"

    @mock.patch("tools.mcp_autogen_bridge.FunctionTool")
    def test_bridge_creates_function_tools(self, mock_function_tool_class):
        """Test that bridge creates FunctionTool objects correctly."""
        # Mock the FunctionTool class itself
        mock_function_tool_instance = mock.Mock()
        mock_function_tool_instance.name = "test_tool"
        mock_function_tool_instance.description = "Test tool"
        mock_function_tool_class.return_value = mock_function_tool_instance

        # Create bridge with mock client
        mock_client = mock.MagicMock()
        mock_tool = mock.Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "Test tool"
        mock_tool.parameters = []

        mock_client.tools = {"test_tool": mock_tool}

        bridge = MCPAutogenBridge(mock_client)

        # Get autogen tools
        tools = bridge.get_autogen_tools()

        # Verify FunctionTool was created with correct arguments
        assert len(tools) == 1
        assert tools[0] == mock_function_tool_instance
        mock_function_tool_class.assert_called_once()

        # Verify the function passed to FunctionTool
        call_args = mock_function_tool_class.call_args
        assert call_args[1]["name"] == "test_tool"
        assert call_args[1]["description"] == "Test tool"

    def test_get_tools_for_server_coverage(self):
        """Test getting tools for a specific server to improve coverage."""
        # Create mock client with tools from different servers
        mock_client = mock.MagicMock()

        # Tool from server1
        tool1 = mock.Mock()
        tool1.name = "tool1"
        tool1.description = "Tool 1"
        tool1.parameters = []
        tool1.server_name = "server1"

        # Tool from server2
        tool2 = mock.Mock()
        tool2.name = "tool2"
        tool2.description = "Tool 2"
        tool2.parameters = []
        tool2.server_name = "server2"

        mock_client.tools = {"tool1": tool1, "tool2": tool2}

        bridge = MCPAutogenBridge(mock_client)

        # Test getting tools for server1 - covers the branch at line 93-98
        server1_tools = bridge.get_tools_for_server("server1")
        assert len(server1_tools) == 1
        assert server1_tools[0].name == "tool1"

    @pytest.mark.asyncio
    @pytest.mark.timeout(5)
    async def test_tool_execution_method(self):
        """Test the test_tool_execution method for coverage."""
        # Create bridge with mock client
        mock_client = mock.MagicMock()
        mock_tool = mock.Mock()
        mock_tool.name = "test_tool"

        mock_client.tools = {"full_test_tool": mock_tool}

        # Use a real async function instead of AsyncMock
        async def mock_execute_tool(tool_name, kwargs):
            await asyncio.sleep(0)  # Yield control
            return {"result": "success"}

        mock_client.execute_tool = mock_execute_tool

        bridge = MCPAutogenBridge(mock_client)

        # Test successful execution - covers lines 120-134
        result = await bridge.test_tool_execution("test_tool", {"arg": "value"})
        assert result == {"result": "success"}

        # Test with non-existent tool
        with pytest.raises(ValueError, match="Tool not found: nonexistent"):
            await bridge.test_tool_execution("nonexistent", {})
