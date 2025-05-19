"""Final test to reach exact 95% coverage by hitting remaining lines."""

import sys
import unittest.mock as mock

import pytest

from luca_core.manager.manager import LucaManager, ResponseOptions
from luca_core.registry.registry import ToolRegistry
from luca_core.schemas.context import TaskResult
from luca_core.schemas.tools import ToolCategory


class TestFinalMissingCoverage:
    """Test to hit the exact remaining uncovered lines."""

    @pytest.mark.asyncio
    async def test_manager_line_407(self):
        """Cover manager.py line 407 specifically."""
        # Mock context store
        mock_store = mock.AsyncMock()
        manager = LucaManager(context_store=mock_store)
        options = ResponseOptions(verbose=False, learning_mode="pro")

        # Create results where all are failed (no successful results)
        # This ensures combined_result is empty and line 407 is hit
        failed_results = [
            TaskResult(
                task_id="1",
                success=False,
                result="",
                error_message="Error 1",
                execution_time_ms=100,
            ),
            TaskResult(
                task_id="2",
                success=False,
                result="",
                error_message="Error 2",
                execution_time_ms=200,
            ),
        ]

        result = await manager._aggregate_results(failed_results, options)
        assert (
            result
            == "I processed your request, but encountered errors and couldn't produce results."
        )

    def test_registry_line_290(self):
        """Cover registry.py line 290 specifically."""
        registry = ToolRegistry()

        # Register a tool
        @registry.register(name="test_tool", category=ToolCategory.UTILITY)
        def test_func():
            return "test"

        # Change function reference to something that doesn't exist
        registry.tools["test_tool"].function_reference = "nonexistent_func"

        # This should hit line 290
        with pytest.raises(ValueError, match="Function not found for tool: test_tool"):
            registry.execute_tool("test_tool", {})

    def test_registry_lines_325_337(self):
        """Cover registry.py lines 325-337 specifically."""
        registry = ToolRegistry()

        # Register a tool that raises an exception
        @registry.register(name="failing_tool", category=ToolCategory.UTILITY)
        def failing_func():
            raise ValueError("Test failure")

        # Add to current module so it can be found
        sys.modules[__name__].failing_func = failing_func
        registry.tools["failing_tool"].function_reference = "failing_func"

        # Get initial state
        tool = registry.tools["failing_tool"]
        initial_error_count = tool.metrics.error_count

        # Execute and expect exception (this hits lines 325-337)
        with pytest.raises(ValueError, match="Test failure"):
            registry.execute_tool("failing_tool", {})

        # Verify error metrics were updated
        assert tool.metrics.error_count == initial_error_count + 1
        assert tool.metrics.last_error is not None
        assert len(tool.metrics.error_details) > 0

        error_detail = tool.metrics.error_details[-1]
        assert error_detail["error_type"] == "ValueError"
        assert error_detail["error_message"] == "Test failure"
        assert "timestamp" in error_detail
