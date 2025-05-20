"""Base test class for tests involving the registry to ensure proper isolation."""

import pytest

from luca_core.registry.registry import ToolRegistry


class RegistryTestCase:
    """Base test class that ensures registry reset before and after each test.

    Any test class that interacts with the ToolRegistry should inherit from this class
    to ensure proper test isolation. It guarantees that the function cache is reset
    before and after each test to avoid any cross-test contamination.
    """

    def setup_method(self):
        """Reset registry function cache before each test."""
        ToolRegistry.reset()

    def teardown_method(self):
        """Reset registry function cache after each test."""
        ToolRegistry.reset()
