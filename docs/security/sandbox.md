# Sandbox Security Architecture

## Overview

LUCA implements a multi-layered sandbox architecture to safely execute user-provided code. The system provides three distinct sandboxing strategies, each optimized for different trust levels and use cases.

## Threat Model

Threat model: attacker controls the code string but has no filesystem or network access outside the sandbox. Goals: prevent host compromise, deny CPU/memory exhaustion, and avoid leaking secrets.

## Security Strategies

### 1. Docker Sandbox (Maximum Security)

**Use Case**: Untrusted code from external sources

**Security Features**:
- Runs as non-root user (UID 1000)
- All Linux capabilities dropped (`--cap-drop ALL`)
- No new privileges allowed (`--security-opt no-new-privileges`)
- Read-only root filesystem
- Limited PIDs (64) to prevent fork bombs
- Temporary filesystem with no-exec mount
- Network isolation (disabled by default)
- Resource limits (CPU, memory)
- Resource usage metrics collection

**Configuration**:

```python
config = SandboxConfig(
    strategy=SandboxStrategy.DOCKER,
    cpu_limit=0.5,
    memory_limit_mb=256,
    timeout_seconds=10,
    network_access=False,
)
```

### 2. Process Sandbox (Moderate Security)

**Use Case**: Limited trust code, local development

**Security Features**:
- Resource limits via `setrlimit()`
- CPU time limits
- Memory limits
- No core dumps
- Process count restricted to 0
- Subprocess isolation
- Platform check (Unix-only)
- Uses `sys.executable` for consistent Python interpreter

**Configuration**:

```python
config = SandboxConfig(
    strategy=SandboxStrategy.PROCESS,
    cpu_limit=1.0,
    memory_limit_mb=512,
    timeout_seconds=30,
)
```

**Note**: Process sandboxing is Unix-only and not supported on Windows.

### 3. Restricted Python (Basic Security)

**Use Case**: Trusted code with import restrictions

**Security Features**:
- AST-based import validation
- Whitelist of allowed imports
- Restricted builtins (no `eval`, `exec`, `__import__`)
- Built-ins now read-only via MappingProxyType
- Timeout enforcement via threading
- Output capture and isolation

**Configuration**:

```python
config = SandboxConfig(
    strategy=SandboxStrategy.RESTRICTED,
    allowed_imports=["math", "statistics", "json"],
    timeout_seconds=60,
)
```

## Trust Levels

The sandbox manager provides recommended configurations based on trust levels:

| Trust Level | Strategy    | CPU | Memory | Timeout | Network |
|-------------|-------------|-----|--------|---------|---------|
| Untrusted   | Docker      | 0.5 | 256 MB | 10 s    | No      |
| Limited     | Process     | 1.0 | 512 MB | 30 s    | No      |
| Trusted     | Restricted  | 2.0 | 1024 MB| 60 s    | No      |

## Usage Example

```python
from luca_core.sandbox.sandbox_manager import get_sandbox_manager

# Get thread-local sandbox manager
sandbox = get_sandbox_manager()

# Execute untrusted code
result = await sandbox.execute(
    code="print('Hello from sandbox!')",
    config=sandbox.get_recommended_config("untrusted")
)

if result.success:
    print(f"Output: {result.stdout}")
else:
    print(f"Error: {result.stderr}")
```

> `result.resource_usage` returns CPU time and max RSS; log anomalies.

## Security Best Practices

1. **Default to Maximum Security**: Always use the most restrictive sandbox that meets your needs
2. **Validate Input**: Pre-validate code before execution when possible
3. **Monitor & log resources**: Check `result.resource_usage` for anomalies
4. **Timeout Everything**: Always set reasonable timeouts
5. **No Network by Default**: Enable network access only when absolutely necessary
6. **Audit Imports**: For restricted Python, carefully audit allowed imports

## Integration with LUCA

The sandbox is integrated into LUCA's manager layer. Use the new `execute_code_securely()` helper:

```python
# In LucaManager
result = await self.execute_code_securely(
    code=user_code,
    trust_level="untrusted"
)
```

## Resource Limits

The sandbox system enforces strict resource limits through the `limits` module:

### Default Limits (as specified in issue #60)
- **CPU**: 1.0 cores
- **Memory**: 1024 MB
- **Disk**: 512 MB
- **Network**: Offline (disabled by default)

### Trust-Based Limits

```python
from luca_core.sandbox.limits import get_limits_for_trust_level

# Automatically select limits based on trust level
limits = get_limits_for_trust_level("untrusted")  # Strict limits
limits = get_limits_for_trust_level("limited")    # Default limits
limits = get_limits_for_trust_level("trusted")    # Relaxed limits
```

### Custom Limits

```python
from luca_core.sandbox.limits import ResourceLimits
from luca_core.sandbox.sandbox_manager import SandboxConfig

# Create custom limits
custom_limits = ResourceLimits(
    cpu_cores=2.0,
    memory_mb=2048,
    disk_mb=1024,
    network_offline=False,  # Enable network
    timeout_seconds=60,
)

# Use with sandbox config
config = SandboxConfig(limits=custom_limits)
```

### Limit Validation

All resource limits are validated to ensure they don't exceed safe maximums:
- Max CPU: 4.0 cores
- Max Memory: 4096 MB
- Max Disk: 2048 MB
- Max Timeout: 300 seconds

## Known Limitations

1. **Windows Support**: Process sandboxing is not available on Windows
2. **Docker Requirement**: Docker sandbox requires Docker to be installed and running
3. **Performance Overhead**: Docker sandbox incurs ~300-600 ms startup
4. **Import Restrictions**: Restricted Python cannot dynamically import modules

## Security Incident Response

If a security issue is detected:

1. The sandbox will immediately terminate the execution
2. An error result will be returned with details
3. The incident will be logged for audit purposes
4. No persistent changes will be made to the system

## Thread Safety

The sandbox manager uses thread-local storage to ensure safe concurrent execution:

```python
from luca_core.sandbox.sandbox_manager import get_sandbox_manager

# Each thread gets its own sandbox manager instance
manager = get_sandbox_manager()
```

## Future Enhancements

- WebAssembly sandbox for browser-based execution
- gVisor integration for enhanced container security
- Fine-grained capability management
- Resource usage prediction and anomaly detection

## Running LUCA

To run LUCA with sandboxing enabled:

```bash
python3 -m luca_cli run
```