"""Basic smoke tests for the LUCA Dev Assistant."""

import os
import subprocess
import sys

import pytest


@pytest.mark.timeout(10)  # Set explicit timeout for this test
def test_luca_cli_runs():
    """Ensure luca.py launches and exits cleanly with testing mode enabled."""
    # Set environment variable to prevent UI launch
    env = os.environ.copy()
    env["LUCA_TESTING"] = "1"
    
    # Run luca.py with testing environment
    result = subprocess.run(
        [sys.executable, "luca.py"],
        capture_output=True,
        text=True,
        env=env,
        timeout=5  # Add explicit subprocess timeout as well
    )
    
    # Verify results
    assert result.returncode == 0
    assert "testing mode detected" in result.stdout.lower()
    assert "launching luca dev assistant ui" not in result.stdout.lower()
