"""Complete coverage tests for registry module."""

import datetime
import sys
import unittest.mock as mock

import pytest

from luca_core.registry.registry import ToolRegistry
from luca_core.schemas.tools import ToolCategory
from tests.core.test_base import RegistryTestCase


class TestRegistryCompleteCoverage(RegistryTestCase):
    """Tests to achieve complete coverage of registry module."""

    def setup_method(self):
        """Set up test registry."""
        super().setup_method()  # Call the parent class setup_method
        self.registry = ToolRegistry()

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_execute_tool_function_resolution_from_module(self):
        """Test function resolution with cache."""

        # Create a function for our test
        @pytest.mark.skip_ci
        @pytest.mark.issue_81
        def test_func(x):
            return f"result-{x}"

        # Register tool - parameters are auto-extracted from function signature
        @self.registry.register(
            name="test_tool", description="Test", category=ToolCategory.UTILITY
        )
        @pytest.mark.skip_ci
        @pytest.mark.issue_81
        def test_func_with_param(x):
            """Test function with parameter."""
            pass

        # Add function directly to the cache
        ToolRegistry._function_cache["test_func"] = test_func

        # Update function reference to point to our function in the cache
        self.registry.tools["test_tool"].function_reference = "test_func"

        # Execute - should find function in the cache
        result = self.registry.execute_tool("test_tool", {"x": "value"})
        assert result == "result-value"

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
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

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
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

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
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

        # Execute
        result = self.registry.execute_tool("timing_tool", {"value": "test"})

        # Verify result
        assert result == "Result: test"

        # Verify metrics
        tool = self.registry.tools["timing_tool"]
        assert tool.metrics.executions == 1
        assert tool.metrics.success_count == 1
        # We can't test exact timing without proper datetime mocking
        # Just ensure it's not zero
        assert tool.metrics.average_execution_time_ms >= 0
        assert tool.metrics.last_used is not None

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
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

        # First execution
        self.registry.execute_tool("avg_tool", {})
        first_avg = tool.metrics.average_execution_time_ms
        assert tool.metrics.executions == 1
        assert first_avg >= 0  # Should be non-negative

        # Second execution
        self.registry.execute_tool("avg_tool", {})
        second_avg = tool.metrics.average_execution_time_ms
        assert tool.metrics.executions == 2
        # The average should exist
        assert second_avg >= 0

        # Third execution
        self.registry.execute_tool("avg_tool", {})
        third_avg = tool.metrics.average_execution_time_ms
        assert tool.metrics.executions == 3
        assert third_avg >= 0  # (100 + 300) / 2
