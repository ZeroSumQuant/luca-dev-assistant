"""Test configuration for LUCA Dev Assistant.

This file configures pytest with:
1. Environment variables for testing mode
2. Multiprocessing configuration
3. AutoGen-specific test settings
4. AsyncIO configuration
"""

import multiprocessing as mp
import os

import pytest


def pytest_configure(config):
    """Set up environment for tests, with special handling for CI.

    This ensures:
    - LUCA_TESTING is always set to "1" during tests
    - LUCA_SKIP_ASYNC is set to "1" to avoid async complexity in basic tests
    - Multiprocessing uses "spawn" method for better compatibility
    - Additional CI-specific configurations are applied when in GitHub Actions
    - AsyncIO default fixture loop scope is set to function
    """
    # Always set testing mode
    os.environ["LUCA_TESTING"] = "1"
    os.environ["LUCA_SKIP_ASYNC"] = "1"

    # Set asyncio_mode in the config
    config.option.asyncio_mode = "strict"

    # Set the default fixture loop scope
    setattr(config.option, "asyncio_default_fixture_loop_scope", "function")

    # Set multiprocessing start method to "spawn" - more reliable in test environments
    try:
        mp.set_start_method("spawn", force=True)
    except RuntimeError:
        # It may have already been set, which is fine
        pass

    # Add CI-specific configurations
    if os.environ.get("CI") == "true":
        # CI-specific settings could be added here
        print("CI environment detected - applying special test configurations")

    # Register the autogen_mock marker
    config.addinivalue_line(
        "markers",
        "autogen_mock: run this test with AutoGen global mock mode enabled",
    )


def pytest_collection_modifyitems(config, items):
    """Configure AutoGen mocking based on test markers.

    This runs early during collection to ensure AutoGen sees the correct
    environment state before importing modules.
    """
    # Check if we're running autogen_mock tests
    markexpr = config.getoption("-m")

    if markexpr and "autogen_mock" in markexpr:
        # Running specifically autogen_mock tests - enable mocking
        for item in items:
            if "autogen_mock" in item.keywords:
                os.environ["AUTOGEN_USE_MOCK_RESPONSE"] = "1"
                print(f"Enabled AutoGen mocking for {item.nodeid}")
                break
    else:
        # Normal run or explicitly excluding autogen_mock - ensure mocking is off
        os.environ.pop("AUTOGEN_USE_MOCK_RESPONSE", None)


@pytest.fixture(scope="session")
def resource_fixture():
    """Example fixture that properly acquires and cleans up resources.

    This pattern ensures cleanup happens even if tests fail.
    """
    # Setup
    resource = "test_resource"
    yield resource

    # Cleanup - this always runs, even if tests fail
    print(f"Cleaning up test resource: {resource}")
