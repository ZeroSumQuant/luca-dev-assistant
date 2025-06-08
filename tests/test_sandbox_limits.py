"""
Tests for the sandbox limits module.
"""

import pytest

from luca_core.sandbox.limits import (
    DEFAULT_LIMITS,
    RELAXED_LIMITS,
    STRICT_LIMITS,
    LimitsValidator,
    ResourceLimits,
    get_limits_for_trust_level,
)


class TestResourceLimits:
    """Test ResourceLimits dataclass."""

    def test_default_limits_values(self):
        """Test that DEFAULT_LIMITS has the correct values from the issue."""
        assert DEFAULT_LIMITS.cpu_cores == 1.0
        assert DEFAULT_LIMITS.memory_mb == 1024
        assert DEFAULT_LIMITS.disk_mb == 512
        assert DEFAULT_LIMITS.network_offline is True

    def test_strict_limits_values(self):
        """Test that STRICT_LIMITS are more restrictive."""
        assert STRICT_LIMITS.cpu_cores < DEFAULT_LIMITS.cpu_cores
        assert STRICT_LIMITS.memory_mb < DEFAULT_LIMITS.memory_mb
        assert STRICT_LIMITS.disk_mb < DEFAULT_LIMITS.disk_mb
        assert STRICT_LIMITS.network_offline is True
        assert STRICT_LIMITS.timeout_seconds < DEFAULT_LIMITS.timeout_seconds

    def test_relaxed_limits_values(self):
        """Test that RELAXED_LIMITS are less restrictive."""
        assert RELAXED_LIMITS.cpu_cores > DEFAULT_LIMITS.cpu_cores
        assert RELAXED_LIMITS.memory_mb > DEFAULT_LIMITS.memory_mb
        assert RELAXED_LIMITS.disk_mb > DEFAULT_LIMITS.disk_mb
        assert RELAXED_LIMITS.network_offline is False  # Network enabled
        assert RELAXED_LIMITS.timeout_seconds > DEFAULT_LIMITS.timeout_seconds

    def test_limits_immutability(self):
        """Test that ResourceLimits is immutable."""
        limits = ResourceLimits()
        with pytest.raises(AttributeError):
            limits.cpu_cores = 2.0
        with pytest.raises(AttributeError):
            limits.memory_mb = 2048

    def test_to_dict(self):
        """Test conversion to dictionary."""
        limits = ResourceLimits(
            cpu_cores=2.0,
            memory_mb=2048,
            disk_mb=1024,
            network_offline=False,
        )
        result = limits.to_dict()

        assert result["cpu_cores"] == 2.0
        assert result["memory_mb"] == 2048
        assert result["disk_mb"] == 1024
        assert result["network_offline"] is False
        assert "timeout_seconds" in result
        assert "max_processes" in result

    def test_with_network(self):
        """Test creating a copy with network enabled."""
        original = ResourceLimits(network_offline=True)
        with_network = original.with_network()

        # Original unchanged
        assert original.network_offline is True

        # New instance has network
        assert with_network.network_offline is False

        # Other values preserved
        assert with_network.cpu_cores == original.cpu_cores
        assert with_network.memory_mb == original.memory_mb
        assert with_network.disk_mb == original.disk_mb

    def test_with_extended_timeout(self):
        """Test creating a copy with extended timeout."""
        original = ResourceLimits(timeout_seconds=30, cpu_time_seconds=30)
        extended = original.with_extended_timeout(60)

        # Original unchanged
        assert original.timeout_seconds == 30
        assert original.cpu_time_seconds == 30

        # New instance has extended timeout
        assert extended.timeout_seconds == 60
        assert extended.cpu_time_seconds == 60

        # Other values preserved
        assert extended.cpu_cores == original.cpu_cores
        assert extended.memory_mb == original.memory_mb


class TestGetLimitsForTrustLevel:
    """Test get_limits_for_trust_level function."""

    def test_untrusted_returns_strict(self):
        """Test that untrusted code gets strict limits."""
        limits = get_limits_for_trust_level("untrusted")
        assert limits == STRICT_LIMITS

    def test_trusted_returns_relaxed(self):
        """Test that trusted code gets relaxed limits."""
        limits = get_limits_for_trust_level("trusted")
        assert limits == RELAXED_LIMITS

    def test_limited_returns_default(self):
        """Test that limited trust gets default limits."""
        limits = get_limits_for_trust_level("limited")
        assert limits == DEFAULT_LIMITS

    def test_unknown_returns_default(self):
        """Test that unknown trust level gets default limits."""
        limits = get_limits_for_trust_level("unknown")
        assert limits == DEFAULT_LIMITS


