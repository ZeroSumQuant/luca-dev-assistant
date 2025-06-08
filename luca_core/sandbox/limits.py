"""
Resource limits configuration for sandbox execution.

This module defines the default resource limits and constraints
for sandboxed code execution to ensure system stability and security.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ResourceLimits:
    """Resource limits for sandbox execution.

    All limits are immutable to prevent tampering during execution.
    """

    # CPU limits
    cpu_cores: float = 1.0  # Number of CPU cores
    cpu_time_seconds: int = 30  # Maximum CPU time in seconds

    # Memory limits
    memory_mb: int = 1024  # Maximum memory in megabytes

    # Disk I/O limits
    disk_mb: int = 512  # Maximum disk usage in megabytes
    max_file_size_mb: int = 100  # Maximum size for any single file

    # Network access
    network_offline: bool = True  # Network access disabled by default

    # Process limits
    max_processes: int = 50  # Maximum number of processes/threads
    max_open_files: int = 100  # Maximum number of open file descriptors

    # Time limits
    timeout_seconds: int = 30  # Overall execution timeout

    def to_dict(self) -> dict:
        """Convert limits to dictionary for serialization."""
        return {
            "cpu_cores": self.cpu_cores,
            "cpu_time_seconds": self.cpu_time_seconds,
            "memory_mb": self.memory_mb,
            "disk_mb": self.disk_mb,
            "max_file_size_mb": self.max_file_size_mb,
            "network_offline": self.network_offline,
            "max_processes": self.max_processes,
            "max_open_files": self.max_open_files,
            "timeout_seconds": self.timeout_seconds,
        }

    def with_network(self) -> "ResourceLimits":
        """Create a copy with network access enabled."""
        return ResourceLimits(
            cpu_cores=self.cpu_cores,
            cpu_time_seconds=self.cpu_time_seconds,
            memory_mb=self.memory_mb,
            disk_mb=self.disk_mb,
            max_file_size_mb=self.max_file_size_mb,
            network_offline=False,  # Enable network
            max_processes=self.max_processes,
            max_open_files=self.max_open_files,
            timeout_seconds=self.timeout_seconds,
        )

    def with_extended_timeout(self, seconds: int) -> "ResourceLimits":
        """Create a copy with extended timeout."""
        return ResourceLimits(
            cpu_cores=self.cpu_cores,
            cpu_time_seconds=seconds,
            memory_mb=self.memory_mb,
            disk_mb=self.disk_mb,
            max_file_size_mb=self.max_file_size_mb,
            network_offline=self.network_offline,
            max_processes=self.max_processes,
            max_open_files=self.max_open_files,
            timeout_seconds=seconds,
        )


# Default limits as specified in the issue
DEFAULT_LIMITS = ResourceLimits(
    cpu_cores=1.0,
    memory_mb=1024,
    disk_mb=512,
    network_offline=True,
)

# Strict limits for untrusted code
STRICT_LIMITS = ResourceLimits(
    cpu_cores=0.5,
    cpu_time_seconds=10,
    memory_mb=256,
    disk_mb=100,
    max_file_size_mb=10,
    network_offline=True,
    max_processes=10,
    max_open_files=20,
    timeout_seconds=10,
)

# Relaxed limits for trusted code
RELAXED_LIMITS = ResourceLimits(
    cpu_cores=2.0,
    cpu_time_seconds=60,
    memory_mb=2048,
    disk_mb=1024,
    max_file_size_mb=200,
    network_offline=False,
    max_processes=100,
    max_open_files=200,
    timeout_seconds=60,
)


def get_limits_for_trust_level(trust_level: str) -> ResourceLimits:
    """Get appropriate resource limits based on trust level.

    Args:
        trust_level: One of "untrusted", "limited", "trusted"

    Returns:
        ResourceLimits appropriate for the trust level
    """
    if trust_level == "untrusted":
        return STRICT_LIMITS
    elif trust_level == "trusted":
        return RELAXED_LIMITS
    else:  # "limited" or default
        return DEFAULT_LIMITS


class LimitsValidator:
    """Validator for resource limits to ensure they are within safe bounds."""

    # Maximum allowed values for any configuration
    MAX_CPU_CORES = 4.0
    MAX_MEMORY_MB = 4096
    MAX_DISK_MB = 2048
    MAX_TIMEOUT_SECONDS = 300

    @classmethod
    def validate(cls, limits: ResourceLimits) -> tuple[bool, Optional[str]]:
        """Validate that resource limits are within safe bounds.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if limits.cpu_cores > cls.MAX_CPU_CORES:
            return (
                False,
                f"CPU cores ({limits.cpu_cores}) exceeds maximum ({cls.MAX_CPU_CORES})",
            )

        if limits.cpu_cores <= 0:
            return False, "CPU cores must be positive"

        if limits.memory_mb > cls.MAX_MEMORY_MB:
            return (
                False,
                f"Memory ({limits.memory_mb}MB) exceeds max ({cls.MAX_MEMORY_MB}MB)",
            )

        if limits.memory_mb <= 0:
            return False, "Memory must be positive"

        if limits.disk_mb > cls.MAX_DISK_MB:
            return (
                False,
                f"Disk ({limits.disk_mb}MB) exceeds maximum ({cls.MAX_DISK_MB}MB)",
            )

        if limits.disk_mb <= 0:
            return False, "Disk space must be positive"

        if limits.timeout_seconds > cls.MAX_TIMEOUT_SECONDS:
            msg = f"Timeout ({limits.timeout_seconds}s) exceeds max "
            msg += f"({cls.MAX_TIMEOUT_SECONDS}s)"
            return False, msg

        if limits.timeout_seconds <= 0:
            return False, "Timeout must be positive"

        if limits.max_processes <= 0:
            return False, "Max processes must be positive"

        if limits.max_open_files <= 0:
            return False, "Max open files must be positive"

        return True, None
