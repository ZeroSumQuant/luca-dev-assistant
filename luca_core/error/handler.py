"""Error handler implementation.

This module provides utility functions and classes for standardized error
handling across the system using the ErrorPayload schema.
"""

import functools
import logging
import traceback
from typing import Any, Callable, Dict, Optional, TypeVar

from luca_core.schemas import ErrorCategory, ErrorPayload, ErrorSeverity

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ErrorHandler:
    """Error handler for standardized error handling."""

    def __init__(self):
        """Initialize the error handler."""
        self.error_handlers: Dict[ErrorCategory, Callable[[ErrorPayload], None]] = {}
        self.telemetry_enabled = True

    def register_handler(
        self, category: ErrorCategory, handler: Callable[[ErrorPayload], None]
    ) -> None:
        """Register a handler for a specific error category.

        Args:
            category: Error category
            handler: Handler function that takes an ErrorPayload
        """
        self.error_handlers[category] = handler

    def handle_error(self, error: ErrorPayload) -> None:
        """Handle an error using registered handlers.

        Args:
            error: Error payload to handle
        """
        # Log the error
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(
                f"{error.category}: {error.message}", extra={"context": error.context}
            )
        elif error.severity == ErrorSeverity.ERROR:
            logger.error(
                f"{error.category}: {error.message}", extra={"context": error.context}
            )
        elif error.severity == ErrorSeverity.WARNING:
            logger.warning(
                f"{error.category}: {error.message}", extra={"context": error.context}
            )
        else:
            logger.info(
                f"{error.category}: {error.message}", extra={"context": error.context}
            )

        # Send telemetry if enabled
        if self.telemetry_enabled and error.severity in [
            ErrorSeverity.ERROR,
            ErrorSeverity.CRITICAL,
        ]:
            self._send_telemetry(error)

        # Call category-specific handler if registered
        handler = self.error_handlers.get(error.category)
        if handler:
            try:
                handler(error)
            except Exception as e:
                logger.error(f"Error in error handler for {error.category}: {e}")

    def _send_telemetry(self, error: ErrorPayload) -> None:
        """Send telemetry for an error.

        This is a placeholder for actual telemetry implementation.
        """
        pass  # In a real implementation, this would send telemetry data

    def enable_telemetry(self, enabled: bool = True) -> None:
        """Enable or disable telemetry.

        Args:
            enabled: Whether telemetry should be enabled
        """
        self.telemetry_enabled = enabled


# Create a global error handler instance
error_handler = ErrorHandler()


def handle_exceptions(
    error_category: ErrorCategory = ErrorCategory.SYSTEM_ERROR,
    error_severity: ErrorSeverity = ErrorSeverity.ERROR,
    reraise: bool = False,
    log_traceback: bool = True,
    recovery_hint: Optional[str] = None,
) -> Callable:
    """Decorator to handle exceptions and convert them to ErrorPayload.

    Args:
        error_category: Default error category
        error_severity: Default error severity
        reraise: Whether to reraise the exception after handling
        log_traceback: Whether to log the traceback
        recovery_hint: Optional recovery hint to include in the error

    Returns:
        Decorator function

    Example:
        @handle_exceptions(
            error_category=ErrorCategory.USER_ERROR,
            recovery_hint="Check the file path and try again"
        )
        def read_file(path: str) -> str:
            # Implementation...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Create error context
                context = {
                    "function": func.__name__,
                    "args": str(args) if args else None,
                    "kwargs": str(kwargs) if kwargs else None,
                    "exception_type": type(e).__name__,
                }

                # Log traceback if enabled
                if log_traceback:
                    tb = traceback.format_exc()
                    logger.error(f"Exception in {func.__name__}: {e}\n{tb}")
                    context["traceback"] = tb

                # Create error payload
                error = ErrorPayload(
                    error_code="UNKNOWN_ERROR",
                    category=error_category,
                    severity=error_severity,
                    message=str(e),
                    context=context,
                    recovery_hint=recovery_hint,
                )

                # Handle the error
                error_handler.handle_error(error)

                # Reraise if requested
                if reraise:
                    raise

                # Otherwise, return the error payload
                return error

        return wrapper

    return decorator
