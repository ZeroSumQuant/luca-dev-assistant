"""Additional tests to improve coverage for error handler module."""

import logging
import unittest.mock as mock

import pytest

from luca_core.error.handler import ErrorHandler, error_handler
from luca_core.schemas.error import (
    ErrorCategory,
    ErrorPayload,
    ErrorSeverity,
)


class TestErrorHandlerCoverage:
    """Test error handler edge cases for coverage."""

    def setup_method(self):
        """Set up test error handler."""
        self.handler = ErrorHandler()

    def test_handle_error_with_failing_handler(self):
        """Test handle_error when the registered handler raises an exception."""

        # Register a handler that raises an exception
        def failing_handler(error):
            raise RuntimeError("Handler failed")

        self.handler.register_handler(ErrorCategory.SYSTEM_ERROR, failing_handler)

        # Create an error
        error = ErrorPayload(
            error_code="TEST001",
            message="Test error",
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            context={},
        )

        # Mock logger to capture error message
        with mock.patch("luca_core.error.handler.logger") as mock_logger:
            # This should not raise, but log the handler error
            self.handler.handle_error(error)

            # Verify the handler error was logged
            mock_logger.error.assert_any_call(
                f"Error in error handler for {error.category}: Handler failed"
            )

    def test_handle_error_with_telemetry_disabled(self):
        """Test handle_error with telemetry disabled."""
        # Disable telemetry
        self.handler.enable_telemetry(False)

        # Create an error
        error = ErrorPayload(
            error_code="TEST002",
            message="Test error",
            category=ErrorCategory.USER_ERROR,
            severity=ErrorSeverity.WARNING,
            context={},
        )

        # Mock _send_telemetry to verify it's not called
        with mock.patch.object(self.handler, "_send_telemetry") as mock_telemetry:
            self.handler.handle_error(error)

            # Telemetry should not be called when disabled
            mock_telemetry.assert_not_called()

    def test_handle_error_no_registered_handler(self):
        """Test handle_error when no handler is registered for the category."""
        # Create an error with a category that has no handler
        error = ErrorPayload(
            error_code="TEST003",
            message="Test error",
            category=ErrorCategory.AUTH_ERROR,
            severity=ErrorSeverity.ERROR,
            context={},
        )

        # Mock logger to verify error is logged
        with mock.patch("luca_core.error.handler.logger") as mock_logger:
            self.handler.handle_error(error)

            # Error should be logged at ERROR level
            mock_logger.error.assert_called_once()

    def test_handle_error_critical_severity(self):
        """Test handle_error with critical severity."""
        error = ErrorPayload(
            error_code="TEST005",
            message="Critical error",
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.CRITICAL,
            context={},
        )

        # Mock logger to verify critical is logged
        with mock.patch("luca_core.error.handler.logger") as mock_logger:
            self.handler.handle_error(error)

            # Critical should be logged
            mock_logger.critical.assert_called_once()

    def test_handle_error_warning_severity(self):
        """Test handle_error with warning severity."""
        error = ErrorPayload(
            error_code="TEST006",
            message="Warning message",
            category=ErrorCategory.USER_ERROR,
            severity=ErrorSeverity.WARNING,
            context={},
        )

        # Mock logger to verify warning is logged
        with mock.patch("luca_core.error.handler.logger") as mock_logger:
            self.handler.handle_error(error)

            # Warning should be logged
            mock_logger.warning.assert_called_once()

    def test_handle_error_info_severity(self):
        """Test handle_error with info severity."""
        error = ErrorPayload(
            error_code="TEST007",
            message="Info message",
            category=ErrorCategory.USER_ERROR,
            severity=ErrorSeverity.INFO,
            context={},
        )

        # Mock logger to verify info is logged
        with mock.patch("luca_core.error.handler.logger") as mock_logger:
            self.handler.handle_error(error)

            # Info should be logged
            mock_logger.info.assert_called_once()

    def test_enable_telemetry(self):
        """Test enable_telemetry method."""
        # Initially enabled by default
        assert self.handler.telemetry_enabled is True

        # Disable telemetry
        self.handler.enable_telemetry(False)
        assert self.handler.telemetry_enabled is False

        # Re-enable telemetry
        self.handler.enable_telemetry(True)
        assert self.handler.telemetry_enabled is True

        # Enable with default parameter
        self.handler.enable_telemetry()
        assert self.handler.telemetry_enabled is True

    def test_global_error_handler_instance(self):
        """Test that global error_handler is properly initialized."""
        assert error_handler is not None
        assert isinstance(error_handler, ErrorHandler)
        assert error_handler.telemetry_enabled is True

    @mock.patch("luca_core.error.handler.logger")
    def test_send_telemetry_placeholder(self, mock_logger):
        """Test _send_telemetry placeholder method."""
        error = ErrorPayload(
            error_code="TEST004",
            message="Test error",
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.INFO,
            context={},
        )

        # Call the placeholder method directly
        self.handler._send_telemetry(error)

        # It should do nothing (no logs, no exceptions)
        mock_logger.assert_not_called()
