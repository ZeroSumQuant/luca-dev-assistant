"""Schema definitions for ContextStore models.

This module defines the core data models for messages, tasks, and other
context-related information that needs to be persisted across conversations.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Role of the message sender."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    SPECIALIST = "specialist"


class Message(BaseModel):
    """A single message in a conversation."""

    id: str
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Conversation(BaseModel):
    """A conversation between the user and LUCA."""

    id: str
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    project_id: Optional[str] = None
    message_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskStatus(str, Enum):
    """Status of a task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class Task(BaseModel):
    """A task to be executed by an agent."""

    id: str
    agent_id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    parent_task_id: Optional[str] = None


class ClarificationRequest(BaseModel):
    """Request for clarification from an agent."""

    id: str
    task_id: str
    agent_id: str
    question: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
    response: Optional[str] = None


class TaskResult(BaseModel):
    """Result of a completed task."""

    task_id: str
    success: bool
    result: Any
    error_message: Optional[str] = None
    execution_time_ms: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MetricRecord(BaseModel):
    """Performance metrics for a completed task or agent execution."""

    task_id: str
    agent_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    latency_ms: int
    error_count: int
    user_feedback_score: Optional[float] = None
    tokens_used: int
    completion_status: Literal["success", "partial", "failure"]
    domain: str
    learning_mode: str
    additional_metrics: Dict[str, Any] = Field(default_factory=dict)


class Project(BaseModel):
    """Project representation for persistent state across sessions."""

    id: str
    name: str
    description: str
    domain: str  # References domain preset
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    git_repository: Optional[str] = None
    conversations: List[str] = Field(
        default_factory=list
    )  # References to conversation IDs
    files: Dict[str, str] = Field(default_factory=dict)  # filename -> file content hash
    custom_agents: List[str] = Field(
        default_factory=list
    )  # References to custom agent IDs

    def export_ticket(self) -> str:
        """Serializes conversation, files changed, and metrics into a JSON bundle for auditors."""
        # This is a placeholder for the actual implementation
        # In the real implementation, this would:
        # 1. Collect all conversations, file changes, and metrics
        # 2. Format them according to the ticket schema
        # 3. Return a serialized JSON string
        return f"Ticket for project {self.name} (ID: {self.id})"


class UserPreferences(BaseModel):
    """User preferences for LUCA."""

    user_id: str
    learning_mode: Literal["noob", "pro", "guru"] = "pro"
    theme: Literal["light", "dark", "system"] = "system"
    domain_preference: str = "general"
    model_preferences: Dict[str, str] = Field(
        default_factory=dict
    )  # agent_id -> model_name
    ui_preferences: Dict[str, Any] = Field(default_factory=dict)
