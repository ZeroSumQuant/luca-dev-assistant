"""Complete coverage tests for registry module."""

import datetime
import sys
import unittest.mock as mock

import pytest

from luca_core.registry.registry import ToolRegistry
from luca_core.schemas.tools import ToolCategory


class TestRegistryCompleteCoverage:
    """Tests to achieve complete coverage of registry module."""

    def setup_method(self):
        """Set up test registry."""
        self.registry = ToolRegistry()

    def test_execute_tool_function_resolution_from_module(self):
        """Test function resolution from sys.modules."""
        # Create a mock module with our function
        mock_module = mock.MagicMock()

        def test_func(x):
            return f"result-{x}"

        setattr(mock_module, "test_func", test_func)

        # Add to sys.modules
        sys.modules["test_module"] = mock_module

        # Register tool
        @self.registry.register(
            name="test_tool", description="Test", category=ToolCategory.UTILITY
        )
        def test_func_placeholder():
            pass

        # Update function reference to point to module function
        self.registry.tools["test_tool"].function_reference = "test_func"

        # Execute - should find function in module
        result = self.registry.execute_tool("test_tool", {"x": "value"})
        assert result == "result-value"

        # Cleanup
        del sys.modules["test_module"]

    def test_execute_tool_function_not_found(self):
        """Test function not found error path."""

        # Register a tool with non-existent function
        @self.registry.register(
            name="missing_tool", description="Test", category=ToolCategory.UTILITY
        )
        def placeholder():
            pass

        # Set function reference to non-existent function
        self.registry.tools["missing_tool"].function_reference = "non_existent_func"

        # Should raise ValueError
        with pytest.raises(
            ValueError, match="Function not found for tool: missing_tool"
        ):
            self.registry.execute_tool("missing_tool", {})

    def test_execute_tool_with_exception_metrics(self):
        """Test exception handling and metrics update."""

        # Register a tool that raises an exception
        @self.registry.register(
            name="error_tool", description="Test", category=ToolCategory.UTILITY
        )
        def error_func():
            raise RuntimeError("Test error")

        # Make function findable
        globals()["error_func"] = error_func
        self.registry.tools["error_tool"].function_reference = "error_func"

        # Get initial metrics
        tool = self.registry.tools["error_tool"]
        initial_error_count = tool.metrics.error_count

        # Execute and expect exception
        with pytest.raises(RuntimeError, match="Test error"):
            self.registry.execute_tool("error_tool", {})

        # Verify metrics were updated
        assert tool.metrics.error_count == initial_error_count + 1
        assert tool.metrics.last_error is not None
        assert len(tool.metrics.error_details) > 0

        # Check error details
        last_error = tool.metrics.error_details[-1]
        assert last_error["error_type"] == "RuntimeError"
        assert last_error["error_message"] == "Test error"
        assert "timestamp" in last_error

    def test_execute_tool_success_with_timing(self):
        """Test successful execution with timing metrics."""

        # Register a simple tool
        @self.registry.register(
            name="timing_tool", description="Test", category=ToolCategory.UTILITY
        )
        def timing_func(value="default"):
            return f"Result: {value}"

        # Make function findable
        globals()["timing_func"] = timing_func
        self.registry.tools["timing_tool"].function_reference = "timing_func"

        # Mock datetime for controlled timing
        with mock.patch("luca_core.registry.registry.datetime") as mock_datetime:
            # Set up times
            start_time = datetime.datetime(2024, 1, 1, 10, 0, 0)
            end_time = datetime.datetime(2024, 1, 1, 10, 0, 0, 500000)  # 500ms later

            mock_datetime.utcnow.side_effect = [start_time, end_time, end_time]

            # Execute
            result = self.registry.execute_tool("timing_tool", {"value": "test"})

            # Verify result
            assert result == "Result: test"

            # Verify metrics
            tool = self.registry.tools["timing_tool"]
            assert tool.metrics.executions == 1
            assert tool.metrics.total_execution_time_ms == 500
            assert tool.metrics.average_execution_time_ms == 500
            assert tool.metrics.last_execution == end_time

    def test_multiple_executions_average_timing(self):
        """Test average timing calculation across multiple executions."""

        # Register a simple tool
        @self.registry.register(
            name="avg_tool", description="Test", category=ToolCategory.UTILITY
        )
        def avg_func():
            return "done"

        # Make function findable
        globals()["avg_func"] = avg_func
        self.registry.tools["avg_tool"].function_reference = "avg_func"

        tool = self.registry.tools["avg_tool"]

        # Mock datetime for controlled timing
        with mock.patch("luca_core.registry.registry.datetime") as mock_datetime:
            # First execution: 100ms
            mock_datetime.utcnow.side_effect = [
                datetime.datetime(2024, 1, 1, 10, 0, 0),
                datetime.datetime(2024, 1, 1, 10, 0, 0, 100000),
                datetime.datetime(2024, 1, 1, 10, 0, 0, 100000),
            ]
            self.registry.execute_tool("avg_tool", {})
            assert tool.metrics.average_execution_time_ms == 100

            # Second execution: 300ms (average should be 200)
            mock_datetime.utcnow.side_effect = [
                datetime.datetime(2024, 1, 1, 10, 0, 1),
                datetime.datetime(2024, 1, 1, 10, 0, 1, 300000),
                datetime.datetime(2024, 1, 1, 10, 0, 1, 300000),
            ]
            self.registry.execute_tool("avg_tool", {})
            assert tool.metrics.executions == 2
            assert tool.metrics.average_execution_time_ms == 200  # (100 + 300) / 2
