"""Additional tests to improve coverage for registry module."""

import datetime
import sys
import unittest.mock as mock

import pytest

from luca_core.registry.registry import ToolRegistry, registry, tool
from luca_core.schemas.tools import (
    ToolCategory,
    ToolMetadata,
    ToolParameter,
    ToolRegistration,
    ToolScope,
    ToolSpecification,
    ToolUsageMetrics,
)


class TestToolDecorator:
    """Test the @tool decorator function."""

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_tool_decorator_basic(self):
        """Test basic usage of @tool decorator."""

        # Use decorator without parentheses
        @tool
        def sample_tool():
            """A sample tool."""
            return "result"

        # Verify the tool is registered
        assert "sample_tool" in registry.tools
        assert (
            registry.tools["sample_tool"].specification.metadata.name == "sample_tool"
        )

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_tool_decorator_with_args(self):
        """Test @tool decorator with arguments."""

        @tool(
            description="Test tool", category=ToolCategory.UTILITY, domain_tags=["test"]
        )
        def another_tool():
            """Another sample tool."""
            return "another result"

        # Verify the tool is registered with custom metadata
        assert "another_tool" in registry.tools
        tool_spec = registry.tools["another_tool"].specification
        assert tool_spec.metadata.description == "Test tool"
        assert tool_spec.metadata.category == ToolCategory.UTILITY
        assert "test" in tool_spec.metadata.domain_tags


class TestRegistryErrorHandling:
    """Test error handling in registry execute_tool method."""

    def setup_method(self):
        """Set up test registry."""
        self.registry = ToolRegistry()

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_execute_tool_with_exception(self):
        """Test execute_tool error handling and metrics recording."""

        # Define a tool that raises an exception
        def failing_tool():
            raise ValueError("Tool failure")

        # Register the tool
        self.registry.register(
            name="failing_tool",
            description="A tool that fails",
            category=ToolCategory.UTILITY,
        )(failing_tool)

        # Add the function to current module so registry can find it
        sys.modules[__name__].failing_tool = failing_tool

        # Get the tool registration
        tool = self.registry.tools["failing_tool"]
        initial_error_count = tool.metrics.error_count

        # Execute and expect failure
        with pytest.raises(ValueError, match="Tool failure"):
            self.registry.execute_tool("failing_tool", {})

        # Verify error metrics were updated
        assert tool.metrics.error_count == initial_error_count + 1
        assert tool.metrics.last_error is not None
        assert len(tool.metrics.error_details) > 0

        # Check the error details
        last_error = tool.metrics.error_details[-1]
        assert last_error["error_type"] == "ValueError"
        assert last_error["error_message"] == "Tool failure"
        assert "timestamp" in last_error

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_execute_tool_metrics_calculation(self):
        """Test execution time metrics calculation."""

        # Define a simple tool
        def simple_tool():
            return "success"

        # Register the tool
        self.registry.register(
            name="simple_tool",
            description="A simple tool",
            category=ToolCategory.UTILITY,
        )(simple_tool)

        # Add the function to current module so registry can find it
        sys.modules[__name__].simple_tool = simple_tool

        # Mock datetime to control timing
        with mock.patch("luca_core.registry.registry.datetime") as mock_datetime:
            # Set up mock times
            start_time = datetime.datetime(2024, 1, 1, 10, 0, 0)
            end_time = datetime.datetime(2024, 1, 1, 10, 0, 1)  # 1 second later

            mock_datetime.utcnow.side_effect = [start_time, end_time, end_time]

            # Execute the tool
            result = self.registry.execute_tool("simple_tool", {})

            # Verify result
            assert result == "success"

            # Check metrics
            tool = self.registry.tools["simple_tool"]
            assert tool.metrics.executions == 1
            assert tool.metrics.total_execution_time_ms == 1000  # 1 second in ms
            assert tool.metrics.average_execution_time_ms == 1000
            assert tool.metrics.last_execution == end_time

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_execute_tool_average_time_calculation(self):
        """Test average execution time calculation over multiple runs."""

        # Define a simple tool
        def quick_tool():
            return "done"

        # Register the tool
        self.registry.register(
            name="quick_tool", description="A quick tool", category=ToolCategory.UTILITY
        )(quick_tool)

        # Add the function to current module so registry can find it
        sys.modules[__name__].quick_tool = quick_tool

        tool = self.registry.tools["quick_tool"]

        # Mock datetime for controlled timing
        with mock.patch("luca_core.registry.registry.datetime") as mock_datetime:
            # First execution: 100ms
            mock_datetime.utcnow.side_effect = [
                datetime.datetime(2024, 1, 1, 10, 0, 0),
                datetime.datetime(2024, 1, 1, 10, 0, 0, 100000),  # 100ms later
                datetime.datetime(2024, 1, 1, 10, 0, 0, 100000),
            ]
            self.registry.execute_tool("quick_tool", {})

            assert tool.metrics.executions == 1
            assert tool.metrics.average_execution_time_ms == 100

            # Second execution: 200ms
            mock_datetime.utcnow.side_effect = [
                datetime.datetime(2024, 1, 1, 10, 0, 1),
                datetime.datetime(2024, 1, 1, 10, 0, 1, 200000),  # 200ms later
                datetime.datetime(2024, 1, 1, 10, 0, 1, 200000),
            ]
            self.registry.execute_tool("quick_tool", {})

            assert tool.metrics.executions == 2
            # Average of 100ms and 200ms = 150ms
            assert tool.metrics.average_execution_time_ms == 150

            # Third execution: 300ms
            mock_datetime.utcnow.side_effect = [
                datetime.datetime(2024, 1, 1, 10, 0, 2),
                datetime.datetime(2024, 1, 1, 10, 0, 2, 300000),  # 300ms later
                datetime.datetime(2024, 1, 1, 10, 0, 2, 300000),
            ]
            self.registry.execute_tool("quick_tool", {})

            assert tool.metrics.executions == 3
            # Average of 100ms, 200ms, and 300ms = 200ms
            assert tool.metrics.average_execution_time_ms == 200

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_tool_not_found_error(self):
        """Test execute_tool with non-existent tool."""
        with pytest.raises(ValueError, match="Tool not found: nonexistent"):
            self.registry.execute_tool("nonexistent", {})

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_function_not_found_error(self):
        """Test execute_tool when function cannot be resolved."""
        # Register a tool with a non-existent function reference
        metadata = ToolMetadata(
            name="missing_func",
            description="Missing function",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            domain_tags=["test"],
            scope=ToolScope(
                allowed_paths=["/tmp"],
                allowed_hosts=[],
                allowed_protocols=[],
                rate_limits={},
            ),
        )

        spec = ToolSpecification(
            metadata=metadata,
            parameters=[],
            return_type="None",
            return_description="Nothing",
        )

        registration = ToolRegistration(
            specification=spec,
            function_reference="non_existent_function",
            metrics=ToolUsageMetrics(tool_name="missing_func"),
        )

        self.registry.tools["missing_func"] = registration

        with pytest.raises(
            ValueError, match="Function not found for tool: missing_func"
        ):
            self.registry.execute_tool("missing_func", {})
