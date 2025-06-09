# LUCA Configuration Guide

This directory contains configuration files for the LUCA Dev Assistant. The configuration system supports hierarchical YAML files with environment variable overrides.

## Quick Start

1. Copy `luca.yaml.example` to `luca.yaml`:
   ```bash
   cp config/luca.yaml.example config/luca.yaml
   ```

2. Edit `luca.yaml` to customize your settings

3. Set required environment variables:
   ```bash
   export LUCA_API_KEYS_OPENAI=your-openai-key
   # or
   export ZEROSUM_OPENAI_KEY=your-openai-key
   ```

## Configuration Files

### defaults.yaml
Base configuration with sensible defaults. This file is loaded first and provides fallback values for all settings.

### luca.yaml
Your main configuration file (create from `luca.yaml.example`). Only specify values you want to override from defaults.

### luca.yaml.example
Example configuration showing all available options with documentation.

## Configuration Structure

### Components
Core system components:
- **context_store**: Persistent storage configuration
- **tool_registry**: Tool management and permissions
- **error_schema**: Error handling settings

### Agents
Agent definitions including:
- **Luca** (manager): Main orchestration agent
- **Specialists**: Coder, Tester, DocWriter, Analyst

### Domains
Domain-specific configurations:
- **general**: General development
- **web**: Web development
- **data_science**: Data science tasks
- **quantitative_finance**: QuantConnect development

### Error Handling
Retry strategies and error recovery configuration.

## Environment Variables

Override any configuration value using environment variables:

```bash
# Format: LUCA_<SECTION>_<KEY>
export LUCA_DEBUG=true
export LUCA_LOG_LEVEL=DEBUG

# Nested values use underscores
export LUCA_COMPONENTS_CONTEXT_STORE_TYPE=postgres
export LUCA_AGENTS_TEMPERATURE=0.5

# JSON values for complex types
export LUCA_DOMAINS_GENERAL_ACTIVE_SPECIALISTS='["coder", "tester"]'
```

## Loading Configuration

```python
from luca_core.config import load_config

# Load with defaults and environment overrides
config = load_config()

# Load specific file
config = load_config(config_file="custom.yaml")

# Disable environment overrides
config = load_config(apply_env_overrides=False)
```

## Security Considerations

1. **Never commit API keys** - Use environment variables
2. **Sandbox configuration** - Review allowed_paths and security_level
3. **Tool permissions** - Use blocked_tools to restrict access
4. **Path validation** - All file paths are validated against traversal attacks

## Examples

### Development Configuration
```yaml
debug: true
log_level: DEBUG
components:
  context_store:
    backup_interval: 60  # More frequent backups during dev
```

### Production Configuration
```yaml
environment: production
debug: false
log_level: WARNING
components:
  context_store:
    type: postgres
    connection_params:
      host: ${DB_HOST}
      port: ${DB_PORT}
      database: luca_prod
  error_schema:
    telemetry_enabled: true
    error_retention_days: 90
```

### Custom Domain
```yaml
domains:
  machine_learning:
    description: Machine learning development
    active_specialists:
      - coder
      - tester
      - ml_engineer  # Custom specialist
    default_tools:
      - numpy_tools
      - pytorch_tools
```

## Validation

Configuration is validated on load using Pydantic schemas. Common validation errors:

- **Invalid temperature**: Must be between 0.0 and 2.0
- **Invalid timeout**: Must be positive integer
- **Unknown fields**: Extra fields not in schema are rejected
- **Type mismatches**: Values must match expected types

## Troubleshooting

1. **File not found**: Check that config files exist in the config directory
2. **Validation errors**: Review error messages for specific field issues
3. **Environment override not working**: Ensure variable names use correct format
4. **YAML syntax errors**: Use a YAML validator to check syntax

For more details, see the configuration schema in `luca_core/config/schemas.py`.