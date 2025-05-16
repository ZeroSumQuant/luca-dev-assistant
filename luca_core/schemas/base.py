"""
Core schema definitions for LUCA's agent orchestration system.

This module contains base schema classes shared across the system.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

# Basic enums and types for use throughout the system


class SeverityLevel(str, Enum):
    """Severity levels for errors and messages."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class CompletionStatus(str, Enum):
    """Completion status for tasks and operations."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"


class DomainType(str, Enum):
    """Domain types for categorizing tasks and tools."""

    GENERAL = "general"
    WEB = "web"
    DATA_SCIENCE = "data_science"
    QUANTITATIVE_FINANCE = "quantitative_finance"


class LearningMode(str, Enum):
    """Learning modes for user interaction."""

    NOOB = "noob"
    PRO = "pro"
    GURU = "guru"


class AgentRole(str, Enum):
    """Role types for agents in the system."""

    MANAGER = "manager"
    DEVELOPER = "developer"
    QA = "qa"
    DOC_WRITER = "doc_writer"
    ANALYST = "analyst"
    CUSTOM = "custom"
