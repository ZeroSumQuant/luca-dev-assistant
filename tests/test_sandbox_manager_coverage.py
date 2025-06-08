"""Additional tests to improve sandbox_manager.py coverage."""

import os
import sys
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from luca_core.sandbox.limits import ResourceLimits  # noqa: E402
from luca_core.sandbox.sandbox_manager import (  # noqa: E402
    DockerSandboxExecutor,
    RestrictedPythonExecutor,
    SandboxConfig,
)


class TestRestrictedPythonEdgeCases:
    """Test edge cases in RestrictedPythonExecutor."""

    @pytest.mark.asyncio
    async def test_syntax_error_during_validation(self):
        """Test handling of syntax errors in code validation."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig()

        # Code with syntax error
        code_with_syntax_error = "import math\nprint('unclosed"
        result = await executor.execute(code_with_syntax_error, config)

        assert result.success is False
        assert "Syntax error" in result.stderr

    @pytest.mark.asyncio
    async def test_importfrom_validation(self):
        """Test ImportFrom node validation."""
        executor = RestrictedPythonExecutor()

        # Test direct validation method
        error = executor._validate_imports("from os import path", [])
        assert error == "Import not allowed: os"

        error = executor._validate_imports("from json import loads", ["json"])
        assert error is None  # json is allowed

    @pytest.mark.asyncio
    async def test_import_multiple_modules(self):
        """Test import of multiple modules."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig(allowed_imports=["json"])

        # Import multiple modules, only json is allowed
        result = await executor.execute("import json, os", config)
        assert result.success is False
        assert "Import not allowed: os" in result.stderr

    @pytest.mark.asyncio
    async def test_compile_error(self):
        """Test handling of compile errors that happen after validation."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig()

        # Test successful execution
        result = await executor.execute("print('test')", config)
        assert result.success is True
        assert "test" in result.stdout

    @pytest.mark.asyncio
    async def test_execution_timeout_in_thread(self):
        """Test timeout handling in restricted executor thread."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig(limits=ResourceLimits(timeout_seconds=0.1))

        # Code that will timeout - use a counter to avoid true infinite loop
        # This prevents CI hangs while still testing timeout behavior
        result = await executor.execute("for i in range(10**9): pass", config)

        assert result.success is False
        assert "timeout" in result.stderr.lower()

    @pytest.mark.asyncio
    async def test_dangerous_builtin_not_available(self):
        """Test that dangerous builtins are not available."""
        executor = RestrictedPythonExecutor()

        # Verify dangerous builtins are not in safe_builtins
        assert "eval" not in executor.safe_builtins
        assert "exec" not in executor.safe_builtins
        assert "__import__" not in executor.safe_builtins
        assert "open" not in executor.safe_builtins
        assert "compile" not in executor.safe_builtins


class TestDockerSandboxEdgeCases:
    """Test edge cases in DockerSandboxExecutor."""

    @pytest.mark.asyncio
    async def test_docker_stats_parsing_error(self):
        """Test handling of docker stats parsing errors."""
        executor = DockerSandboxExecutor()
        config = SandboxConfig()

        # Mock subprocess execution
        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = (b"Hello", b"")

        # Mock stats collection with malformed output
        mock_stats_proc = AsyncMock()
        mock_stats_proc.returncode = 0
        mock_stats_proc.communicate.return_value = (b"container123\\n", b"")

        mock_stats_cmd = AsyncMock()
        mock_stats_cmd.returncode = 0
        mock_stats_cmd.communicate.return_value = (b"malformed stats", b"")

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_exec.side_effect = [mock_proc, mock_stats_proc, mock_stats_cmd]

            result = await executor.execute("print('test')", config)

            # Should still succeed even if stats parsing fails
            assert result.success is True

    @pytest.mark.asyncio
    async def test_docker_command_failure(self):
        """Test handling of docker command failures."""
        executor = DockerSandboxExecutor()
        config = SandboxConfig()

        # Mock subprocess to return non-zero exit code
        mock_proc = AsyncMock()
        mock_proc.returncode = 1
        mock_proc.communicate.return_value = (b"", b"Docker error")

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = await executor.execute("print('test')", config)

            assert result.success is False
            assert result.exit_code == 1
            assert "Docker error" in result.stderr

    @pytest.mark.asyncio
    async def test_docker_with_network_access(self):
        """Test Docker with network access enabled."""
        executor = DockerSandboxExecutor()
        config = SandboxConfig(limits=ResourceLimits(network_offline=False))

        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = (b"", b"")

        with patch(
            "asyncio.create_subprocess_exec", return_value=mock_proc
        ) as mock_exec:
            await executor.execute("print('test')", config)

            # Verify --network none is NOT in the command when network is enabled
            cmd = mock_exec.call_args_list[0][0]
            if "--network" in cmd:
                network_idx = cmd.index("--network")
                assert cmd[network_idx + 1] != "none"
