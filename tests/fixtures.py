"""Test fixtures for managing AutoGen mock behavior."""

import os

import pytest


@pytest.fixture(scope="function")
def autogen_mode(request, monkeypatch):
    """
    Fixture to control AutoGen mock behavior in tests.

    Usage:
        @pytest.mark.parametrize("autogen_mode", [True, False], indirect=True)
        def test_something(autogen_mode):
            # Test runs with both mocked and unmocked AutoGen

    Can also be used directly:
        def test_something(autogen_mode):
            autogen_mode.set_mock(False)  # Disable mocking for this test
    """

    class AutoGenMode:
        def __init__(self, monkeypatch):
            self.monkeypatch = monkeypatch
            self.original_values = {}

        def set_mock(self, enabled):
            """Enable or disable AutoGen mocking."""
            if enabled:
                self.monkeypatch.setenv("AUTOGEN_USE_MOCK_RESPONSE", "1")
            else:
                self.monkeypatch.delenv("AUTOGEN_USE_MOCK_RESPONSE", raising=False)

        def disable_ci_mock(self):
            """Disable CI-specific mocking behavior."""
            self.monkeypatch.delenv("CI", raising=False)
            self.monkeypatch.delenv("AUTOGEN_USE_MOCK_RESPONSE", raising=False)

    mode = AutoGenMode(monkeypatch)

    # Handle parametrization
    if hasattr(request, "param"):
        mode.set_mock(request.param)

    yield mode

    # Cleanup is automatic with monkeypatch


@pytest.fixture(scope="function")
def no_autogen_mock(monkeypatch):
    """
    Fixture that completely disables AutoGen mocking for a test.

    Usage:
        def test_real_execution(no_autogen_mock):
            # This test will always use real AutoGen behavior
    """
    monkeypatch.delenv("AUTOGEN_USE_MOCK_RESPONSE", raising=False)
    monkeypatch.delenv("CI", raising=False)
    yield
