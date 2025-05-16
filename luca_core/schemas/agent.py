"""Schema definitions for agent management.

This module defines the data models used to manage and configure
agents within the LUCA system.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Set, Union

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Roles that agents can perform in the system."""

    MANAGER = "manager"
    CODER = "coder"
    TESTER = "tester"
    DOC_WRITER = "doc_writer"
    ANALYST = "analyst"
    CUSTOM = "custom"


class AgentStatus(str, Enum):
    """Possible statuses for an agent."""

    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    DISABLED = "disabled"


class LLMModelConfig(BaseModel):
    """Configuration for LLM model used by an agent."""

    model_name: str
    temperature: float = 0.2
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    stop_sequences: List[str] = Field(default_factory=list)
    timeout_seconds: int = 30


class AgentCapability(str, Enum):
    """Capabilities that agents can possess."""

    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    REFACTORING = "refactoring"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    QUANTITATIVE_ANALYSIS = "quantitative_analysis"
    PLANNING = "planning"
    PROJECT_MANAGEMENT = "project_management"
    DEBUGGING = "debugging"
    DATA_ANALYSIS = "data_analysis"


class AgentConfig(BaseModel):
    """Configuration for an agent."""

    id: str
    name: str
    role: AgentRole
    description: str
    llm_config: LLMModelConfig
    system_prompt: str
    capabilities: List[AgentCapability] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    max_consecutive_auto_reply: int = 10
    max_retries: int = 3
    timeout_seconds: int = 300
    termination_keywords: List[str] = Field(
        default_factory=lambda: ["TERMINATE", "TASK_COMPLETE"]
    )


class Agent(BaseModel):
    """Complete agent representation including runtime state."""

    config: AgentConfig
    status: AgentStatus = AgentStatus.IDLE
    current_task_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    error_count: int = 0
    total_tasks_completed: int = 0
    task_history: List[str] = Field(default_factory=list)

    def get_agent_description(self) -> str:
        """Get a description of the agent for display."""
        return f"{self.config.name} ({self.config.role}): {self.config.description}"


class AgentTeam(BaseModel):
    """A team of agents working together on tasks."""

    id: str
    name: str
    manager_agent_id: str  # The ID of the coordinating agent
    member_agent_ids: List[str]  # IDs of team member agents
    created_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = True
    description: Optional[str] = None


class LearningMode(str, Enum):
    """Learning modes that affect how LUCA communicates with the user."""

    NOOB = "noob"  # Detailed explanations, step-by-step guidance
    PRO = "pro"  # Concise responses focused on execution
    GURU = "guru"  # Deep technical details and rationale
