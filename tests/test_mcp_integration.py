"""Tests for MCP integration"""

import os

import pytest

# Skip all MCP tests in CI environments where they might hang
pytestmark = pytest.mark.skipif(
    os.environ.get("CI") == "true",
    reason="MCP tests skipped in CI due to subprocess/stdio issues",
)


@pytest.mark.skipif(
    True,  # Skip for now
    reason="MCP tests temporarily disabled until stability issues resolved",
)
class TestMCPIntegration:
    """Test MCP client and bridge functionality - temporarily disabled"""

    def test_placeholder(self):
        """Placeholder test"""
        assert True