class TestLimitsValidator:
    """Test LimitsValidator class."""

    def test_validate_default_limits(self):
        """Test that default limits are valid."""
        is_valid, error = LimitsValidator.validate(DEFAULT_LIMITS)
        assert is_valid is True
        assert error is None

    def test_validate_strict_limits(self):
        """Test that strict limits are valid."""
        is_valid, error = LimitsValidator.validate(STRICT_LIMITS)
        assert is_valid is True
        assert error is None

    def test_validate_relaxed_limits(self):
        """Test that relaxed limits are valid."""
        is_valid, error = LimitsValidator.validate(RELAXED_LIMITS)
        assert is_valid is True
        assert error is None

    def test_validate_excessive_cpu(self):
        """Test validation fails for excessive CPU."""
        limits = ResourceLimits(cpu_cores=5.0)  # Exceeds max of 4.0
        is_valid, error = LimitsValidator.validate(limits)
        assert is_valid is False
        assert "CPU cores" in error
        assert "exceeds max" in error

    def test_validate_negative_cpu(self):
        """Test validation fails for negative CPU."""
        limits = ResourceLimits(cpu_cores=-1.0)
        is_valid, error = LimitsValidator.validate(limits)
        assert is_valid is False
        assert "CPU cores must be positive" in error

    def test_validate_excessive_memory(self):
        """Test validation fails for excessive memory."""
        limits = ResourceLimits(memory_mb=5000)  # Exceeds max of 4096
        is_valid, error = LimitsValidator.validate(limits)
        assert is_valid is False
        assert "Memory" in error
        assert "exceeds max" in error

    def test_validate_zero_memory(self):
        """Test validation fails for zero memory."""
        limits = ResourceLimits(memory_mb=0)
        is_valid, error = LimitsValidator.validate(limits)
        assert is_valid is False
        assert "Memory must be positive" in error

    def test_validate_excessive_disk(self):
        """Test validation fails for excessive disk."""
        limits = ResourceLimits(disk_mb=3000)  # Exceeds max of 2048
        is_valid, error = LimitsValidator.validate(limits)
        assert is_valid is False
        assert "Disk" in error
        assert "exceeds maximum" in error

    def test_validate_negative_disk(self):
        """Test validation fails for negative disk."""
        limits = ResourceLimits(disk_mb=-100)
        is_valid, error = LimitsValidator.validate(limits)
        assert is_valid is False
        assert "Disk space must be positive" in error

    def test_validate_excessive_timeout(self):
        """Test validation fails for excessive timeout."""
        limits = ResourceLimits(timeout_seconds=400)  # Exceeds max of 300
        is_valid, error = LimitsValidator.validate(limits)
        assert is_valid is False
        assert "Timeout" in error
        assert "exceeds max" in error

    def test_validate_zero_timeout(self):
        """Test validation fails for zero timeout."""
        limits = ResourceLimits(timeout_seconds=0)
        is_valid, error = LimitsValidator.validate(limits)
        assert is_valid is False
        assert "Timeout must be positive" in error

    def test_validate_zero_processes(self):
        """Test validation fails for zero max processes."""
        limits = ResourceLimits(max_processes=0)
        is_valid, error = LimitsValidator.validate(limits)
        assert is_valid is False
        assert "Max processes must be positive" in error

    def test_validate_zero_files(self):
        """Test validation fails for zero max open files."""
        limits = ResourceLimits(max_open_files=0)
        is_valid, error = LimitsValidator.validate(limits)
        assert is_valid is False
        assert "Max open files must be positive" in error

    def test_validate_edge_cases(self):
        """Test validation at boundary values."""
        # At maximum values - should be valid
        limits = ResourceLimits(
            cpu_cores=4.0,
            memory_mb=4096,
            disk_mb=2048,
            timeout_seconds=300,
        )
        is_valid, error = LimitsValidator.validate(limits)
        assert is_valid is True
        assert error is None

        # Just above maximum CPU - should fail
        limits = ResourceLimits(cpu_cores=4.1)
        is_valid, error = LimitsValidator.validate(limits)
        assert is_valid is False
