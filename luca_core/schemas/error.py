"""Schema definitions for error handling.

This module defines the standardized error payload used across the system
to ensure consistent error handling and reporting.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ErrorCategory(str, Enum):
    """Categories of errors for classification and handling."""

    USER_ERROR = "user_error"  # Error caused by invalid user input
    SYSTEM_ERROR = "system_error"  # Internal system error
    AUTH_ERROR = "auth_error"  # Authentication or authorization error
    RESOURCE_ERROR = "resource_error"  # Error related to resource access
    TIMEOUT_ERROR = "timeout_error"  # Timeout during operation


class ErrorSeverity(str, Enum):
    """Severity levels for errors."""

    INFO = "info"  # Informational message, not a true error
    WARNING = "warning"  # Warning that doesn't prevent operation
    ERROR = "error"  # Error that prevents the specific operation
    CRITICAL = "critical"  # Critical error that affects system stability


class ErrorPayload(BaseModel):
    """Standardized error payload format used throughout the system."""

    schema_version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    error_code: str = "GENERIC_ERROR"
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    remediation: Optional[str] = None
    context_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    recovery_hint: Optional[str] = None  # Deprecated, use remediation instead

    def get_user_message(self) -> str:
        """Return a user-friendly version of the error message."""
        base_message = self.message

        if self.remediation:
            return f"{base_message} - {self.remediation}"
        elif self.recovery_hint:  # Fallback for deprecated field
            return f"{base_message} - {self.recovery_hint}"
        return base_message

    @classmethod
    def from_exception(
        cls,
        exception: Exception,
        category: ErrorCategory = ErrorCategory.SYSTEM_ERROR,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        error_code: str = "UNKNOWN_ERROR",
    ) -> "ErrorPayload":
        """Create an ErrorPayload from an exception."""
        return cls(
            error_code=error_code,
            category=category,
            severity=severity,
            message=str(exception),
            context={"exception_type": type(exception).__name__},
        )


class ErrorCode(str, Enum):
    """Standardized error codes for common error scenarios."""

    # General errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # Authentication errors
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    SESSION_EXPIRED = "SESSION_EXPIRED"

    # Resource errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"

    # System errors
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DEPENDENCY_FAILED = "DEPENDENCY_FAILED"

    # Timeouts
    OPERATION_TIMEOUT = "OPERATION_TIMEOUT"
    API_TIMEOUT = "API_TIMEOUT"


# Error handling utilities
def create_user_error(
    message: str,
    recovery_hint: Optional[str] = None,
    error_code: str = "VALIDATION_ERROR",
    remediation: Optional[str] = None,
) -> ErrorPayload:
    """Create a user error payload."""
    # Use recovery_hint as remediation for backward compatibility
    final_remediation = remediation or recovery_hint
    return ErrorPayload(
        error_code=error_code,
        category=ErrorCategory.USER_ERROR,
        severity=ErrorSeverity.ERROR,
        message=message,
        remediation=final_remediation,
    )


def create_system_error(
    message: str,
    context: Optional[Dict[str, Any]] = None,
    error_code: str = "UNKNOWN_ERROR",
) -> ErrorPayload:
    """Create a system error payload."""
    return ErrorPayload(
        error_code=error_code,
        category=ErrorCategory.SYSTEM_ERROR,
        severity=ErrorSeverity.ERROR,
        message=message,
        context=context or {},
    )


def create_timeout_error(operation: str, timeout_seconds: int) -> ErrorPayload:
    """Create a timeout error payload."""
    return ErrorPayload(
        error_code="OPERATION_TIMEOUT",
        category=ErrorCategory.TIMEOUT_ERROR,
        severity=ErrorSeverity.ERROR,
        message=f"Operation '{operation}' timed out after {timeout_seconds} seconds",  # noqa: E501
        remediation="Try again with a longer timeout or simplify the request",
    )
