"""Schema package for LUCA Core.

This package contains all Pydantic models used throughout the LUCA system,
ensuring type consistency and validation across components.
"""

# Agent models
from luca_core.schemas.agent import (Agent, AgentCapability, AgentConfig,
                                     AgentRole, AgentStatus, AgentTeam,
                                     LearningMode, LLMModelConfig)
# Context models
from luca_core.schemas.context import (ClarificationRequest, Conversation,
                                       Message, MessageRole, MetricRecord,
                                       Project, Task, TaskResult, TaskStatus,
                                       UserPreferences)
# Error models
from luca_core.schemas.error import (ErrorCategory, ErrorCode, ErrorPayload,
                                     ErrorSeverity, create_system_error,
                                     create_timeout_error, create_user_error)
# Tool models
from luca_core.schemas.tools import (ToolCategory, ToolMetadata, ToolParameter,
                                     ToolRegistration, ToolScope,
                                     ToolSpecification, ToolUsageMetrics)

__all__ = [
    # Context models
    "Message",
    "MessageRole",
    "Conversation",
    "Task",
    "TaskStatus",
    "TaskResult",
    "ClarificationRequest",
    "MetricRecord",
    "Project",
    "UserPreferences",
    # Error models
    "ErrorPayload",
    "ErrorCategory",
    "ErrorSeverity",
    "ErrorCode",
    "create_user_error",
    "create_system_error",
    "create_timeout_error",
    # Tool models
    "ToolCategory",
    "ToolScope",
    "ToolMetadata",
    "ToolParameter",
    "ToolSpecification",
    "ToolUsageMetrics",
    "ToolRegistration",
    # Agent models
    "AgentRole",
    "AgentStatus",
    "AgentCapability",
    "LLMModelConfig",
    "AgentConfig",
    "Agent",
    "AgentTeam",
    "LearningMode",
]
