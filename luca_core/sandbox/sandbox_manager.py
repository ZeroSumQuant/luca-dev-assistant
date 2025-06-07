"""
Comprehensive sandboxing manager for secure code execution.

This module provides multiple sandboxing strategies to safely execute
user-provided code with proper resource limits and security boundaries.
"""

import ast
import asyncio
import os
import resource
import sys
import tempfile
import threading
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, List, Optional


class SandboxStrategy(Enum):
    """Available sandboxing strategies."""

    DOCKER = "docker"
    PROCESS = "process"  # subprocess with resource limits
    RESTRICTED = "restricted"  # restricted Python execution
    NONE = "none"  # no sandboxing (dangerous!)


class SandboxConfig:
    """Configuration for sandbox execution."""

    def __init__(
        self,
        strategy: SandboxStrategy = SandboxStrategy.DOCKER,
        cpu_limit: float = 1.0,  # CPU cores
        memory_limit_mb: int = 512,  # Memory in MB
        timeout_seconds: int = 30,
        allowed_imports: Optional[List[str]] = None,
        allowed_paths: Optional[List[str]] = None,
        network_access: bool = False,
        env_vars: Optional[Dict[str, str]] = None,
    ):
        self.strategy = strategy
        self.cpu_limit = cpu_limit
        self.memory_limit_mb = memory_limit_mb
        self.timeout_seconds = timeout_seconds
        self.allowed_imports = allowed_imports or []
        self.allowed_paths = allowed_paths or []
        self.network_access = network_access
        self.env_vars = env_vars or {}


class SandboxResult:
    """Result of sandboxed execution."""

    def __init__(
        self,
        stdout: str = "",
        stderr: str = "",
        exit_code: int = 0,
        error: Optional[Exception] = None,
        resource_usage: Optional[Dict[str, Any]] = None,
    ):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.error = error
        self.resource_usage = resource_usage or {}

    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.exit_code == 0 and self.error is None


class SandboxExecutor(ABC):
    """Abstract base class for sandbox executors."""

    @abstractmethod
    async def execute(self, code: str, config: SandboxConfig) -> SandboxResult:
        """Execute code in sandbox with given configuration."""
        pass


