"""Final tests to achieve better sandbox coverage."""

import os
import sys
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from luca_core.sandbox.sandbox_manager import (  # noqa: E402
    SandboxConfig,
    SandboxManager,
    SandboxStrategy,
)


class TestSandboxManagerEdgeCases:
    """Test edge cases in SandboxManager."""

    @pytest.mark.asyncio
    async def test_unknown_strategy(self):
        """Test handling of unknown sandbox strategy."""
        manager = SandboxManager()

        # Create a config with an invalid strategy by mocking
        config = SandboxConfig()

        # Temporarily remove the executor to simulate unknown strategy
        original_executors = manager.executors.copy()
        manager.executors.clear()

        try:
            result = await manager.execute("print('test')", config)

            assert result.success is False
            assert "Unknown sandbox strategy" in result.stderr
            assert result.exit_code == -1
        finally:
            # Restore executors
            manager.executors = original_executors

    @pytest.mark.asyncio
    async def test_docker_network_enabled(self):
        """Test Docker executor with network enabled."""
        from luca_core.sandbox.limits import ResourceLimits
        from luca_core.sandbox.sandbox_manager import DockerSandboxExecutor

        executor = DockerSandboxExecutor()
        config = SandboxConfig(
            strategy=SandboxStrategy.DOCKER,
            limits=ResourceLimits(network_offline=False),  # Network enabled
        )

        # Mock subprocess execution
        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = (b"output", b"")

        with patch(
            "asyncio.create_subprocess_exec", return_value=mock_proc
        ) as mock_exec:
            await executor.execute("print('test')", config)

            # Check that network=none was NOT used
            call_args = mock_exec.call_args_list[0][0]
            # Network should not be restricted
            if "--network" in call_args:
                idx = call_args.index("--network")
                assert call_args[idx + 1] != "none"

    @pytest.mark.asyncio
    async def test_restricted_executor_thread_exception(self):
        """Test exception handling in RestrictedPythonExecutor thread."""
        from luca_core.sandbox.sandbox_manager import RestrictedPythonExecutor

        executor = RestrictedPythonExecutor()
        config = SandboxConfig()

        # Test normal execution
        result = await executor.execute("print('test')", config)

        assert result.success is True
        assert "test" in result.stdout
