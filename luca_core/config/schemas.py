"""Configuration schema definitions for LUCA.

This module defines Pydantic models for configuration validation,
matching the structure described in agent-orchestration.md.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from luca_core.schemas.base import AgentRole, DomainType


class StorageType(str, Enum):
    """Storage backend types for ContextStore."""

    SQLITE = "sqlite"
    POSTGRES = "postgres"
    CHROMA = "chroma"


class SecurityLevel(str, Enum):
    """Security levels for sandbox configuration."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SandboxType(str, Enum):
    """Types of sandboxes available."""

    DOCKER = "docker"
    SUBPROCESS = "subprocess"
    LOCAL = "local"


class RetryStrategy(str, Enum):
    """Retry strategies for error handling."""

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"


class EscalationStrategy(str, Enum):
    """Escalation strategies for critical errors."""

    USER_NOTIFICATION = "user_notification"
    RESTART_AGENT = "restart_agent"
    SWITCH_MODEL = "switch_model"
    HUMAN_INTERVENTION = "human_intervention"


class ContextStoreConfig(BaseModel):
    """Configuration for the ContextStore component."""

    type: StorageType = StorageType.SQLITE
    path: Path = Path("./data/context.db")
    backup_interval: int = Field(
        default=300, ge=0, description="Backup interval in seconds"
    )
    connection_params: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("path", mode="before")
    @classmethod
    def validate_path(cls, v: Union[str, Path]) -> Path:
        """Convert string paths to Path objects."""
        return Path(v) if isinstance(v, str) else v


class ToolRegistryConfig(BaseModel):
    """Configuration for the ToolRegistry component."""

    default_scope: str = "/workspace/luca/**"
    version_check: bool = True
    allowed_tools: List[str] = Field(default_factory=list)
    blocked_tools: List[str] = Field(default_factory=list)


class ErrorSchemaConfig(BaseModel):
    """Configuration for error handling schema."""

    levels: List[str] = Field(
        default_factory=lambda: ["info", "warning", "error", "critical"]
    )
    telemetry_enabled: bool = True
    error_retention_days: int = Field(default=30, ge=1)


class ComponentConfig(BaseModel):
    """Configuration for core components."""

    context_store: ContextStoreConfig = Field(default_factory=ContextStoreConfig)
    tool_registry: ToolRegistryConfig = Field(default_factory=ToolRegistryConfig)
    error_schema: ErrorSchemaConfig = Field(default_factory=ErrorSchemaConfig)


class SandboxConfig(BaseModel):
    """Configuration for sandbox execution."""

    allowed_paths: List[str] = Field(default_factory=lambda: ["/workspace/luca/**"])
    execution_timeout: int = Field(default=60, ge=1, description="Timeout in seconds")
    memory_limit: Optional[str] = None  # e.g., "2g"
    cpu_limit: Optional[float] = None  # e.g., 2.0
    network_enabled: bool = True
    security_level: SecurityLevel = SecurityLevel.MEDIUM


class AgentConfig(BaseModel):
    """Configuration for an individual agent."""

    name: str
    role: Union[AgentRole, str]
    description: str
    model: str = "gpt-4o"
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    system_prompt: str
    max_retries: int = Field(default=3, ge=0)
    timeout_seconds: int = Field(default=300, ge=1)
    capabilities: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    sandbox: Optional[SandboxConfig] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Union[AgentRole, str]) -> str:
        """Convert AgentRole enum to string if needed."""
        return v.value if isinstance(v, AgentRole) else v


class LucaConfig(AgentConfig):
    """Configuration for the main LUCA manager agent."""

    name: str = "Luca"
    role: Union[AgentRole, str] = AgentRole.MANAGER
    description: str = "Main orchestration agent that coordinates all tasks"
    system_prompt: str = "You are Luca, the AutoGen development assistant manager."
    specialists: Dict[str, AgentConfig] = Field(default_factory=dict)


class DomainSpecificSettings(BaseModel):
    """Domain-specific settings for an agent."""

    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    additional_tools: List[str] = Field(default_factory=list)


class DomainConfig(BaseModel):
    """Configuration for a specific domain."""

    description: str
    active_specialists: List[str]
    specialist_settings: Dict[str, DomainSpecificSettings] = Field(default_factory=dict)
    default_tools: List[str] = Field(default_factory=list)


class RetryConfig(BaseModel):
    """Configuration for retry behavior."""

    max_retries: int = Field(default=3, ge=0)
    backoff_factor: float = Field(default=1.5, ge=1.0)
    retry_statuses: List[str] = Field(
        default_factory=lambda: ["timeout", "temporary_failure"]
    )
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL


class ErrorHandlingConfig(BaseModel):
    """Configuration for error handling strategies."""

    default: RetryConfig = Field(default_factory=RetryConfig)
    critical: Dict[str, Any] = Field(
        default_factory=lambda: {
            "escalation_path": "user_notification",
            "recovery_strategies": [
                "restart_agent",
                "switch_model",
                "human_intervention",
            ],
        }
    )
    error_specific: Dict[str, RetryConfig] = Field(default_factory=dict)


class ConfigSchema(BaseModel):
    """Complete configuration schema for LUCA."""

    components: ComponentConfig = Field(default_factory=ComponentConfig)
    agents: LucaConfig = Field(default_factory=LucaConfig)
    domains: Dict[str, DomainConfig] = Field(default_factory=dict)
    error_handling: ErrorHandlingConfig = Field(default_factory=ErrorHandlingConfig)

    # Global settings
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    api_keys: Dict[str, str] = Field(default_factory=dict)
    environment: Literal["development", "staging", "production"] = "development"

    @model_validator(mode="after")
    def validate_domains(self) -> "ConfigSchema":
        """Ensure standard domains are present if not specified."""
        standard_domains = {
            DomainType.GENERAL.value,
            DomainType.WEB.value,
            DomainType.DATA_SCIENCE.value,
            DomainType.QUANTITATIVE_FINANCE.value,
        }

        # Add default configurations for missing standard domains
        for domain in standard_domains:
            if domain not in self.domains:
                if domain == DomainType.GENERAL.value:
                    self.domains[domain] = DomainConfig(
                        description="General-purpose development",
                        active_specialists=["coder", "tester", "doc_writer"],
                    )
                elif domain == DomainType.QUANTITATIVE_FINANCE.value:
                    self.domains[domain] = DomainConfig(
                        description="QuantConnect development",
                        active_specialists=["coder", "tester", "analyst"],
                    )
                else:
                    self.domains[domain] = DomainConfig(
                        description=f"{domain.replace('_', ' ').title()} domain",
                        active_specialists=["coder", "tester"],
                    )

        return self

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",  # Strict validation - no extra fields allowed
    }
