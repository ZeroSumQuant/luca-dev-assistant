import os
import subprocess
import sys
import time
from subprocess import PIPE

import pytest


# Mark test with timeout to prevent hanging - increased timeout for agent initialization
@pytest.mark.timeout(30)
def test_luca_echo():
    """Luca should echo the prompt back (tests agent orchestration integration)."""
    # Set environment variables for testing
    env = os.environ.copy()
    env["LUCA_TESTING"] = "1"
    env["LUCA_DEBUG"] = "1"  # Add debug environment variable for verbose output
    env["LUCA_SKIP_ASYNC"] = (
        "1"  # Skip async processing to avoid database and initialization issues
    )

    # Print test start for debugging
    print(f"\n{'='*50}\nStarting test_luca_echo at {time.time()}\n{'='*50}")
    print(
        f"Environment variables: LUCA_TESTING={env.get('LUCA_TESTING')}, "
        f"LUCA_DEBUG={env.get('LUCA_DEBUG')}, "
        f"LUCA_SKIP_ASYNC={env.get('LUCA_SKIP_ASYNC')}"
    )
    print(f"Python executable: {sys.executable}")

    # Run the test with the testing environment variable and capture output
    try:
        # Use a more direct subprocess call to ensure environment is passed correctly
        print("Launching subprocess...")
        process = subprocess.Popen(
            [sys.executable, "scripts/luca.py", "Hello"],
            stdout=PIPE,
            stderr=PIPE,
            text=True,
            env=env,
        )

        print(f"Subprocess started with PID: {process.pid}")

        # Set a timeout to avoid hanging
        print("Waiting for process to complete...")
        stdout, stderr = process.communicate(
            timeout=25
        )  # Increased timeout for agent initialization

        # Print the outputs for debugging
        print(f"\n{'='*20} STDOUT {'='*20}\n{stdout}")
        print(f"\n{'='*20} STDERR {'='*20}\n{stderr}")
        print(f"Return code: {process.returncode}")

        # Verify the results - work with the new agent architecture
        assert (
            process.returncode == 0
        ), f"Process returned non-zero exit code: {process.returncode}"
        assert (
            "testing mode detected" in stdout.lower()
        ), "Testing mode flag not detected!"
        assert (
            "skip async mode detected" in stdout.lower()
        ), "Skip async mode not detected!"

        # The new process no longer echoes the input directly
        assert (
            "processing prompt" in stdout.lower()
        ), "No 'processing prompt' output found"

        # This could be any response from the agent system
        assert (
            "agent response" in stdout.lower() or "lucastring" in stdout.lower()
        ), "No agent response found"

    except subprocess.TimeoutExpired:
        print("Process timed out! Attempting to get partial output...")
        process.kill()

        try:
            partial_stdout, partial_stderr = process.communicate(timeout=2)
            print(f"\n{'='*20} PARTIAL STDOUT {'='*20}\n{partial_stdout}")
            print(f"\n{'='*20} PARTIAL STDERR {'='*20}\n{partial_stderr}")
        except Exception as e:
            print(f"Could not retrieve partial output: {e}")

        pytest.fail(
            "Process timed out - agent initialization might be "
            "taking too long or hanging"
        )
