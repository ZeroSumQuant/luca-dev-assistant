"""Tests for the error handler implementation."""

import logging
from unittest.mock import Mock, patch

import pytest

from luca_core.error.handler import ErrorHandler, error_handler, handle_exceptions
from luca_core.schemas import (
    ErrorCategory,
    ErrorPayload,
    ErrorSeverity,
    create_system_error,
    create_user_error,
)


class TestErrorHandler:
    """Test the ErrorHandler class."""

    def test_init(self):
        """Test error handler initialization."""
        handler = ErrorHandler()
        assert handler.error_handlers == {}
        assert handler.telemetry_enabled is True

    def test_register_handler(self):
        """Test registering error handlers."""
        handler = ErrorHandler()
        mock_handler = Mock()

        handler.register_handler(ErrorCategory.SYSTEM_ERROR, mock_handler)
        assert ErrorCategory.SYSTEM_ERROR in handler.error_handlers
        assert handler.error_handlers[ErrorCategory.SYSTEM_ERROR] == mock_handler

    @patch("luca_core.error.handler.logger")
    def test_handle_error_critical(self, mock_logger):
        """Test handling critical errors."""
        handler = ErrorHandler()
        error = ErrorPayload(
            error_code="TEST001",
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.CRITICAL,
            message="Test critical error",
            context={"test": "data"},
        )

        handler.handle_error(error)
        mock_logger.critical.assert_called_once_with(
            "ErrorCategory.SYSTEM_ERROR: Test critical error",
            extra={"context": {"test": "data"}},
        )

    @patch("luca_core.error.handler.logger")
    def test_handle_error_error(self, mock_logger):
        """Test handling error level errors."""
        handler = ErrorHandler()
        error = ErrorPayload(
            error_code="TEST002",
            category=ErrorCategory.USER_ERROR,
            severity=ErrorSeverity.ERROR,
            message="Test error",
            context={},
        )

        handler.handle_error(error)
        mock_logger.error.assert_called_once_with(
            "ErrorCategory.USER_ERROR: Test error", extra={"context": {}}
        )

    @patch("luca_core.error.handler.logger")
    def test_handle_error_warning(self, mock_logger):
        """Test handling warnings."""
        handler = ErrorHandler()
        error = ErrorPayload(
            error_code="TEST003",
            category=ErrorCategory.AUTH_ERROR,
            severity=ErrorSeverity.WARNING,
            message="Test warning",
            context={"user": "test"},
        )

        handler.handle_error(error)
        mock_logger.warning.assert_called_once_with(
            "ErrorCategory.AUTH_ERROR: Test warning",
            extra={"context": {"user": "test"}},
        )

    @patch("luca_core.error.handler.logger")
    def test_handle_error_info(self, mock_logger):
        """Test handling info level errors."""
        handler = ErrorHandler()
        error = ErrorPayload(
            error_code="TEST004",
            category=ErrorCategory.USER_ERROR,
            severity=ErrorSeverity.INFO,
            message="Test info",
            context={},
        )

        handler.handle_error(error)
        mock_logger.info.assert_called_once_with(
            "ErrorCategory.USER_ERROR: Test info", extra={"context": {}}
        )

    def test_handle_error_with_registered_handler(self):
        """Test handling errors with registered handlers."""
        handler = ErrorHandler()
        mock_handler = Mock()
        handler.register_handler(ErrorCategory.SYSTEM_ERROR, mock_handler)

        error = ErrorPayload(
            error_code="TEST005",
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            message="Test error for handler",
            context={},
        )

        with patch("luca_core.error.handler.logger"):
            handler.handle_error(error)

        mock_handler.assert_called_once_with(error)

    @patch("luca_core.error.handler.logger")
    def test_handle_error_with_telemetry_disabled(self, mock_logger):
        """Test handling errors with telemetry disabled."""
        handler = ErrorHandler()
        handler.telemetry_enabled = False

        error = ErrorPayload(
            error_code="TEST006",
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            message="Test error",
            context={},
        )

        handler.handle_error(error)
        # Should still log even with telemetry disabled
        mock_logger.error.assert_called_once()


def test_handle_exceptions_decorator():
    """Test the handle_exceptions decorator."""

    @handle_exceptions(
        error_severity=ErrorSeverity.WARNING,
        error_category=ErrorCategory.USER_ERROR,
        recovery_hint="Custom recovery hint",
    )
    def failing_function():
        """Function that raises an exception."""
        raise ValueError("Test exception")

    @handle_exceptions()
    def successful_function():
        """Function that succeeds."""
        return "success"

    # Test successful function
    assert successful_function() == "success"

    # Test failing function
    with patch("luca_core.error.handler.error_handler") as mock_handler:
        result = failing_function()
        assert isinstance(result, ErrorPayload)
        assert result.message == "Test exception"
        assert result.severity == ErrorSeverity.WARNING
        assert result.category == ErrorCategory.USER_ERROR
        assert result.recovery_hint == "Custom recovery hint"

        # Check that error handler was called
        mock_handler.handle_error.assert_called_once()
        error_payload = mock_handler.handle_error.call_args[0][0]
        assert error_payload == result


def test_handle_exceptions_decorator_with_reraise():
    """Test the handle_exceptions decorator with reraise option."""

    @handle_exceptions(reraise=True)
    def failing_function():
        """Function that raises an exception."""
        raise ValueError("Test exception")

    with patch("luca_core.error.handler.error_handler"):
        with pytest.raises(ValueError, match="Test exception"):
            failing_function()


def test_handle_exceptions_decorator_returns_error_payload():
    """Test the handle_exceptions decorator returns ErrorPayload on error."""

    @handle_exceptions()
    def failing_function():
        """Function that raises an exception."""
        raise ValueError("Test exception")

    with patch("luca_core.error.handler.error_handler"):
        result = failing_function()
        assert isinstance(result, ErrorPayload)
        assert result.message == "Test exception"
        assert result.category == ErrorCategory.SYSTEM_ERROR  # Default
        assert result.severity == ErrorSeverity.ERROR  # Default


def test_handle_exceptions_decorator_preserves_function_attributes():
    """Test that handle_exceptions decorator preserves function attributes."""

    @handle_exceptions()
    def documented_function():
        """This is a documented function."""
        return "result"

    assert documented_function.__name__ == "documented_function"
    assert documented_function.__doc__ == "This is a documented function."


def test_global_error_handler():
    """Test the global error handler instance."""
    from luca_core.error.handler import error_handler

    assert isinstance(error_handler, ErrorHandler)
    assert error_handler.error_handlers == {}
    assert error_handler.telemetry_enabled is True
