"""Error package for LUCA Core.

This package provides utilities for standardized error handling
across the system using the ErrorPayload schema.
"""

from luca_core.error.handler import (ErrorHandler, error_handler,
                                     handle_exceptions)

__all__ = [
    "ErrorHandler",
    "error_handler",
    "handle_exceptions",
]
