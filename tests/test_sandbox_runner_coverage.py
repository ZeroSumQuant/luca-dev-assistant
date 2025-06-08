"""Additional tests for sandbox runner coverage."""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from luca_core.sandbox.runner import SandboxRunner, SandboxTimeoutError  # noqa: E402


class TestSandboxRunnerCoverage:
    """Test SandboxRunner edge cases for coverage."""

    def test_sandbox_runner_init(self):
        """Test SandboxRunner initialization."""
        runner = SandboxRunner(image="python:3.11", workdir="/tmp/test", timeout=60)
        assert runner.image == "python:3.11"
        assert runner.workdir == "/tmp/test"
        assert runner.timeout == 60

    def test_sandbox_runner_with_path(self):
        """Test SandboxRunner with Path object."""
        runner = SandboxRunner(
            image="python:3.11", workdir=Path("/tmp/test"), timeout=60
        )
        assert runner.workdir == "/tmp/test"

    def test_sandbox_runner_run_success(self):
        """Test successful command execution."""
        runner = SandboxRunner(image="python:3.11", workdir="/tmp/test", timeout=60)

        # Mock subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello, world!"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = runner.run(["python", "-c", "print('Hello, world!')"])

            # Verify docker command was called correctly
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args[0] == "docker"
            assert args[1] == "run"
            assert "--rm" in args
            assert "--cpus=1" in args
            assert "--memory=2g" in args
            assert "-v" in args
            assert "/tmp/test:/workspace:rw" in args
            assert "python:3.11" in args
            assert "python" in args
            assert "-c" in args
            assert "print('Hello, world!')" in args

            # Verify result
            assert result.returncode == 0
            assert result.stdout == "Hello, world!"

    def test_sandbox_runner_timeout(self):
        """Test timeout handling."""
        runner = SandboxRunner(image="python:3.11", workdir="/tmp/test", timeout=5)

        # Mock subprocess.run to raise TimeoutExpired
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd=["docker", "run", "..."], timeout=5
            )

            with pytest.raises(SandboxTimeoutError) as exc_info:
                runner.run(["python", "-c", "import time; time.sleep(10)"])

            assert "Sandbox execution exceeded 5s" in str(exc_info.value)
            assert "python" in str(exc_info.value)
