"""
Comprehensive tests for the sandbox manager.
"""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from luca_core.sandbox.sandbox_manager import (  # noqa: E402
    DockerSandboxExecutor,
    ProcessSandboxExecutor,
    RestrictedPythonExecutor,
    SandboxConfig,
    SandboxManager,
    SandboxResult,
    SandboxStrategy,
    get_sandbox_manager,
)


class TestSandboxConfig:
    """Test SandboxConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = SandboxConfig()
        assert config.strategy == SandboxStrategy.DOCKER
        assert config.cpu_limit == 1.0
        assert config.memory_limit_mb == 512
        assert config.timeout_seconds == 30
        assert config.allowed_imports == []
        assert config.allowed_paths == []
        assert config.network_access is False
        assert config.env_vars == {}

    def test_custom_config(self):
        """Test custom configuration values."""
        config = SandboxConfig(
            strategy=SandboxStrategy.PROCESS,
            cpu_limit=2.0,
            memory_limit_mb=1024,
            timeout_seconds=60,
            allowed_imports=["math", "json"],
            allowed_paths=["/tmp"],
            network_access=True,
            env_vars={"FOO": "bar"},
        )
        assert config.strategy == SandboxStrategy.PROCESS
        assert config.cpu_limit == 2.0
        assert config.memory_limit_mb == 1024
        assert config.timeout_seconds == 60
        assert config.allowed_imports == ["math", "json"]
        assert config.allowed_paths == ["/tmp"]
        assert config.network_access is True
        assert config.env_vars == {"FOO": "bar"}


class TestSandboxResult:
    """Test SandboxResult class."""

    def test_success_result(self):
        """Test successful execution result."""
        result = SandboxResult(stdout="Hello", stderr="", exit_code=0)
        assert result.success is True
        assert result.stdout == "Hello"
        assert result.stderr == ""
        assert result.exit_code == 0
        assert result.error is None

    def test_failed_result(self):
        """Test failed execution result."""
        result = SandboxResult(
            stdout="",
            stderr="Error",
            exit_code=1,
            error=Exception("Test error"),
        )
        assert result.success is False
        assert result.exit_code == 1
        assert result.error is not None

    def test_resource_usage(self):
        """Test resource usage tracking."""
        result = SandboxResult(
            resource_usage={
                "execution_time_seconds": 1.5,
                "memory_peak_mb": 100,
            }
        )
        assert result.resource_usage["execution_time_seconds"] == 1.5
        assert result.resource_usage["memory_peak_mb"] == 100


class TestDockerSandboxExecutor:
    """Test Docker sandbox executor."""

    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """Test successful code execution in Docker."""
        executor = DockerSandboxExecutor()
        config = SandboxConfig()

        # Mock subprocess execution
        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = (b"Hello World", b"")

        with patch(
            "asyncio.create_subprocess_exec", return_value=mock_proc
        ) as mock_exec:
            result = await executor.execute("print('Hello World')", config)

            # Check Docker command construction from first call
            assert mock_exec.call_count >= 1
            cmd = mock_exec.call_args_list[0][0]
            assert "docker" in cmd
            assert "run" in cmd
            assert "--rm" in cmd
            assert "--user" in cmd
            assert "1000:1000" in cmd
            assert "--security-opt" in cmd
            assert "no-new-privileges" in cmd
            assert "--cap-drop" in cmd
            assert "ALL" in cmd
            assert "--cpus=1.0" in cmd
            assert "--memory=512m" in cmd
            assert "--pids-limit" in cmd
            assert "64" in cmd
            assert "--read-only" in cmd
            assert "--tmpfs" in cmd

            # Check result
            assert result.success is True
            assert result.stdout == "Hello World"
            assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling in Docker executor."""
        executor = DockerSandboxExecutor()
        config = SandboxConfig(timeout_seconds=1)

        mock_proc = AsyncMock()
        mock_proc.returncode = None
        mock_proc.communicate.side_effect = asyncio.TimeoutError()

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = await executor.execute("import time; time.sleep(10)", config)

            assert result.success is False
            assert "timeout" in result.stderr.lower()
            assert result.exit_code == -1
            mock_proc.kill.assert_called_once()

    @pytest.mark.asyncio
    async def test_network_restriction(self):
        """Test network restriction in Docker."""
        executor = DockerSandboxExecutor()
        config = SandboxConfig(network_access=False)

        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = (b"", b"")

        with patch(
            "asyncio.create_subprocess_exec", return_value=mock_proc
        ) as mock_exec:
            await executor.execute("print('test')", config)

            # Check first call for docker run command
            assert mock_exec.call_count >= 1
            cmd = mock_exec.call_args_list[0][0]
            assert "--network" in cmd
            assert "none" in cmd


