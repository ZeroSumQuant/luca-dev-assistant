import os
import subprocess
import sys
from subprocess import PIPE

import pytest


def test_luca_echo():
    """Luca should echo the prompt back (proves FileTool + DockerTool wire-up)."""
    # Set environment variable to prevent UI launch
    env = os.environ.copy()
    env["LUCA_TESTING"] = "1"

    # Debug: Print environment to verify
    print(f"Test environment variable LUCA_TESTING: {env.get('LUCA_TESTING')}")

    # Run the test with the testing environment variable and capture output
    try:
        # Use a more direct subprocess call to ensure environment is passed correctly
        process = subprocess.Popen(
            [sys.executable, "luca.py", "Hello"],
            stdout=PIPE,
            stderr=PIPE,
            text=True,
            env=env,
        )

        # Set a timeout to avoid hanging
        stdout, stderr = process.communicate(timeout=10)

        # Print the output for debugging
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")

        # Verify the results
        assert process.returncode == 0
        assert "hello" in stdout.lower()
        assert (
            "testing mode detected" in stdout.lower()
        ), "Testing mode flag not detected!"
        assert (
            "launching luca dev assistant ui" not in stdout.lower()
        ), "UI was launched despite testing mode!"

    except subprocess.TimeoutExpired:
        process.kill()
        pytest.fail("Process timed out - UI might be attempting to launch")