class DockerSandboxExecutor(SandboxExecutor):
    """Docker-based sandbox executor."""

    def __init__(self, image: str = "python:3.11-slim"):
        self.image = image

    async def execute(self, code: str, config: SandboxConfig) -> SandboxResult:
        """Execute code in Docker container."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write code to temporary file
            code_file = Path(tmpdir) / "code.py"
            code_file.write_text(code)

            # Build Docker command with security hardening
            cmd = [
                "docker",
                "run",
                "--rm",
                "--user",
                "1000:1000",  # Non-root user
                "--security-opt",
                "no-new-privileges",
                "--cap-drop",
                "ALL",  # Drop all Linux capabilities
                f"--cpus={config.cpu_limit}",
                f"--memory={config.memory_limit_mb}m",
                "--pids-limit",
                "64",  # Prevent fork bombs
                "--read-only",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,size=100m",  # nosec B108
            ]

            # Add network restrictions
            if not config.network_access:
                cmd.extend(["--network", "none"])

            # Add environment variables
            for key, value in config.env_vars.items():
                cmd.extend(["-e", f"{key}={value}"])

            # Mount code file
            cmd.extend(
                [
                    "-v",
                    f"{code_file}:/code.py:ro",
                    self.image,
                    "python",
                    "/code.py",
                ]
            )

            try:
                # Run with timeout
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=config.timeout_seconds
                )

                # Collect resource metrics (optional - best effort)
                resource_usage = {}
                try:
                    # Get container ID from the process (this is a simplified approach)
                    # In production, track container ID from docker run
                    stats_proc = await asyncio.create_subprocess_exec(
                        "docker",
                        "ps",
                        "-q",
                        "--filter",
                        f"ancestor={self.image}",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.DEVNULL,
                    )
                    container_ids, _ = await stats_proc.communicate()

                    if container_ids and stats_proc.returncode == 0:
                        container_id = container_ids.decode().strip().split("\n")[0]
                        if container_id:
                            # Get stats for the container
                            stats_cmd = await asyncio.create_subprocess_exec(
                                "docker",
                                "stats",
                                "--no-stream",
                                "--format",
                                "{{.CPUPerc}};{{.MemUsage}}",
                                container_id,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.DEVNULL,
                            )
                            stats_output, _ = await stats_cmd.communicate()

                            if stats_output and stats_cmd.returncode == 0:
                                cpu_str, mem_str = (
                                    stats_output.decode().strip().split(";")
                                )
                                resource_usage = {
                                    "cpu_percent": cpu_str.strip("%"),
                                    "memory_usage": mem_str.split("/")[0].strip(),
                                }
                except Exception:
                    # Ignore errors in stats collection
                    pass

                return SandboxResult(
                    stdout=stdout.decode() if stdout else "",
                    stderr=stderr.decode() if stderr else "",
                    exit_code=proc.returncode or 0,
                    resource_usage=resource_usage,
                )

            except asyncio.TimeoutError:
                if proc and proc.returncode is None:
                    proc.kill()
                return SandboxResult(
                    stderr=f"Execution timeout ({config.timeout_seconds}s)",
                    exit_code=-1,
                    error=TimeoutError("Execution timeout"),
                )
            except Exception as e:
                return SandboxResult(
                    stderr=str(e),
                    exit_code=-1,
                    error=e,
                )


class ProcessSandboxExecutor(SandboxExecutor):
    """Subprocess-based sandbox with resource limits."""

    async def execute(self, code: str, config: SandboxConfig) -> SandboxResult:
        """Execute code in subprocess with resource limits."""

        # Check platform support
        if os.name == "nt":
            return SandboxResult(
                stderr="Process sandboxing not supported on Windows",
                exit_code=-1,
                error=Exception("Process sandboxing requires Unix-like OS"),
            )

        def set_limits():
            """Set resource limits for subprocess."""
            try:
                # Set CPU time limit
                resource.setrlimit(
                    resource.RLIMIT_CPU,
                    (config.timeout_seconds, config.timeout_seconds),
                )
            except Exception:
                pass  # Skip if not supported

            try:
                # Set memory limit (in bytes) - only if current limit allows it
                memory_bytes = config.memory_limit_mb * 1024 * 1024
                current_limit = resource.getrlimit(resource.RLIMIT_AS)
                if current_limit[1] >= memory_bytes:  # Check against hard limit
                    resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
            except Exception:
                pass  # Skip if not supported

            try:
                # Disable core dumps
                resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            except Exception:
                pass

            try:
                # Limit number of processes - be conservative
                current_nproc = resource.getrlimit(resource.RLIMIT_NPROC)
                if current_nproc[0] > 50:  # Only limit if we have more than 50
                    resource.setrlimit(resource.RLIMIT_NPROC, (50, current_nproc[1]))
            except Exception:
                pass

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                preexec_fn=set_limits if os.name != "nt" else None,
                env={**os.environ, **config.env_vars},
            )

            # Get start resource usage
            start_time = asyncio.get_event_loop().time()

            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=config.timeout_seconds
            )

            # Calculate resource usage
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time

            return SandboxResult(
                stdout=stdout.decode() if stdout else "",
                stderr=stderr.decode() if stderr else "",
                exit_code=proc.returncode or 0,
                resource_usage={
                    "execution_time_seconds": duration,
                    "cpu_limit": config.cpu_limit,
                    "memory_limit_mb": config.memory_limit_mb,
                },
            )

        except asyncio.TimeoutError:
            if proc and proc.returncode is None:
                proc.kill()
            return SandboxResult(
                stderr=f"Execution timeout ({config.timeout_seconds}s)",
                exit_code=-1,
                error=TimeoutError("Execution timeout"),
            )
        except Exception as e:
            return SandboxResult(
                stderr=str(e),
                exit_code=-1,
                error=e,
            )
        finally:
            Path(temp_file).unlink(missing_ok=True)


class RestrictedPythonExecutor(SandboxExecutor):
    """Restricted Python execution environment."""

    def __init__(self):
        self.safe_builtins = {
            "abs",
            "all",
            "any",
            "bool",
            "dict",
            "enumerate",
            "filter",
            "float",
            "int",
            "len",
            "list",
            "map",
            "max",
            "min",
            "print",
            "range",
            "round",
            "set",
            "sorted",
            "str",
            "sum",
            "tuple",
            "zip",
        }

    def _validate_imports(self, code: str, allowed_imports: List[str]) -> Optional[str]:
        """Validate that code only uses allowed imports."""
        try:
            tree = ast.parse(code, mode="exec")
        except SyntaxError as e:
            return f"Syntax error: {e}"

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in allowed_imports:
                        return f"Import not allowed: {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module not in allowed_imports:
                    return f"Import not allowed: {node.module}"

        return None

    async def execute(self, code: str, config: SandboxConfig) -> SandboxResult:
        """Execute code in restricted Python environment."""

        # Validate imports first
        import_error = self._validate_imports(code, config.allowed_imports)
        if import_error:
            return SandboxResult(
                stderr=import_error,
                exit_code=-1,
                error=Exception(import_error),
            )

        # Create restricted globals with read-only builtins
        import builtins

        builtin_dict = vars(builtins)
        safe_builtins = {
            name: builtin_dict[name]
            for name in self.safe_builtins
            if name in builtin_dict
        }
        restricted_globals = {"__builtins__": MappingProxyType(safe_builtins)}

        # Add allowed imports by providing a restricted __import__
        original_import = builtins.__import__

        def restricted_import(name, *args, **kwargs):
            if name not in config.allowed_imports:
                raise ImportError(f"Import not allowed: {name}")
            return original_import(name, *args, **kwargs)

        # Create a new dict with our custom import
        import_builtins = dict(safe_builtins)
        import_builtins["__import__"] = restricted_import
        restricted_globals["__builtins__"] = MappingProxyType(import_builtins)

        # Capture output
        import sys
        from io import StringIO

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_buffer = StringIO()
        stderr_buffer = StringIO()

        try:
            sys.stdout = stdout_buffer
            sys.stderr = stderr_buffer

            # Execute with timeout
            exec_locals: Dict[str, Any] = {}

            def run_code():
                exec(code, restricted_globals, exec_locals)  # nosec B102

            thread = threading.Thread(target=run_code)
            thread.daemon = True
            thread.start()
            thread.join(timeout=config.timeout_seconds)

            if thread.is_alive():
                return SandboxResult(
                    stderr=f"Execution timeout ({config.timeout_seconds}s)",
                    exit_code=-1,
                    error=TimeoutError("Execution timeout"),
                )

            return SandboxResult(
                stdout=stdout_buffer.getvalue(),
                stderr=stderr_buffer.getvalue(),
                exit_code=0,
            )

        except Exception as e:
            return SandboxResult(
                stderr=str(e),
                exit_code=-1,
                error=e,
            )
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


class SandboxManager:
    """Main sandbox manager that coordinates execution strategies."""

    def __init__(self):
        self.executors = {
            SandboxStrategy.DOCKER: DockerSandboxExecutor(),
            SandboxStrategy.PROCESS: ProcessSandboxExecutor(),
            SandboxStrategy.RESTRICTED: RestrictedPythonExecutor(),
        }

    async def execute(
        self,
        code: str,
        config: Optional[SandboxConfig] = None,
    ) -> SandboxResult:
        """Execute code with specified sandbox configuration."""
        if config is None:
            config = SandboxConfig()

        # Validate configuration
        if config.strategy == SandboxStrategy.NONE:
            return SandboxResult(
                stderr="Unsafe execution mode not allowed",
                exit_code=-1,
                error=Exception("Sandbox strategy 'none' is not allowed"),
            )

        # Get appropriate executor
        executor = self.executors.get(config.strategy)
        if not executor:
            return SandboxResult(
                stderr=f"Unknown sandbox strategy: {config.strategy}",
                exit_code=-1,
                error=Exception(f"Unknown sandbox strategy: {config.strategy}"),
            )

        # Execute code
        try:
            return await executor.execute(code, config)
        except Exception as e:
            return SandboxResult(
                stderr=f"Sandbox execution failed: {str(e)}",
                exit_code=-1,
                error=e,
            )

    def get_recommended_config(self, trust_level: str = "untrusted") -> SandboxConfig:
        """Get recommended sandbox configuration based on trust level."""
        if trust_level == "untrusted":
            # Maximum security for untrusted code
            return SandboxConfig(
                strategy=SandboxStrategy.DOCKER,
                cpu_limit=0.5,
                memory_limit_mb=256,
                timeout_seconds=10,
                network_access=False,
            )
        elif trust_level == "limited":
            # Some restrictions for limited trust
            return SandboxConfig(
                strategy=SandboxStrategy.PROCESS,
                cpu_limit=1.0,
                memory_limit_mb=512,
                timeout_seconds=30,
                network_access=False,
            )
        elif trust_level == "trusted":
            # Minimal restrictions for trusted code
            return SandboxConfig(
                strategy=SandboxStrategy.RESTRICTED,
                cpu_limit=2.0,
                memory_limit_mb=1024,
                timeout_seconds=60,
                allowed_imports=["math", "statistics", "json"],
                network_access=False,
            )
        else:
            # Default to maximum security
            return self.get_recommended_config("untrusted")


# Thread-local storage for sandbox managers
_local = threading.local()


def get_sandbox_manager() -> SandboxManager:
    """Get a thread-local sandbox manager instance.

    Returns:
        Thread-local SandboxManager instance
    """
    if not hasattr(_local, "sandbox_manager"):
        _local.sandbox_manager = SandboxManager()
    return _local.sandbox_manager


# Global instance for backward compatibility
sandbox_manager = get_sandbox_manager()