class TestProcessSandboxExecutor:
    """Test process sandbox executor."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.name == "nt", reason="Process sandboxing not supported on Windows"
    )
    async def test_successful_execution(self):
        """Test successful code execution in subprocess."""
        executor = ProcessSandboxExecutor()
        config = SandboxConfig()

        result = await executor.execute("print('Hello from subprocess')", config)
        assert result.success is True
        assert "Hello from subprocess" in result.stdout

    @pytest.mark.asyncio
    async def test_windows_platform_check(self):
        """Test Windows platform check."""
        executor = ProcessSandboxExecutor()
        config = SandboxConfig()

        with patch("os.name", "nt"):
            result = await executor.execute("print('test')", config)
            assert result.success is False
            assert "Windows" in result.stderr

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.name == "nt", reason="Process sandboxing not supported on Windows"
    )
    async def test_resource_usage_tracking(self):
        """Test resource usage tracking."""
        executor = ProcessSandboxExecutor()
        config = SandboxConfig()

        result = await executor.execute("print('test')", config)
        assert "execution_time_seconds" in result.resource_usage
        assert "cpu_limit" in result.resource_usage
        assert "memory_limit_mb" in result.resource_usage
        assert result.resource_usage["cpu_limit"] == 1.0
        assert result.resource_usage["memory_limit_mb"] == 512


class TestRestrictedPythonExecutor:
    """Test restricted Python executor."""

    @pytest.mark.asyncio
    async def test_safe_code_execution(self):
        """Test execution of safe code."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig(allowed_imports=["math"])

        result = await executor.execute("print(2 + 2)", config)
        assert result.success is True
        assert "4" in result.stdout

    @pytest.mark.asyncio
    async def test_import_validation(self):
        """Test import validation blocks unauthorized imports."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig(allowed_imports=["math"])

        # Test disallowed import
        result = await executor.execute("import os", config)
        assert result.success is False
        assert "Import not allowed: os" in result.stderr

        # Test allowed import
        result = await executor.execute("import math\nprint(math.pi)", config)
        assert result.success is True
        assert "3.14" in result.stdout

    @pytest.mark.asyncio
    async def test_from_import_validation(self):
        """Test from-import validation."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig(allowed_imports=["json"])

        result = await executor.execute("from os import path", config)
        assert result.success is False
        assert "Import not allowed: os" in result.stderr

    @pytest.mark.asyncio
    async def test_builtin_restrictions(self):
        """Test builtin function restrictions."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig()

        # Test allowed builtin
        result = await executor.execute("print(len([1, 2, 3]))", config)
        assert result.success is True
        assert "3" in result.stdout

        # Dangerous builtins should not be available
        # eval should not be in the safe builtins, so it will raise NameError
        assert "eval" not in executor.safe_builtins

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling in restricted executor."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig(timeout_seconds=1)

        result = await executor.execute("while True: pass", config)
        assert result.success is False
        assert "timeout" in result.stderr.lower()


class TestSandboxManager:
    """Test the main SandboxManager class."""

    @pytest.mark.asyncio
    async def test_docker_strategy_selection(self):
        """Test Docker strategy is selected correctly."""
        manager = SandboxManager()
        config = SandboxConfig(strategy=SandboxStrategy.DOCKER)

        with patch.object(DockerSandboxExecutor, "execute") as mock_execute:
            mock_execute.return_value = SandboxResult(stdout="test")
            await manager.execute("print('test')", config)
            mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_strategy_selection(self):
        """Test process strategy is selected correctly."""
        manager = SandboxManager()
        config = SandboxConfig(strategy=SandboxStrategy.PROCESS)

        with patch.object(ProcessSandboxExecutor, "execute") as mock_execute:
            mock_execute.return_value = SandboxResult(stdout="test")
            await manager.execute("print('test')", config)
            mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_restricted_strategy_selection(self):
        """Test restricted strategy is selected correctly."""
        manager = SandboxManager()
        config = SandboxConfig(strategy=SandboxStrategy.RESTRICTED)

        with patch.object(RestrictedPythonExecutor, "execute") as mock_execute:
            mock_execute.return_value = SandboxResult(stdout="test")
            await manager.execute("print('test')", config)
            mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_none_strategy_blocked(self):
        """Test that 'none' strategy is blocked."""
        manager = SandboxManager()
        config = SandboxConfig(strategy=SandboxStrategy.NONE)

        result = await manager.execute("print('test')", config)
        assert result.success is False
        assert "not allowed" in result.stderr

    @pytest.mark.asyncio
    async def test_default_config(self):
        """Test execution with default config."""
        manager = SandboxManager()

        with patch.object(DockerSandboxExecutor, "execute") as mock_execute:
            mock_execute.return_value = SandboxResult(stdout="default")
            await manager.execute("print('test')")
            mock_execute.assert_called_once()
            # Check default config was used
            _, call_config = mock_execute.call_args[0]
            assert call_config.strategy == SandboxStrategy.DOCKER

    def test_get_recommended_config_untrusted(self):
        """Test recommended config for untrusted code."""
        manager = SandboxManager()
        config = manager.get_recommended_config("untrusted")

        assert config.strategy == SandboxStrategy.DOCKER
        assert config.cpu_limit == 0.5
        assert config.memory_limit_mb == 256
        assert config.timeout_seconds == 10
        assert config.network_access is False

    def test_get_recommended_config_limited(self):
        """Test recommended config for limited trust code."""
        manager = SandboxManager()
        config = manager.get_recommended_config("limited")

        assert config.strategy == SandboxStrategy.PROCESS
        assert config.cpu_limit == 1.0
        assert config.memory_limit_mb == 512
        assert config.timeout_seconds == 30
        assert config.network_access is False

    def test_get_recommended_config_trusted(self):
        """Test recommended config for trusted code."""
        manager = SandboxManager()
        config = manager.get_recommended_config("trusted")

        assert config.strategy == SandboxStrategy.RESTRICTED
        assert config.cpu_limit == 2.0
        assert config.memory_limit_mb == 1024
        assert config.timeout_seconds == 60
        assert config.allowed_imports == ["math", "statistics", "json"]
        assert config.network_access is False

    def test_get_recommended_config_default(self):
        """Test default recommended config for unknown trust level."""
        manager = SandboxManager()
        config = manager.get_recommended_config("unknown")

        # Should default to untrusted
        assert config.strategy == SandboxStrategy.DOCKER
        assert config.cpu_limit == 0.5

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """Test exception handling in manager."""
        manager = SandboxManager()
        config = SandboxConfig(strategy=SandboxStrategy.DOCKER)

        with patch.object(DockerSandboxExecutor, "execute") as mock_execute:
            mock_execute.side_effect = Exception("Test error")
            result = await manager.execute("print('test')", config)

            assert result.success is False
            assert "Sandbox execution failed" in result.stderr
            assert result.exit_code == -1

    @pytest.mark.asyncio
    async def test_docker_resource_metrics(self):
        """Test Docker resource metrics collection."""
        executor = DockerSandboxExecutor()
        config = SandboxConfig()

        # Mock subprocess execution
        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = (b"Hello", b"")

        # Mock stats collection
        mock_stats_proc = AsyncMock()
        mock_stats_proc.returncode = 0
        mock_stats_proc.communicate.return_value = (b"container123\n", b"")

        mock_stats_cmd = AsyncMock()
        mock_stats_cmd.returncode = 0
        mock_stats_cmd.communicate.return_value = (b"15.5%;100MiB / 500MiB", b"")

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            # First call is main docker run, second is ps, third is stats
            mock_exec.side_effect = [mock_proc, mock_stats_proc, mock_stats_cmd]

            result = await executor.execute("print('test')", config)

            assert result.success is True
            assert "cpu_percent" in result.resource_usage
            assert "memory_usage" in result.resource_usage
            assert result.resource_usage["cpu_percent"] == "15.5"
            assert result.resource_usage["memory_usage"] == "100MiB"

    @pytest.mark.asyncio
    async def test_concurrent_execution_thread_safety(self):
        """Test concurrent execution with thread-local managers."""
        import asyncio

        async def run_code(i):
            manager = get_sandbox_manager()
            config = SandboxConfig(strategy=SandboxStrategy.RESTRICTED)
            result = await manager.execute(f"print({i})", config)
            return result.stdout.strip()

        # Run multiple concurrent executions
        results = await asyncio.gather(*(run_code(i) for i in range(5)))

        # Check all executions completed successfully
        assert len(results) == 5
        assert set(results) == {"0", "1", "2", "3", "4"}

    def test_thread_local_factory(self):
        """Test thread-local factory creates separate instances."""
        import threading

        managers = []

        def get_manager():
            managers.append(get_sandbox_manager())

        # Create managers in different threads
        threads = []
        for _ in range(3):
            t = threading.Thread(target=get_manager)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        # Also get one from main thread
        managers.append(get_sandbox_manager())

        # Check that we have 4 managers total
        assert len(managers) == 4

        # Main thread manager should be the same instance
        assert managers[-1] is get_sandbox_manager()

    @pytest.mark.asyncio
    async def test_manager_execute_code_securely(self):
        """Test the manager's execute_code_securely method."""
        from luca_core.manager.manager import LucaManager

        # Create a mock context store
        mock_store = AsyncMock()
        manager = LucaManager(context_store=mock_store)

        # Test with trusted code
        result = await manager.execute_code_securely(
            "print('Hello from manager')", trust_level="trusted"
        )

        assert result["success"] is True
        assert "Hello from manager" in result["stdout"]
        assert result["exit_code"] == 0

    @pytest.mark.asyncio
    async def test_docker_executor_exception_handling(self):
        """Test Docker executor handles exceptions properly."""
        executor = DockerSandboxExecutor()
        config = SandboxConfig()

        # Mock subprocess to raise an exception
        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_exec.side_effect = Exception("Docker not found")

            result = await executor.execute("print('test')", config)

            assert result.success is False
            assert "Docker not found" in result.stderr
            assert result.exit_code == -1
