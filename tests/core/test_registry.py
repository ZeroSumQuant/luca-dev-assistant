"""Tests for the tool registry implementation."""

from datetime import datetime
from typing import Any, Optional

import pytest

from luca_core.registry import ToolRegistry
from luca_core.schemas import (
    ToolCategory,
    ToolScope,
    create_system_error,
    create_user_error,
)


# Sample functions to use for testing
def sample_tool(param1: str, param2: int = 42) -> str:
    """A sample tool for testing."""
    return f"{param1}:{param2}"


def no_params_tool() -> str:
    """Tool with no parameters."""
    return "success"


def optional_params_tool(required: str, optional: Optional[str] = None) -> dict:
    """Tool with optional parameters."""
    return {"required": required, "optional": optional}


class TestToolRegistry:
    """Test the ToolRegistry class."""

    def setup_method(self):
        """Reset the registry's function cache before each test."""
        ToolRegistry.reset()

    def test_init(self):
        """Test registry initialization."""
        registry = ToolRegistry()
        assert registry.tools == {}
        assert registry.default_scope is not None
        assert registry.default_scope.resource_limits["memory_mb"] == 1024

    def test_init_with_custom_scope(self):
        """Test registry initialization with custom scope."""
        custom_scope = ToolScope(
            allowed_paths=["/custom/**"],
            denied_paths=["/private/**"],
            resource_limits={"memory_mb": 2048},
            network_access=True,
        )
        registry = ToolRegistry(default_scope=custom_scope)
        assert registry.default_scope == custom_scope
        assert registry.default_scope.network_access is True

    def test_register_decorator(self):
        """Test the register decorator."""
        registry = ToolRegistry()

        @registry.register(
            name="test_tool",
            description="A test tool",
            category=ToolCategory.UTILITY,
            version="1.0",
            domain_tags=["test"],
        )
        def my_tool(param: str) -> str:
            """My tool docstring."""
            return f"Result: {param}"

        assert "test_tool" in registry.tools
        tool_reg = registry.tools["test_tool"]
        assert tool_reg.specification.metadata.name == "test_tool"
        assert tool_reg.specification.metadata.description == "A test tool"
        assert tool_reg.specification.metadata.category == ToolCategory.UTILITY
        assert tool_reg.specification.metadata.version == "1.0"
        assert "test" in tool_reg.specification.metadata.domain_tags

    def test_register_decorator_defaults(self):
        """Test the register decorator with defaults."""
        registry = ToolRegistry()

        @registry.register()
        def another_tool(value: int) -> int:
            """Doubles the value."""
            return value * 2

        assert "another_tool" in registry.tools
        tool_reg = registry.tools["another_tool"]
        assert tool_reg.specification.metadata.name == "another_tool"
        assert tool_reg.specification.metadata.description == "Doubles the value."
        assert tool_reg.specification.metadata.version == "0.1.0"

    def test_register_function(self):
        """Test registering a function directly."""
        registry = ToolRegistry()
        registry.register_function(
            sample_tool,
            name="sample",
            description="A sample tool",
            category="utility",
        )

        assert "sample" in registry.tools
        tool_reg = registry.tools["sample"]
        assert tool_reg.specification.metadata.name == "sample"
        assert len(tool_reg.specification.parameters) == 2

        # Check parameters
        param1 = tool_reg.specification.parameters[0]
        assert param1.name == "param1"
        assert param1.required is True

        param2 = tool_reg.specification.parameters[1]
        assert param2.name == "param2"
        assert param2.required is False
        assert param2.default == 42

    def test_register_with_invalid_category(self):
        """Test registering with invalid category string."""
        registry = ToolRegistry()

        @registry.register(category="invalid_category")
        def test_tool() -> str:
            return "test"

        tool_reg = registry.tools["test_tool"]
        # Should default to UTILITY when invalid
        assert tool_reg.specification.metadata.category == ToolCategory.UTILITY

    def test_unregister(self):
        """Test unregistering a tool."""
        registry = ToolRegistry()

        @registry.register(name="temp_tool")
        def temp_tool() -> str:
            return "temp"

        assert "temp_tool" in registry.tools

        # Unregister should return True
        result = registry.unregister("temp_tool")
        assert result is True
        assert "temp_tool" not in registry.tools

    def test_unregister_nonexistent(self):
        """Test unregistering a nonexistent tool."""
        registry = ToolRegistry()

        # Unregister nonexistent should return False
        result = registry.unregister("nonexistent")
        assert result is False

    def test_get_tool(self):
        """Test getting a tool by name."""
        registry = ToolRegistry()

        @registry.register(name="lookup_tool")
        def lookup_tool() -> str:
            return "found"

        tool = registry.get_tool("lookup_tool")
        assert tool is not None
        assert tool.specification.metadata.name == "lookup_tool"

    def test_get_tool_nonexistent(self):
        """Test getting a nonexistent tool by name."""
        registry = ToolRegistry()

        tool = registry.get_tool("nonexistent")
        assert tool is None

    def test_list_tools(self):
        """Test listing all tools."""
        registry = ToolRegistry()

        @registry.register(name="tool1")
        def tool1() -> str:
            return "1"

        @registry.register(name="tool2")
        def tool2() -> str:
            return "2"

        tools = registry.list_tools()
        assert len(tools) == 2
        tool_names = [t.specification.metadata.name for t in tools]
        assert "tool1" in tool_names
        assert "tool2" in tool_names

    def test_get_tools_by_category(self):
        """Test getting tools by category."""
        registry = ToolRegistry()

        @registry.register(name="code_tool", category=ToolCategory.CODE)
        def code_tool() -> str:
            return "code"

        @registry.register(name="data_tool", category=ToolCategory.DATA)
        def data_tool() -> str:
            return "data"

        @registry.register(name="another_code_tool", category=ToolCategory.CODE)
        def another_code_tool() -> str:
            return "code2"

        # Test with enum
        code_tools = registry.get_tools_by_category(ToolCategory.CODE)
        assert len(code_tools) == 2

        # Test with string - need to use lowercase
        data_tools = registry.get_tools_by_category("data")
        assert len(data_tools) == 1
        assert data_tools[0].specification.metadata.name == "data_tool"

        # Test with invalid string
        invalid_tools = registry.get_tools_by_category("INVALID")
        assert len(invalid_tools) == 0

    def test_get_tools_by_domain(self):
        """Test getting tools by domain tag."""
        registry = ToolRegistry()

        @registry.register(name="web_tool", domain_tags=["web", "api"])
        def web_tool() -> str:
            return "web"

        @registry.register(name="data_tool", domain_tags=["data", "analytics"])
        def data_tool() -> str:
            return "data"

        @registry.register(name="another_web_tool", domain_tags=["web"])
        def another_web_tool() -> str:
            return "web2"

        web_tools = registry.get_tools_by_domain("web")
        assert len(web_tools) == 2

        data_tools = registry.get_tools_by_domain("data")
        assert len(data_tools) == 1

        nonexistent_tools = registry.get_tools_by_domain("nonexistent")
        assert len(nonexistent_tools) == 0

    def test_parameter_extraction(self):
        """Test that parameters are correctly extracted from function signature."""
        registry = ToolRegistry()

        @registry.register()
        def complex_tool(
            required_str: str,
            optional_str: str = "default",
            required_int: int = 0,
            *args,
            **kwargs,
        ) -> dict:
            """Complex tool with various parameter types."""
            return {}

        tool_reg = registry.tools["complex_tool"]
        params = tool_reg.specification.parameters

        # Should have 3 parameters (args and kwargs are skipped)
        assert len(params) == 3

        # Check first parameter
        assert params[0].name == "required_str"
        assert params[0].required is True
        assert params[0].type == "str"

        # Check second parameter
        assert params[1].name == "optional_str"
        assert params[1].required is False
        assert params[1].default == "default"

        # Check third parameter
        assert params[2].name == "required_int"
        assert params[2].required is False
        assert params[2].default == 0

    def test_metadata_timestamps(self):
        """Test that created_at and updated_at are set."""
        registry = ToolRegistry()

        @registry.register()
        def timestamp_tool() -> str:
            return "test"

        tool_reg = registry.tools["timestamp_tool"]
        metadata = tool_reg.specification.metadata

        # Timestamps should be set and recent
        assert isinstance(metadata.created_at, datetime)
        assert isinstance(metadata.updated_at, datetime)
        # They might not be exactly equal due to microsecond differences, so check they're close
        time_diff = abs((metadata.updated_at - metadata.created_at).total_seconds())
        assert time_diff < 0.001  # Less than 1 millisecond difference

        # Should be recent (within last minute)
        time_diff = datetime.utcnow() - metadata.created_at
        assert time_diff.total_seconds() < 60
