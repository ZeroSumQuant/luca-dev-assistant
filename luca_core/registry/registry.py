"""Tool registry implementation.

This module provides a registry for tools that can be used by agents,
with support for registration, discovery, and execution.
"""

import functools
import inspect
import logging
import sys
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union, get_type_hints

from luca_core.schemas import (
    ErrorPayload,
    ToolCategory,
    ToolMetadata,
    ToolParameter,
    ToolRegistration,
    ToolScope,
    ToolSpecification,
    ToolUsageMetrics,
    create_system_error,
    create_user_error,
)

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for tools that can be used by agents.

    Note: ToolRegistry is not thread-safe; use one registry per OS process.
    """

    _function_cache: Dict[str, Callable] = (
        {}
    )  # Class-level cache for function references

    def __init__(self, default_scope: Optional[ToolScope] = None):
        """Initialize the tool registry.

        Args:
            default_scope: Default scope for tools without explicit scope
        """
        self.tools: Dict[str, ToolRegistration] = {}
        self.default_scope = default_scope or ToolScope(
            allowed_paths=["/workspace/luca/**"],
            denied_paths=[],
            resource_limits={
                "memory_mb": 1024,
                "cpu_seconds": 30,
                "storage_mb": 100,
            },
            network_access=False,
        )

    def register(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        version: str = "0.1.0",
        category: Union[ToolCategory, str] = ToolCategory.UTILITY,
        domain_tags: Optional[List[str]] = None,
        scope: Optional[ToolScope] = None,
        required_permissions: Optional[List[str]] = None,
        author: Optional[str] = None,
        homepage: Optional[str] = None,
    ) -> Callable:
        """Decorator to register a tool function.

        Args:
            name: Name of the tool (defaults to function name)
            description: Tool description (defaults to function docstring)
            version: Tool version
            category: Tool category
            domain_tags: List of domain tags for discovery
            scope: Tool scope (permissions, resource limits)
            required_permissions: Required permissions to use this tool
            author: Tool author
            homepage: Tool homepage or documentation URL

        Returns:
            Decorator function

        Raises:
            KeyError: If a function with the same name is already registered

        Example:
            @registry.register(
                description="Read a text file",
                category=ToolCategory.FILE_IO,
                domain_tags=["general", "file"]
            )
            def read_text(path: str) -> str:
                \"\"\"Read UTF-8 text from a file.\"\"\"
                # Implementation...
        """

        def decorator(func: Callable) -> Callable:
            # Get function signature and docstring
            func_name = name or func.__name__
            func_doc = inspect.getdoc(func) or ""
            func_desc = description or func_doc

            # Extract parameter info from function signature
            sig = inspect.signature(func)
            type_hints = get_type_hints(func)

            parameters = []
            for param_name, param in sig.parameters.items():
                if (
                    param_name == "self"
                    or param.kind == param.VAR_POSITIONAL
                    or param.kind == param.VAR_KEYWORD
                ):
                    continue

                param_type = type_hints.get(param_name, Any).__name__
                param_default = None if param.default is param.empty else param.default
                param_required = param.default is param.empty

                parameters.append(
                    ToolParameter(
                        name=param_name,
                        description=f"Parameter {param_name}",  # Could parse from docstring in a more advanced version
                        type=param_type,
                        required=param_required,
                        default=param_default,
                    )
                )

            # Create tool metadata
            tool_category = category
            if isinstance(tool_category, str):
                try:
                    tool_category = ToolCategory(tool_category)
                except ValueError:
                    tool_category = ToolCategory.UTILITY

            tool_metadata = ToolMetadata(
                name=func_name,
                description=func_desc,
                version=version,
                category=tool_category,
                domain_tags=domain_tags or [],
                scope=scope or self.default_scope,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                deprecated=False,
                required_permissions=required_permissions or [],
                author=author,
                homepage=homepage,
            )

            # Determine return type
            return_type = type_hints.get("return", Any).__name__

            # Create tool specification
            tool_spec = ToolSpecification(
                metadata=tool_metadata,
                parameters=parameters,
                return_type=return_type,
                return_description=f"Returns {return_type}",  # Could parse from docstring
            )

            # Create usage metrics
            tool_metrics = ToolUsageMetrics(
                tool_name=func_name,
            )

            # Create the tool registration
            tool_reg = ToolRegistration(
                specification=tool_spec,
                function_reference=func.__name__,
                metrics=tool_metrics,
                enabled=True,
            )

            # Check for duplicate function references
            if func.__name__ in ToolRegistry._function_cache:
                raise KeyError(f"Function '{func.__name__}' is already registered")

            # Register the tool
            self.tools[func_name] = tool_reg

            # Store the function in the cache
            ToolRegistry._function_cache[func.__name__] = func

            # Return the original function
            return func

        return decorator

    def register_function(self, func: Callable, **kwargs: Any) -> None:
        """Register a function as a tool (non-decorator version).

        Args:
            func: Function to register
            **kwargs: Keyword arguments to pass to register decorator
        """
        decorator = self.register(**kwargs)
        decorator(func)

    @classmethod
    def reset(cls) -> None:
        """Reset the function cache - primarily for testing."""
        cls._function_cache.clear()

    def unregister(self, name: str) -> bool:
        """Unregister a tool.

        Args:
            name: Name of the tool to unregister

        Returns:
            True if the tool was found and unregistered, False otherwise
        """
        if name in self.tools:
            tool = self.tools[name]
            func_ref = tool.function_reference

            # Remove from function cache if present
            if func_ref in ToolRegistry._function_cache:
                del ToolRegistry._function_cache[func_ref]

            del self.tools[name]
            return True
        return False

    def get_tool(self, name: str) -> Optional[ToolRegistration]:
        """Get a tool by name.

        Args:
            name: Name of the tool

        Returns:
            Tool registration or None if not found
        """
        return self.tools.get(name)

    def list_tools(self) -> List[ToolRegistration]:
        """List all registered tools.

        Returns:
            List of tool registrations
        """
        return list(self.tools.values())

    def get_tools_by_category(
        self, category: Union[ToolCategory, str]
    ) -> List[ToolRegistration]:
        """Get tools by category.

        Args:
            category: Tool category

        Returns:
            List of tool registrations matching the category
        """
        if isinstance(category, str):
            try:
                category = ToolCategory(category)
            except ValueError:
                return []

        return [
            tool
            for tool in self.tools.values()
            if tool.specification.metadata.category == category
        ]

    def get_tools_by_domain(self, domain: str) -> List[ToolRegistration]:
        """Get tools by domain tag.

        Args:
            domain: Domain tag

        Returns:
            List of tool registrations with the domain tag
        """
        return [
            tool
            for tool in self.tools.values()
            if domain in tool.specification.metadata.domain_tags
        ]

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool by name with provided arguments.

        Args:
            name: Name of the tool
            arguments: Arguments to pass to the tool

        Returns:
            Result of the tool execution

        Raises:
            ValueError: If the tool is not found
            TypeError: If arguments are invalid
        """
        # Get the tool
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")

        # Get the function reference from cache
        func_ref = tool.function_reference
        func = ToolRegistry._function_cache.get(func_ref)

        if func is None:
            raise ValueError(f"Function not found for tool: {name}")

        # Extract expected parameters
        expected_params = {param.name: param for param in tool.specification.parameters}

        # Validate arguments
        for param_name, param_spec in expected_params.items():
            if param_spec.required and param_name not in arguments:
                raise TypeError(f"Missing required parameter: {param_name}")

        # Build the call arguments
        call_args = {}
        for param_name, param_value in arguments.items():
            if param_name in expected_params:
                call_args[param_name] = param_value

        # Record metrics
        tool.metrics.executions += 1
        tool.metrics.last_used = datetime.utcnow()

        # Execute the tool
        try:
            start_time = datetime.utcnow()
            result = func(**call_args)
            end_time = datetime.utcnow()

            # Update metrics
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            tool.metrics.success_count += 1
            tool.metrics.average_execution_time_ms = (
                tool.metrics.average_execution_time_ms * (tool.metrics.executions - 1)
                + execution_time_ms
            ) / tool.metrics.executions

            return result
        except Exception as e:
            # Record error
            tool.metrics.error_count += 1
            tool.metrics.last_error = datetime.utcnow()
            tool.metrics.error_details.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )

            raise


# Create a global tool registry instance
registry = ToolRegistry()


def tool(*args, **kwargs):
    """Decorator to register a tool with the global registry.

    This can be used as a shortcut for registry.register.

    Example:
        @tool(
            description="Read a text file",
            category=ToolCategory.FILE_IO,
            domain_tags=["general", "file"]
        )
        def read_text(path: str) -> str:
            \"\"\"Read UTF-8 text from a file.\"\"\"
            # Implementation...
    """
    # Allow both @tool and @tool() forms
    if len(args) == 1 and callable(args[0]) and not kwargs:
        return registry.register()(args[0])
    else:
        return registry.register(*args, **kwargs)
