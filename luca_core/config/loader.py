"""YAML configuration loader implementation.

This module provides the core functionality for loading, validating, and
merging configuration from YAML files with environment variable overrides.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from pydantic import ValidationError

from luca_core.config.schemas import ConfigSchema
from luca_core.schemas.error import ErrorPayload, create_user_error
from luca_core.validation.validators import ValidationError as InputValidationError
from luca_core.validation.validators import (
    validate_file_path,
    validate_yaml_safe,
)


class ConfigurationError(Exception):
    """Raised when configuration loading or validation fails."""

    def __init__(self, message: str, error_payload: Optional[ErrorPayload] = None):
        super().__init__(message)
        self.error_payload = error_payload


class ConfigLoader:
    """Handles loading and validation of YAML configuration files."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the configuration loader.

        Args:
            config_dir: Directory to search for configuration files.
                       Defaults to ./config relative to the project root.
        """
        self.config_dir = config_dir or self._find_config_dir()
        self._config_cache: Optional[ConfigSchema] = None

    def _find_config_dir(self) -> Path:
        """Find the configuration directory.

        Searches for a 'config' directory in common locations.
        """
        # Try relative to current working directory
        cwd_config = Path.cwd() / "config"
        if cwd_config.exists() and cwd_config.is_dir():
            return cwd_config

        # Try relative to this file's location (project root)
        project_root = Path(__file__).parent.parent.parent
        root_config = project_root / "config"
        if root_config.exists() and root_config.is_dir():
            return root_config

        # Default to current directory
        return Path.cwd()

    def load_file(self, filename: Union[str, Path]) -> Dict[str, Any]:
        """Load a YAML file and return its contents.

        Args:
            filename: Name or path of the YAML file to load.

        Returns:
            Dictionary containing the parsed YAML content.

        Raises:
            ConfigurationError: If file cannot be loaded or parsed.
        """
        if isinstance(filename, str):
            # If it's just a filename, look in config directory
            if not filename.endswith((".yaml", ".yml")):
                # Try both extensions
                yaml_path = self.config_dir / f"{filename}.yaml"
                yml_path = self.config_dir / f"{filename}.yml"
                filepath = yaml_path if yaml_path.exists() else yml_path
            else:
                filepath = self.config_dir / filename
        else:
            filepath = filename

        # Validate the path - allow absolute paths for config files
        try:
            validate_file_path(
                filepath, must_exist=False, base_dir=self.config_dir.parent
            )
        except (ValueError, InputValidationError) as e:
            raise ConfigurationError(
                f"Invalid configuration path: {filepath}",
                create_user_error(str(e), error_code="CONFIG_PATH_INVALID"),
            )

        if not filepath.exists():
            raise ConfigurationError(
                f"Configuration file not found: {filepath}",
                create_user_error(
                    f"The configuration file '{filepath}' does not exist.",
                    remediation="Check the file path or create the configuration file.",
                    error_code="CONFIG_FILE_NOT_FOUND",
                ),
            )

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Validate YAML safety
            validate_yaml_safe(content)

            # Parse YAML
            data = yaml.safe_load(content)
            return data or {}

        except InputValidationError as e:
            raise ConfigurationError(
                f"Unsafe YAML content in file: {filepath}",
                create_user_error(
                    str(e),
                    remediation=(
                        "Remove any Python object tags or unsafe constructs "
                        "from the YAML file."
                    ),
                    error_code="CONFIG_YAML_UNSAFE",
                ),
            )
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Failed to parse YAML file: {filepath}",
                create_user_error(
                    f"Invalid YAML syntax: {e}",
                    remediation="Check the YAML file for syntax errors.",
                    error_code="CONFIG_YAML_INVALID",
                ),
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration file: {filepath}",
                create_user_error(
                    f"Error reading file: {e}",
                    error_code="CONFIG_FILE_READ_ERROR",
                ),
            )

    def _merge_configs(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries.

        Args:
            base: Base configuration dictionary.
            override: Configuration to override base values.

        Returns:
            Merged configuration dictionary.
        """
        result = base.copy()

        for key, value in override.items():
            if value is None:
                # Skip None values - let defaults apply
                continue
            elif (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                # Recursive merge for nested dictionaries
                result[key] = self._merge_configs(result[key], value)
            elif isinstance(value, dict):
                # New nested dictionary - process recursively to remove None values
                cleaned = self._merge_configs({}, value)
                if cleaned:  # Only add if not empty after cleaning
                    result[key] = cleaned
            else:
                # Override the value
                result[key] = value

        return result

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration.

        Environment variables follow the pattern: LUCA_<SECTION>_<KEY>
        For nested values: LUCA_<SECTION>_<SUBSECTION>_<KEY>

        Args:
            config: Configuration dictionary to update.

        Returns:
            Configuration with environment overrides applied.
        """
        env_prefix = "LUCA_"

        # Filter to only LUCA_ prefixed vars that are relevant to config
        # Top-level keys that don't have nested structure
        top_level_keys = {"debug", "log_level", "api_keys", "environment"}
        # Section keys that have nested structure
        section_keys = {"components", "agents", "domains", "error_handling"}

        for env_key, env_value in os.environ.items():
            if not env_key.startswith(env_prefix):
                continue

            # Parse the environment variable name
            parts = env_key[len(env_prefix) :].lower().split("_")

            # Check if it's a top-level key (may have underscore)
            # Try joining first two parts for keys like log_level
            if len(parts) == 2 and "_".join(parts) in top_level_keys:
                key = "_".join(parts)
                # Set top-level value
                if env_value.startswith("[") or env_value.startswith("{"):
                    try:
                        import json

                        config[key] = json.loads(env_value)
                    except (json.JSONDecodeError, ValueError):
                        config[key] = env_value
                else:
                    config[key] = env_value
                continue
            elif len(parts) == 1 and parts[0] in top_level_keys:
                # Single part top-level key
                key = parts[0]
                # Set top-level value
                if env_value.startswith("[") or env_value.startswith("{"):
                    try:
                        import json

                        config[key] = json.loads(env_value)
                    except (json.JSONDecodeError, ValueError):
                        config[key] = env_value
                else:
                    config[key] = env_value
                continue

            # Skip if not a recognized config section
            if parts[0] not in section_keys:
                continue

            # Special handling for nested paths
            if parts[0] == "domains" and len(parts) >= 3:
                # domains -> domain_name -> field
                domain_name = parts[1]
                # Join remaining parts with underscore for field name
                field_name = "_".join(parts[2:])

                # Ensure the structure exists
                if "domains" not in config:
                    config["domains"] = {}
                if domain_name not in config["domains"]:
                    config["domains"][domain_name] = {}

                # Set the value directly
                current = config["domains"][domain_name]
                key = field_name
            elif parts[0] == "components" and len(parts) == 4:
                # components -> component_name -> field_name -> value
                # e.g., LUCA_COMPONENTS_CONTEXT_STORE_TYPE
                component_name = "_".join(parts[1:3])  # context_store
                field_name = parts[3]  # type

                if "components" not in config:
                    config["components"] = {}
                if component_name not in config["components"]:
                    config["components"][component_name] = {}

                current = config["components"][component_name]
                key = field_name
            else:
                # Standard navigation
                current = config
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    elif not isinstance(current[part], dict):
                        # Can't navigate further if not a dict
                        break
                    current = current[part]
                key = parts[-1]

            # Set the value
            if isinstance(current, dict):
                # Try to parse as JSON for complex types
                if env_value.startswith("[") or env_value.startswith("{"):
                    try:
                        import json

                        current[key] = json.loads(env_value)
                    except (json.JSONDecodeError, ValueError):
                        # Fall back to string value
                        current[key] = env_value
                else:
                    # Plain string value
                    current[key] = env_value

        return config

    def load(
        self,
        config_file: Optional[Union[str, Path]] = None,
        defaults_file: Optional[Union[str, Path]] = None,
        apply_env_overrides: bool = True,
    ) -> ConfigSchema:
        """Load and validate configuration.

        Args:
            config_file: Primary configuration file. Defaults to 'luca.yaml'.
            defaults_file: Default configuration file. Defaults to 'defaults.yaml'.
            apply_env_overrides: Whether to apply environment variable overrides.

        Returns:
            Validated configuration object.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        # Return cached config if available
        if self._config_cache is not None:
            return self._config_cache

        config_data: Dict[str, Any] = {}

        # Load defaults if specified
        if defaults_file:
            try:
                defaults = self.load_file(defaults_file)
                config_data = self._merge_configs(config_data, defaults)
            except ConfigurationError:
                # Defaults are optional, so we can ignore if not found
                pass

        # Load main configuration
        main_file = config_file or "luca.yaml"
        try:
            main_config = self.load_file(main_file)
            config_data = self._merge_configs(config_data, main_config)
        except ConfigurationError as e:
            # Main config is optional if we have defaults or env vars
            if not config_data and not apply_env_overrides:
                raise e

        # Apply environment overrides
        if apply_env_overrides:
            config_data = self._apply_env_overrides(config_data)

        # Validate configuration
        try:
            config = ConfigSchema(**config_data)
            self._config_cache = config
            return config
        except ValidationError as e:
            error_details = []
            for error in e.errors():
                loc = " -> ".join(str(x) for x in error["loc"])
                msg = error["msg"]
                error_details.append(f"{loc}: {msg}")

            raise ConfigurationError(
                "Configuration validation failed",
                create_user_error(
                    f"Invalid configuration: {'; '.join(error_details)}",
                    remediation=(
                        "Check the configuration against the schema requirements."
                    ),
                    error_code="CONFIG_VALIDATION_ERROR",
                ),
            )

    def reload(self) -> ConfigSchema:
        """Reload configuration from disk.

        Returns:
            Newly loaded configuration.
        """
        self._config_cache = None
        return self.load()

    def save(self, config: ConfigSchema, filename: Union[str, Path]) -> None:
        """Save configuration to a YAML file.

        Args:
            config: Configuration object to save.
            filename: Target filename for saving.

        Raises:
            ConfigurationError: If save fails.
        """
        if isinstance(filename, str):
            if not filename.endswith((".yaml", ".yml")):
                filename = f"{filename}.yaml"
            filepath = self.config_dir / filename
        else:
            filepath = filename

        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Convert to dictionary, excluding None values
            config_dict = config.model_dump(exclude_none=True, mode="json")

            # Write YAML file
            with open(filepath, "w", encoding="utf-8") as f:
                yaml.safe_dump(
                    config_dict,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to save configuration to {filepath}",
                create_user_error(
                    f"Error writing file: {e}",
                    error_code="CONFIG_SAVE_ERROR",
                ),
            )


# Convenience function for loading configuration
def load_config(
    config_file: Optional[Union[str, Path]] = None,
    config_dir: Optional[Path] = None,
    apply_env_overrides: bool = True,
) -> ConfigSchema:
    """Load configuration using default settings.

    Args:
        config_file: Configuration file to load.
        config_dir: Directory containing configuration files.
        apply_env_overrides: Whether to apply environment variable overrides.

    Returns:
        Loaded and validated configuration.
    """
    loader = ConfigLoader(config_dir=config_dir)
    return loader.load(config_file=config_file, apply_env_overrides=apply_env_overrides)
