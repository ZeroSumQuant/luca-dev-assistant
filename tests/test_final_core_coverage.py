"""Final tests to achieve 100% coverage for core modules."""

import sys
from unittest.mock import AsyncMock, patch

import pytest

from luca_core.registry.registry import ToolRegistry, tool
from luca_core.sandbox.limits import ResourceLimits
from luca_core.sandbox.sandbox_manager import (
    DockerSandboxExecutor,
    RestrictedPythonExecutor,
    SandboxConfig,
)


class TestRegistryDuplicateRegistration:
    """Test duplicate tool registration."""

    def test_duplicate_function_registration(self):
        """Test that registering the same function twice raises KeyError."""
        # Create a fresh registry
        ToolRegistry()  # This creates the registry singleton

        # Register a function
        @tool(name="test_func", category="test")
        def my_function(x: int) -> int:
            return x * 2

        # Try to register another function with the same name
        with pytest.raises(KeyError) as exc_info:

            @tool(name="test_func2", category="test")
            def my_function(y: int) -> int:  # Same function name  # noqa: F811
                return y * 3

        assert "Function 'my_function' is already registered" in str(exc_info.value)


class TestDockerSandboxEnvironmentVars:
    """Test Docker sandbox with environment variables."""

    @pytest.mark.asyncio
    async def test_docker_with_env_vars(self):
        """Test Docker executor with environment variables."""
        executor = DockerSandboxExecutor()
        config = SandboxConfig(
            env_vars={"CUSTOM_VAR": "test_value", "ANOTHER_VAR": "123"}
        )

        # Mock subprocess execution
        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = (b"Success", b"")

        with patch(
            "asyncio.create_subprocess_exec", return_value=mock_proc
        ) as mock_exec:
            result = await executor.execute("print('test')", config)

            # Check that env vars were added to command
            cmd = mock_exec.call_args_list[0][0]
            assert "-e" in cmd
            assert "CUSTOM_VAR=test_value" in cmd
            assert "ANOTHER_VAR=123" in cmd
            assert result.success is True


class TestRestrictedPythonImportError:
    """Test restricted import functionality."""

    @pytest.mark.asyncio
    async def test_restricted_import_in_allowed_module(self):
        """Test that __import__ works for allowed modules."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig(allowed_imports=["json", "math"])

        code = """
import json
import math
result = math.sqrt(16)
print(f"Result: {result}")
"""
        result = await executor.execute(code, config)

        assert result.success is True
        assert "Result: 4.0" in result.stdout


class TestRestrictedPythonExceptionHandling:
    """Test exception handling in RestrictedPythonExecutor."""

    @pytest.mark.asyncio
    async def test_exception_during_execution(self):
        """Test exception handling during execution."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig()

        # Mock threading.Thread to raise an exception
        with patch("threading.Thread") as mock_thread:
            mock_thread.side_effect = RuntimeError("Thread creation failed")

            result = await executor.execute("print('test')", config)

            assert result.success is False
            assert "Thread creation failed" in result.stderr
            assert result.exit_code == -1


class TestProcessSandboxResourceLimits:
    """Test process sandbox resource limit setting."""

    @pytest.mark.asyncio
    async def test_resource_limit_setting_code_coverage(self):
        """Test to ensure resource limit code is covered."""
        # This is tricky because the resource limits are set in a subprocess
        # We'll create a test that exercises the parent process code paths
        from luca_core.sandbox.sandbox_manager import ProcessSandboxExecutor

        executor = ProcessSandboxExecutor()
        config = SandboxConfig(
            limits=ResourceLimits(
                cpu_cores=0.5,
                memory_mb=256,
                max_processes=10,
                max_open_files=50,
            )
        )

        # The actual resource limit setting happens in the subprocess
        # But we can at least ensure the code paths are exercised
        code = """
import os
print(f"PID: {os.getpid()}")
"""

        # This will create the subprocess and run the set_limits function
        result = await executor.execute(code, config)

        # On non-Windows systems, this should work
        if sys.platform != "win32":
            assert result.success is True
            assert "PID:" in result.stdout
