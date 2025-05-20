"""Tests for the sandbox runner module."""

import subprocess
import unittest.mock as mock
from pathlib import Path

import pytest

from luca_core.sandbox.runner import SandboxRunner, SandboxTimeoutError


class TestSandboxRunner:
    """Test suite for sandbox runner functionality."""

    def test_sandbox_runner_init(self):
        """Test SandboxRunner initialization."""
        runner = SandboxRunner("test-image", "/test/dir", timeout=600)

        assert runner.image == "test-image"
        assert runner.workdir == "/test/dir"
        assert runner.timeout == 600

    def test_sandbox_runner_init_with_path(self):
        """Test SandboxRunner initialization with Path object."""
        test_path = Path("/test/dir")
        runner = SandboxRunner("test-image", test_path)

        assert runner.image == "test-image"
        assert runner.workdir == "/test/dir"
        assert runner.timeout == 300  # Default timeout

    @mock.patch("subprocess.run")
    def test_run_success(self, mock_run):
        """Test successful command execution."""
        # Setup mock
        mock_result = subprocess.CompletedProcess(
            args=["echo", "test"], returncode=0, stdout="test\n", stderr=""
        )
        mock_run.return_value = mock_result

        # Create runner and execute
        runner = SandboxRunner("test-image", "/workspace")
        result = runner.run(["echo", "test"])

        # Verify
        assert result.returncode == 0
        assert result.stdout == "test\n"

        # Check that subprocess.run was called correctly
        mock_run.assert_called_once_with(
            [
                "docker",
                "run",
                "--rm",
                "--cpus=1",
                "--memory=2g",
                "-v",
                "/workspace:/workspace:rw",
                "test-image",
                "echo",
                "test",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

    @mock.patch("subprocess.run")
    def test_run_timeout(self, mock_run):
        """Test command execution timeout."""
        # Setup mock to raise TimeoutExpired
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=["docker", "run"], timeout=300
        )

        # Create runner and execute
        runner = SandboxRunner("test-image", "/workspace")

        # Should raise SandboxTimeoutError
        with pytest.raises(SandboxTimeoutError) as exc_info:
            runner.run(["sleep", "400"])

        assert "Sandbox execution exceeded 300s" in str(exc_info.value)

    @mock.patch("subprocess.run")
    def test_run_with_custom_timeout(self, mock_run):
        """Test command execution with custom timeout."""
        # Setup mock
        mock_result = subprocess.CompletedProcess(
            args=["ls"], returncode=0, stdout="file.txt\n", stderr=""
        )
        mock_run.return_value = mock_result

        # Create runner with custom timeout
        runner = SandboxRunner("test-image", "/workspace", timeout=60)
        result = runner.run(["ls"])

        # Verify timeout was used
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args.kwargs["timeout"] == 60

    def test_sandbox_timeout_error(self):
        """Test SandboxTimeoutError exception."""
        error = SandboxTimeoutError("Test timeout")
        assert isinstance(error, RuntimeError)
        assert str(error) == "Test timeout"

    @mock.patch("subprocess.run")
    def test_run_with_complex_command(self, mock_run):
        """Test running complex command with multiple arguments."""
        # Setup mock
        mock_result = subprocess.CompletedProcess(
            args=["python", "-c", "print('hello')"],
            returncode=0,
            stdout="hello\n",
            stderr="",
        )
        mock_run.return_value = mock_result

        # Create runner and execute
        runner = SandboxRunner("python:3.13", "/code")
        result = runner.run(["python", "-c", "print('hello')"])

        # Verify the command was constructed correctly
        expected_cmd = [
            "docker",
            "run",
            "--rm",
            "--cpus=1",
            "--memory=2g",
            "-v",
            "/code:/workspace:rw",
            "python:3.13",
            "python",
            "-c",
            "print('hello')",
        ]
        mock_run.assert_called_once_with(
            expected_cmd, capture_output=True, text=True, timeout=300
        )
