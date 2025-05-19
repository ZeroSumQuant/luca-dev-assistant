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
        mock_client.list_tools.return_value = {"test_tool": {"name": "test_tool"}}

        bridge = MCPAutogenBridge(mock_client)
        await bridge.initialize()

        # Mock execute_tool to return a string
        mock_client.execute_tool = mock.AsyncMock(return_value="string result")

        # Get the wrapped function
        wrapped_func = bridge.autogen_tools[0].wrapped_func

        # Call with test arguments
        result = await wrapped_func(tool_key="test_tool", arg1="value1")

        # Verify string result is returned as-is
        assert result == "string result"
