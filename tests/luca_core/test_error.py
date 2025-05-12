"""Tests for the ErrorPayload schema and error handling utilities."""

import os
import sys

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import pytest
from pydantic import ValidationError

from luca_core.schemas.error import (ErrorCategory, ErrorCode, ErrorPayload,
                                     ErrorSeverity, create_system_error,
                                     create_timeout_error, create_user_error)


def test_error_payload_creation():
    """Test creation of an ErrorPayload instance."""
    error = ErrorPayload(
        category=ErrorCategory.USER_ERROR,
        severity=ErrorSeverity.WARNING,
        message="Test error message",
        context={"test_key": "test_value"},
        recovery_hint="Try this instead",
    )

    assert error.category == ErrorCategory.USER_ERROR
    assert error.severity == ErrorSeverity.WARNING
    assert error.message == "Test error message"
    assert error.context == {"test_key": "test_value"}
    assert error.recovery_hint == "Try this instead"


def test_error_payload_from_exception():
    """Test creating an ErrorPayload from an exception."""
    exception = ValueError("Invalid value")
    error = ErrorPayload.from_exception(exception)

    assert error.category == ErrorCategory.SYSTEM_ERROR
    assert error.severity == ErrorSeverity.ERROR
    assert error.message == "Invalid value"
    assert error.context["exception_type"] == "ValueError"


def test_error_payload_get_user_message():
    """Test getting a user-friendly error message."""
    # Without recovery hint
    error1 = ErrorPayload(
        category=ErrorCategory.SYSTEM_ERROR,
        severity=ErrorSeverity.ERROR,
        message="System failure",
    )
    assert error1.get_user_message() == "System failure"

    # With recovery hint
    error2 = ErrorPayload(
        category=ErrorCategory.SYSTEM_ERROR,
        severity=ErrorSeverity.ERROR,
        message="System failure",
        recovery_hint="Try restarting the application",
    )
    assert (
        error2.get_user_message() == "System failure - Try restarting the application"
    )


def test_create_user_error():
    """Test the create_user_error utility function."""
    error = create_user_error("Invalid input", "Please check your input and try again")

    assert error.category == ErrorCategory.USER_ERROR
    assert error.severity == ErrorSeverity.ERROR
    assert error.message == "Invalid input"
    assert error.recovery_hint == "Please check your input and try again"


def test_create_system_error():
    """Test the create_system_error utility function."""
    error = create_system_error("Database connection failed", {"db_host": "localhost"})

    assert error.category == ErrorCategory.SYSTEM_ERROR
    assert error.severity == ErrorSeverity.ERROR
    assert error.message == "Database connection failed"
    assert error.context == {"db_host": "localhost"}


def test_create_timeout_error():
    """Test the create_timeout_error utility function."""
    error = create_timeout_error("API call", 30)

    assert error.category == ErrorCategory.TIMEOUT_ERROR
    assert error.severity == ErrorSeverity.ERROR
    assert error.message == "Operation 'API call' timed out after 30 seconds"
    assert "Try again with a longer timeout" in error.recovery_hint
