"""Tests for tool registry execute_tool functionality."""

import unittest.mock
from datetime import datetime
from typing import Any, Dict

import pytest

from luca_core.registry import ToolRegistry

# Mark all tests in this file as requiring real execution (not mocked)
pytestmark = pytest.mark.real_exec
from luca_core.schemas import (
    ToolCategory,
    ToolMetadata,
    ToolParameter,
    ToolRegistration,
    ToolScope,
    ToolSpecification,
    ToolUsageMetrics,
)
from tests.core.test_base import RegistryTestCase

# No longer need the disable_autogen_mock fixture since we're using markers


def example_tool(message: str, count: int = 1) -> str:
    """Example tool function for testing."""
    return f"{message} x {count}"


def failing_tool() -> None:
    """Tool that always fails."""
    raise ValueError("This tool always fails")


def optional_params_tool(required: str, optional: str = "default") -> str:
    """Tool with optional parameters."""
    return f"{required} - {optional}"


class TestToolExecute(RegistryTestCase):
    """Test the tool.execute_tool method."""

    def setup_method(self):
        """Set up test fixture."""
        super().setup_method()  # Call the parent class setup_method
        self.registry = ToolRegistry()

        # Register example tool
        metadata = ToolMetadata(
            name="example_tool",
            description="Example tool for testing",
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
            parameters=[
                ToolParameter(
                    name="message",
                    description="Message to repeat",
                    type="str",
                    required=True,
                ),
                ToolParameter(
                    name="count",
                    description="Number of times to repeat",
                    type="int",
                    required=False,
                    default=1,
                ),
            ],
            return_type="str",
            return_description="Formatted message",
        )

        registration = ToolRegistration(
            specification=spec,
            function_reference="example_tool",
            metrics=ToolUsageMetrics(tool_name="example_tool"),
        )

        self.registry.tools = {"example_tool": registration}

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_execute_tool_success(self):
        """Test executing a tool successfully."""
        # Debug: check environment
        import os

        print("\n=== DEBUGGING AUTOGEN_USE_MOCK_RESPONSE ===")
        print(
            f"AUTOGEN_USE_MOCK_RESPONSE = {os.environ.get('AUTOGEN_USE_MOCK_RESPONSE', 'NOT SET')}"
        )
        print(f"CI = {os.environ.get('CI', 'NOT SET')}")

        # Add the function directly to the cache
        ToolRegistry._function_cache["example_tool"] = example_tool

        # Guard against unexpected mocking
        assert not isinstance(
            ToolRegistry._function_cache["example_tool"], unittest.mock.MagicMock
        ), "Tool unexpectedly mocked—check AUTOGEN_USE_MOCK_RESPONSE"

        # Debug what's in the registry
        print(f"Registry tools: {list(self.registry.tools.keys())}")
        if "example_tool" in self.registry.tools:
            tool_reg = self.registry.tools["example_tool"]
            print(f"Tool function_reference: {tool_reg.function_reference}")
            print(
                f"Tool parameters: {[p.name for p in tool_reg.specification.parameters]}"
            )

        result = self.registry.execute_tool(
            "example_tool", {"message": "Hello", "count": 3}
        )
        assert result == "Hello x 3"

        # Check metrics were updated
        tool = self.registry.get_tool("example_tool")
        assert tool.metrics.executions == 1
        assert tool.metrics.success_count == 1
        assert tool.metrics.error_count == 0
        assert tool.metrics.last_used is not None
        assert tool.metrics.average_execution_time_ms >= 0

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_execute_tool_missing_required_param(self):
        """Test executing a tool without required parameters."""
        # Ensure the function is in the cache
        ToolRegistry._function_cache["example_tool"] = example_tool

        with pytest.raises(TypeError, match="Missing required parameter: message"):
            self.registry.execute_tool("example_tool", {"count": 3})

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_execute_tool_not_found(self):
        """Test executing a non-existent tool."""
        with pytest.raises(ValueError, match="Tool not found: non_existent"):
            self.registry.execute_tool("non_existent", {})

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_execute_tool_with_failure(self):
        """Test executing a tool that fails."""
        # Register failing tool
        metadata = ToolMetadata(
            name="failing_tool",
            description="Always fails",
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
            function_reference="failing_tool",
            metrics=ToolUsageMetrics(tool_name="failing_tool"),
        )

        self.registry.tools["failing_tool"] = registration

        # Add the function directly to the cache
        ToolRegistry._function_cache["failing_tool"] = failing_tool

        with pytest.raises(ValueError, match="This tool always fails"):
            self.registry.execute_tool("failing_tool", {})

        # Check error metrics
        tool = self.registry.get_tool("failing_tool")
        assert tool.metrics.executions == 1
        assert tool.metrics.success_count == 0
        assert tool.metrics.error_count == 1
        assert tool.metrics.last_error is not None
        assert len(tool.metrics.error_details) == 1

        error = tool.metrics.error_details[0]
        assert error["error_type"] == "ValueError"
        assert error["error_message"] == "This tool always fails"

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_execute_with_defaults(self):
        """Test executing a tool with default parameters."""
        # Ensure the function is in the cache
        ToolRegistry._function_cache["example_tool"] = example_tool

        result = self.registry.execute_tool("example_tool", {"message": "Test"})
        assert result == "Test x 1"

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_execute_unknown_params_ignored(self):
        """Test that unknown parameters are ignored."""
        # Ensure the function is in the cache
        ToolRegistry._function_cache["example_tool"] = example_tool

        result = self.registry.execute_tool(
            "example_tool", {"message": "Hello", "unknown": "ignored"}
        )
        assert result == "Hello x 1"

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_multiple_executions_update_metrics(self):
        """Test that multiple executions update metrics correctly."""
        # Ensure the function is in the cache
        ToolRegistry._function_cache["example_tool"] = example_tool

        # First execution
        self.registry.execute_tool("example_tool", {"message": "First"})
        tool = self.registry.get_tool("example_tool")
        first_avg = tool.metrics.average_execution_time_ms

        # Second execution
        self.registry.execute_tool("example_tool", {"message": "Second"})
        tool = self.registry.get_tool("example_tool")

        assert tool.metrics.executions == 2
        assert tool.metrics.success_count == 2

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_function_not_found(self):
        """Test when function reference cannot be resolved."""
        # Create a tool with non-existent function
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
