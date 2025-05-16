"""Schema definitions for tool registry.

This module defines the data models used by the tool registry to track
and manage available tools.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field


class ToolCategory(str, Enum):
    """Categories for tools to facilitate discovery and usage."""

    FILE_IO = "file_io"
    GIT = "git"
    CODE = "code"
    QUANTCONNECT = "quantconnect"
    DATA = "data"
    WEB = "web"
    SYSTEM = "system"
    UTILITY = "utility"
    MCP = "mcp"


class ToolScope(BaseModel):
    """Defines the scope (boundaries) of a tool's operation."""

    allowed_paths: List[str] = Field(default_factory=list)
    denied_paths: List[str] = Field(default_factory=list)
    resource_limits: Dict[str, Any] = Field(default_factory=dict)
    network_access: bool = False
    environment_variables: Dict[str, str] = Field(default_factory=dict)


class ToolMetadata(BaseModel):
    """Metadata for a registered tool."""

    name: str
    description: str
    version: str
    category: ToolCategory
    domain_tags: List[str] = Field(default_factory=list)
    scope: ToolScope
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deprecated: bool = False
    required_permissions: List[str] = Field(default_factory=list)
    author: Optional[str] = None
    homepage: Optional[str] = None


class ToolParameter(BaseModel):
    """Parameter specification for a tool."""

    name: str
    description: str
    type: str
    required: bool = True
    default: Optional[Any] = None
    enum_values: Optional[List[Any]] = None


class ToolSpecification(BaseModel):
    """Complete specification of a tool."""

    metadata: ToolMetadata
    parameters: List[ToolParameter]
    return_type: str
    return_description: str


class ToolUsageMetrics(BaseModel):
    """Metrics for tool usage."""

    tool_name: str
    executions: int = 0
    success_count: int = 0
    error_count: int = 0
    average_execution_time_ms: float = 0
    last_used: Optional[datetime] = None
    last_error: Optional[datetime] = None
    error_details: List[Dict[str, Any]] = Field(default_factory=list)


class ToolRegistration(BaseModel):
    """Registration information for a tool in the registry."""

    specification: ToolSpecification
    function_reference: str  # This will be a reference to the actual function
    metrics: ToolUsageMetrics
    enabled: bool = True
