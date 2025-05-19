"""Tests to improve coverage for MCP AutoGen bridge."""

import json
import unittest.mock as mock

import pytest

from tools.mcp_autogen_bridge import MCPAutogenBridge


class TestMCPBridgeCoverage:
    """Test MCP bridge edge cases for coverage."""

    @pytest.mark.asyncio
    async def test_bridge_tool_wrapper_string_result(self):
        """Test that string results are returned as-is."""
        # Create bridge with mock client
        mock_client = mock.MagicMock()
        mock_tool = mock.Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "Test tool"
        mock_tool.parameters = []

        mock_client.tools = {"test_tool": mock_tool}

        bridge = MCPAutogenBridge(mock_client)

        # Mock execute_tool to return a string
        mock_client.execute_tool = mock.AsyncMock(return_value="string result")

        # Get autogen tools
        tools = bridge.get_autogen_tools()
        assert len(tools) > 0

        # Get the wrapped function from autogen FunctionTool
        wrapped_func = tools[0]._func

        # Call with test arguments - this covers line 50
        result = await wrapped_func(arg1="value1")

        # Verify string result is returned as-is
        assert result == "string result"
