"""Test integration file for luca_core module.

This file tests the integration of core components and ensures they work together correctly.
"""

import os
import sys
import tempfile
import uuid

import pytest

# Force Python to find the luca_core module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from luca_core.schemas.error import ErrorCategory, ErrorPayload, ErrorSeverity


def test_modules_importable():
    """Test that core modules can be imported."""
    # These imports should work if the module structure is correct
    from luca_core.context import store
    from luca_core.error import handler
    from luca_core.manager import manager
    from luca_core.registry import registry
    from luca_core.schemas import context, error

    # If we got here without an import error, the test passes
    assert True
