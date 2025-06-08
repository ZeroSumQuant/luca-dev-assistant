"""Additional tests for sandbox config with limits integration."""

import pytest

from luca_core.sandbox.limits import ResourceLimits
from luca_core.sandbox.sandbox_manager import SandboxConfig, SandboxStrategy


class TestSandboxConfigWithLimits:
    """Test SandboxConfig integration with ResourceLimits."""

    def test_config_validates_limits(self):
        """Test that SandboxConfig validates limits on construction."""
        # Try to create config with invalid limits (exceeds max)
        invalid_limits = ResourceLimits(
            cpu_cores=10.0,  # Exceeds max of 4.0
            memory_mb=8192,  # Exceeds max of 4096
        )

        with pytest.raises(ValueError) as exc_info:
            SandboxConfig(limits=invalid_limits)

        assert "Invalid resource limits" in str(exc_info.value)
        assert "CPU cores" in str(exc_info.value)

    def test_config_with_zero_values(self):
        """Test that config rejects limits with zero values."""
        zero_cpu_limits = ResourceLimits(cpu_cores=0)

        with pytest.raises(ValueError) as exc_info:
            SandboxConfig(limits=zero_cpu_limits)

        assert "CPU cores must be positive" in str(exc_info.value)

    def test_config_backward_compatibility(self):
        """Test backward compatibility properties work correctly."""
        # Create config with specific limits
        limits = ResourceLimits(
            cpu_cores=1.5,
            memory_mb=2048,
            timeout_seconds=45,
            network_offline=False,
        )
        config = SandboxConfig(limits=limits)

        # Test all backward compatibility properties
        assert config.cpu_limit == 1.5
        assert config.memory_limit_mb == 2048
        assert config.timeout_seconds == 45
        assert config.network_access is True  # inverted from network_offline

    def test_config_with_all_parameters(self):
        """Test creating config with all parameters."""
        limits = ResourceLimits(
            cpu_cores=2.0,
            memory_mb=1536,
            disk_mb=768,
            network_offline=True,
            max_processes=30,
            timeout_seconds=20,
        )

        config = SandboxConfig(
            strategy=SandboxStrategy.RESTRICTED,
            limits=limits,
            allowed_imports=["os", "sys"],
            allowed_paths=["/home/user"],
            env_vars={"PYTHONPATH": "/custom/path"},
        )

        assert config.strategy == SandboxStrategy.RESTRICTED
        assert config.limits == limits
        assert config.allowed_imports == ["os", "sys"]
        assert config.allowed_paths == ["/home/user"]
        assert config.env_vars == {"PYTHONPATH": "/custom/path"}
        assert config.cpu_limit == 2.0
        assert config.memory_limit_mb == 1536
        assert config.network_access is False
