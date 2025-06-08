"""Test configuration for LUCA Dev Assistant.

This file configures pytest with:
1. Environment variables for testing mode
2. Multiprocessing configuration
3. AutoGen-specific test settings
4. AsyncIO configuration
"""

import asyncio
import multiprocessing as mp
import os
import threading

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


@pytest.fixture(autouse=True)
def ensure_clean_async_state():
    """Ensure clean async state after each test to prevent CI hangs.

    Based on research into pytest-asyncio hanging issues, this fixture
    checks for and cleans up:
    - Non-daemon threads that could block process exit
    - Pending asyncio tasks that weren't awaited

    This is critical for CI stability when testing async code that uses
    FunctionTool or similar patterns that may spawn background operations.
    """
    yield

    # Check for non-daemon threads
    non_daemon_threads = []
    for thread in threading.enumerate():
        if thread is not threading.main_thread() and not thread.daemon:
            non_daemon_threads.append(thread)

    if non_daemon_threads:
        thread_info = ", ".join(
            [f"{t.name} (alive={t.is_alive()})" for t in non_daemon_threads]
        )
        # Don't fail immediately - try to diagnose
        print(f"WARNING: Non-daemon threads still running: {thread_info}")

        # Try to stop threads if they're from our sandbox tests
        for thread in non_daemon_threads:
            if hasattr(thread, "_target") and thread._target:
                # Log what the thread was doing
                print(f"Thread {thread.name} target: {thread._target}")
            # Note: We can't forcefully kill threads in Python, but logging helps

    # Check for pending asyncio tasks
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No loop running, which is fine
        return

    try:
        current_task = asyncio.current_task(loop)
    except RuntimeError:
        current_task = None

    pending_tasks = [
        task
        for task in asyncio.all_tasks(loop)
        if not task.done() and task != current_task
    ]
    if pending_tasks:
        # Try to cancel them to prevent hangs
        for task in pending_tasks:
            task.cancel()

        task_info = ", ".join([str(task) for task in pending_tasks[:5]])  # Limit output
        print(
            f"WARNING: Cancelled {len(pending_tasks)} pending async tasks: {task_info}"
        )
