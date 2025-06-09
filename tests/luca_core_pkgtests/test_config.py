"""Unit tests for the YAML configuration loader."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from pydantic import ValidationError

from luca_core.config import (
    AgentConfig,
    ComponentConfig,
    ConfigLoader,
    ConfigSchema,
    DomainConfig,
    ErrorHandlingConfig,
    LucaConfig,
    load_config,
)
from luca_core.config.loader import ConfigurationError
from luca_core.config.schemas import (
    ContextStoreConfig,
    RetryConfig,
    StorageType,
)
from luca_core.schemas.base import AgentRole, DomainType


class TestConfigSchemas:
    """Test configuration schema models."""

    def test_context_store_config_defaults(self):
        """Test ContextStoreConfig with default values."""
        config = ContextStoreConfig()
        assert config.type == StorageType.SQLITE
        assert config.path == Path("./data/context.db")
        assert config.backup_interval == 300
        assert config.connection_params == {}

    def test_context_store_config_custom(self):
        """Test ContextStoreConfig with custom values."""
        config = ContextStoreConfig(
            type=StorageType.POSTGRES,
            path="/custom/path/db",
            backup_interval=600,
            connection_params={"host": "localhost", "port": 5432},
        )
        assert config.type == StorageType.POSTGRES
        assert config.path == Path("/custom/path/db")
        assert config.backup_interval == 600
        assert config.connection_params == {"host": "localhost", "port": 5432}

    def test_agent_config_validation(self):
        """Test AgentConfig validation."""
        config = AgentConfig(
            name="TestAgent",
            role=AgentRole.DEVELOPER,
            description="Test agent",
            system_prompt="You are a test agent",
            temperature=0.5,
        )
        assert config.name == "TestAgent"
        assert config.role == "developer"  # Enum converted to string
        assert config.temperature == 0.5

    def test_agent_config_invalid_temperature(self):
        """Test AgentConfig with invalid temperature."""
        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(
                name="TestAgent",
                role="developer",
                description="Test agent",
                system_prompt="You are a test agent",
                temperature=3.0,  # Too high
            )
        errors = exc_info.value.errors()
        assert any("temperature" in str(e) for e in errors)

    def test_luca_config_defaults(self):
        """Test LucaConfig with defaults."""
        config = LucaConfig(
            system_prompt="You are Luca",
        )
        assert config.name == "Luca"
        assert config.role == AgentRole.MANAGER.value
        assert (
            config.description == "Main orchestration agent that coordinates all tasks"
        )
        assert config.specialists == {}

    def test_domain_config(self):
        """Test DomainConfig."""
        config = DomainConfig(
            description="Test domain",
            active_specialists=["coder", "tester"],
            default_tools=["tool1", "tool2"],
        )
        assert config.description == "Test domain"
        assert config.active_specialists == ["coder", "tester"]
        assert config.default_tools == ["tool1", "tool2"]

    def test_retry_config(self):
        """Test RetryConfig."""
        config = RetryConfig(
            max_retries=5,
            backoff_factor=2.0,
            retry_statuses=["timeout", "network_error"],
        )
        assert config.max_retries == 5
        assert config.backoff_factor == 2.0
        assert config.retry_statuses == ["timeout", "network_error"]

    def test_config_schema_complete(self):
        """Test complete ConfigSchema."""
        config = ConfigSchema()

        # Check defaults
        assert config.debug is False
        assert config.log_level == "INFO"
        assert config.environment == "development"

        # Check components
        assert isinstance(config.components, ComponentConfig)
        assert isinstance(config.agents, LucaConfig)
        assert isinstance(config.error_handling, ErrorHandlingConfig)

        # Check default domains are added
        assert DomainType.GENERAL.value in config.domains
        assert DomainType.QUANTITATIVE_FINANCE.value in config.domains

    def test_config_schema_no_extra_fields(self):
        """Test that ConfigSchema rejects extra fields."""
        with pytest.raises(ValidationError) as exc_info:
            ConfigSchema(unknown_field="value")
        errors = exc_info.value.errors()
        assert any("Extra inputs are not permitted" in str(e["msg"]) for e in errors)


class TestConfigLoader:
    """Test ConfigLoader functionality."""

    def test_init_default_config_dir(self):
        """Test ConfigLoader initialization with default directory."""
        loader = ConfigLoader()
        assert loader.config_dir.is_absolute()

    def test_init_custom_config_dir(self):
        """Test ConfigLoader initialization with custom directory."""
        custom_dir = Path("/custom/config")
        loader = ConfigLoader(config_dir=custom_dir)
        assert loader.config_dir == custom_dir

    def test_load_yaml_file(self, tmp_path):
        """Test loading a valid YAML file."""
        # Create test YAML file
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        yaml_file = config_dir / "test.yaml"

        test_data = {
            "components": {
                "context_store": {
                    "type": "sqlite",
                    "path": "/test/path",
                }
            }
        }

        with open(yaml_file, "w") as f:
            yaml.dump(test_data, f)

        loader = ConfigLoader(config_dir=config_dir)
        data = loader.load_file("test.yaml")

        assert data == test_data

    def test_load_yaml_file_not_found(self):
        """Test loading non-existent YAML file."""
        loader = ConfigLoader()

        with pytest.raises(ConfigurationError) as exc_info:
            loader.load_file("nonexistent.yaml")

        assert "not found" in str(exc_info.value)
        assert exc_info.value.error_payload is not None

    def test_load_yaml_file_invalid_syntax(self, tmp_path):
        """Test loading YAML file with invalid syntax."""
        yaml_file = tmp_path / "invalid.yaml"

        with open(yaml_file, "w") as f:
            f.write("invalid: yaml: syntax: ][")

        loader = ConfigLoader(config_dir=tmp_path.parent)

        with pytest.raises(ConfigurationError) as exc_info:
            loader.load_file(yaml_file)

        assert "parse YAML" in str(exc_info.value)

    def test_merge_configs(self):
        """Test configuration merging."""
        loader = ConfigLoader()

        base = {
            "a": 1,
            "b": {"c": 2, "d": 3},
            "e": [1, 2, 3],
        }

        override = {
            "a": 10,
            "b": {"c": 20, "f": 4},
            "g": 5,
        }

        result = loader._merge_configs(base, override)

        assert result == {
            "a": 10,  # Overridden
            "b": {"c": 20, "d": 3, "f": 4},  # Merged
            "e": [1, 2, 3],  # Unchanged
            "g": 5,  # New
        }

    def test_apply_env_overrides(self):
        """Test environment variable overrides."""
        loader = ConfigLoader()

        config = {
            "components": {
                "context_store": {
                    "type": "sqlite",
                }
            },
            "debug": False,
        }

        with patch.dict(
            os.environ,
            {
                "LUCA_DEBUG": "true",
                "LUCA_COMPONENTS_CONTEXT_STORE_TYPE": "postgres",
                "LUCA_LOG_LEVEL": "DEBUG",
            },
        ):
            result = loader._apply_env_overrides(config.copy())

        assert result["debug"] == "true"
        assert result["components"]["context_store"]["type"] == "postgres"
        assert result["log_level"] == "DEBUG"

    def test_load_complete_config(self, tmp_path):
        """Test loading complete configuration."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create main config file
        main_config = {
            "components": {
                "context_store": {
                    "type": "sqlite",
                    "path": "/data/luca.db",
                }
            },
            "agents": {
                "name": "Luca",
                "system_prompt": "You are Luca",
                "specialists": {
                    "coder": {
                        "name": "Coder",
                        "role": "developer",
                        "description": "Coding specialist",
                        "system_prompt": "You write code",
                    }
                },
            },
            "debug": True,
        }

        yaml_file = config_dir / "luca.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(main_config, f)

        loader = ConfigLoader(config_dir=config_dir)
        config = loader.load()

        assert isinstance(config, ConfigSchema)
        assert config.debug is True
        assert config.components.context_store.type == StorageType.SQLITE
        assert "coder" in config.agents.specialists

    def test_load_with_defaults(self, tmp_path):
        """Test loading with defaults file."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create defaults file
        defaults = {
            "log_level": "DEBUG",
            "components": {
                "tool_registry": {
                    "version_check": False,
                }
            },
        }

        defaults_file = config_dir / "defaults.yaml"
        with open(defaults_file, "w") as f:
            yaml.dump(defaults, f)

        # Create main config that overrides some defaults
        main_config = {"agents": {"system_prompt": "Test prompt"}}

        main_file = config_dir / "luca.yaml"
        with open(main_file, "w") as f:
            yaml.dump(main_config, f)

        loader = ConfigLoader(config_dir=config_dir)
        config = loader.load(defaults_file="defaults.yaml")

        assert config.log_level == "DEBUG"  # From defaults
        assert config.components.tool_registry.version_check is False  # From defaults
        assert config.agents.system_prompt == "Test prompt"  # From main

    def test_validation_error(self, tmp_path):
        """Test configuration validation error."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create config with invalid values
        invalid_config = {
            "agents": {
                "temperature": 5.0,  # Too high
                "system_prompt": "Test",
            }
        }

        yaml_file = config_dir / "luca.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(invalid_config, f)

        loader = ConfigLoader(config_dir=config_dir)

        with pytest.raises(ConfigurationError) as exc_info:
            loader.load()

        assert "validation failed" in str(exc_info.value)
        assert exc_info.value.error_payload is not None

    def test_save_config(self, tmp_path):
        """Test saving configuration to file."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        loader = ConfigLoader(config_dir=config_dir)

        # Create a config to save
        config = ConfigSchema(
            debug=True,
            log_level="DEBUG",
            agents=LucaConfig(
                system_prompt="Test Luca",
                temperature=0.7,
            ),
        )

        # Save it
        loader.save(config, "saved_config.yaml")

        # Verify file exists and can be loaded
        saved_file = config_dir / "saved_config.yaml"
        assert saved_file.exists()

        # Load it back
        loaded_data = loader.load_file("saved_config.yaml")
        assert loaded_data["debug"] is True
        assert loaded_data["log_level"] == "DEBUG"
        assert loaded_data["agents"]["temperature"] == 0.7

    def test_reload_config(self, tmp_path):
        """Test reloading configuration."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        yaml_file = config_dir / "luca.yaml"

        # Initial config
        with open(yaml_file, "w") as f:
            yaml.dump({"debug": False, "agents": {"system_prompt": "Initial"}}, f)

        loader = ConfigLoader(config_dir=config_dir)
        config1 = loader.load()
        assert config1.debug is False

        # Update config file
        with open(yaml_file, "w") as f:
            yaml.dump({"debug": True, "agents": {"system_prompt": "Updated"}}, f)

        # Reload
        config2 = loader.reload()
        assert config2.debug is True

    def test_yaml_safety_validation(self, tmp_path):
        """Test that unsafe YAML constructs are rejected."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create YAML with Python code (unsafe)
        yaml_file = config_dir / "unsafe.yaml"
        with open(yaml_file, "w") as f:
            f.write('test: !!python/object/apply:os.system ["echo hacked"]')

        loader = ConfigLoader(config_dir=config_dir)

        with pytest.raises(ConfigurationError) as exc_info:
            loader.load_file("unsafe.yaml")

        # Should be caught by safety validation, not YAML parsing
        assert "Unsafe YAML content" in str(exc_info.value)


class TestLoadConfigFunction:
    """Test the convenience load_config function."""

    def test_load_config_basic(self, tmp_path):
        """Test basic load_config usage."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        yaml_file = config_dir / "test.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump({"debug": True, "agents": {"system_prompt": "Test"}}, f)

        config = load_config(config_file="test.yaml", config_dir=config_dir)

        assert isinstance(config, ConfigSchema)
        assert config.debug is True

    def test_load_config_env_override(self, tmp_path):
        """Test load_config with environment overrides."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        yaml_file = config_dir / "test.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump({"debug": False, "agents": {"system_prompt": "Test"}}, f)

        with patch.dict(os.environ, {"LUCA_DEBUG": "true"}):
            config = load_config(
                config_file="test.yaml",
                config_dir=config_dir,
                apply_env_overrides=True,
            )

        # Environment variables are applied but ConfigSchema converts "true" to boolean
        assert config.debug is True

    def test_load_config_no_env_override(self, tmp_path):
        """Test load_config without environment overrides."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        yaml_file = config_dir / "test.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump({"debug": False, "agents": {"system_prompt": "Test"}}, f)

        with patch.dict(os.environ, {"LUCA_DEBUG": "true"}):
            config = load_config(
                config_file="test.yaml",
                config_dir=config_dir,
                apply_env_overrides=False,
            )

        assert config.debug is False  # Not overridden


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_yaml_file(self, tmp_path):
        """Test loading empty YAML file."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.touch()  # Create empty file

        loader = ConfigLoader(config_dir=tmp_path.parent)
        config = loader.load(config_file=yaml_file)

        # Should load with all defaults
        assert isinstance(config, ConfigSchema)
        assert config.environment == "development"

    def test_yaml_with_null_values(self, tmp_path):
        """Test YAML file with null values."""
        yaml_file = tmp_path / "nulls.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(
                {
                    "debug": None,
                    "agents": {"temperature": None, "system_prompt": "Test"},
                },
                f,
            )

        loader = ConfigLoader(config_dir=tmp_path.parent)
        config = loader.load(config_file=yaml_file)

        # Null values should use defaults
        assert config.debug is False  # Default
        assert config.agents.temperature == 0.2  # Default

    def test_nested_env_override(self):
        """Test deeply nested environment variable override."""
        loader = ConfigLoader()

        config = {"domains": {"general": {"active_specialists": ["coder"]}}}

        with patch.dict(
            os.environ,
            {
                "LUCA_DOMAINS_GENERAL_ACTIVE_SPECIALISTS": (
                    '["coder", "tester", "analyst"]'
                )
            },
        ):
            result = loader._apply_env_overrides(config.copy())

        assert result["domains"]["general"]["active_specialists"] == [
            "coder",
            "tester",
            "analyst",
        ]

    def test_path_traversal_prevention(self, tmp_path):
        """Test that path traversal attempts are blocked."""
        loader = ConfigLoader(config_dir=tmp_path)

        with pytest.raises(ConfigurationError) as exc_info:
            loader.load_file("../../etc/passwd")

        assert "Invalid configuration path" in str(exc_info.value)

    def test_find_config_dir_fallback(self, tmp_path, monkeypatch):
        """Test _find_config_dir when no config directory exists."""
        # Change to a directory without a config subdirectory
        monkeypatch.chdir(tmp_path)

        # Mock Path(__file__) to prevent finding project root
        import luca_core.config.loader

        fake_file = tmp_path / "loader.py"
        monkeypatch.setattr(luca_core.config.loader, "__file__", str(fake_file))

        loader = ConfigLoader()
        # Should fall back to current directory
        assert loader.config_dir == tmp_path

    def test_config_dir_from_project_root(self, tmp_path, monkeypatch):
        """Test finding config dir relative to project root."""
        # Create a mock project structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        config_dir = project_dir / "config"
        config_dir.mkdir()

        # Create a fake module path
        module_dir = project_dir / "luca_core" / "config"
        module_dir.mkdir(parents=True)

        # Mock __file__ to point to our fake module
        fake_file = module_dir / "loader.py"
        fake_file.touch()

        monkeypatch.chdir(tmp_path)  # Change to parent dir

        # Monkey patch Path(__file__)
        import luca_core.config.loader

        monkeypatch.setattr(luca_core.config.loader, "__file__", str(fake_file))

        loader = ConfigLoader()
        assert loader.config_dir == config_dir

    def test_load_file_with_exception(self, tmp_path, monkeypatch):
        """Test load_file with general exception."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("valid: yaml")

        loader = ConfigLoader(config_dir=tmp_path.parent)

        # Mock open to raise an exception
        def mock_open(*args, **kwargs):
            raise IOError("Disk error")

        monkeypatch.setattr("builtins.open", mock_open)

        with pytest.raises(ConfigurationError) as exc_info:
            loader.load_file(yaml_file)

        assert "Failed to load configuration file" in str(exc_info.value)

    def test_env_override_standard_navigation(self):
        """Test environment override with standard navigation."""
        loader = ConfigLoader()

        config = {"agents": {"max_retries": 3}}

        with patch.dict(os.environ, {"LUCA_AGENTS_TEMPERATURE": "0.5"}):
            result = loader._apply_env_overrides(config.copy())

        assert result["agents"]["temperature"] == "0.5"

    def test_env_override_skip_unknown_section(self):
        """Test that unknown config sections are skipped."""
        loader = ConfigLoader()

        config = {}

        with patch.dict(os.environ, {"LUCA_UNKNOWN_SECTION_VALUE": "test"}):
            result = loader._apply_env_overrides(config.copy())

        # Unknown section should be ignored
        assert "unknown_section" not in result

    def test_save_config_error(self, tmp_path, monkeypatch):
        """Test save config with write error."""
        loader = ConfigLoader(config_dir=tmp_path)

        config = ConfigSchema()

        # Mock yaml.safe_dump to raise an exception
        def mock_dump(*args, **kwargs):
            raise IOError("Write error")

        monkeypatch.setattr("yaml.safe_dump", mock_dump)

        with pytest.raises(ConfigurationError) as exc_info:
            loader.save(config, "test.yaml")

        assert "Failed to save configuration" in str(exc_info.value)

    def test_load_with_missing_main_config(self, tmp_path):
        """Test loading when main config is missing but we have env vars."""
        loader = ConfigLoader(config_dir=tmp_path)

        with patch.dict(os.environ, {"LUCA_DEBUG": "true"}):
            # Should not raise, will use defaults + env vars
            config = loader.load()
            assert config.debug is True  # Converted to boolean by ConfigSchema

    def test_merge_configs_nested_none_values(self):
        """Test merging configs with nested None values."""
        loader = ConfigLoader()

        base = {"components": {"context_store": {"type": "sqlite"}}}

        override = {
            "components": {
                "context_store": {
                    "type": None,  # Should be skipped
                    "path": "/new/path",
                }
            }
        }

        result = loader._merge_configs(base, override)

        # type should remain unchanged, path should be added
        assert result["components"]["context_store"]["type"] == "sqlite"
        assert result["components"]["context_store"]["path"] == "/new/path"

    def test_env_override_with_non_dict_value(self):
        """Test environment override when current value is not a dict."""
        loader = ConfigLoader()

        config = {"agents": "invalid"}  # Not a dict

        with patch.dict(os.environ, {"LUCA_AGENTS_NAME": "TestAgent"}):
            result = loader._apply_env_overrides(config.copy())

        # Should not crash, but won't be able to set nested value
        assert result["agents"] == "invalid"

    def test_env_override_json_parsing(self):
        """Test JSON parsing in environment overrides."""
        loader = ConfigLoader()

        config = {}

        with patch.dict(
            os.environ,
            {
                "LUCA_API_KEYS": '{"openai": "key1", "anthropic": "key2"}',
                "LUCA_DEBUG": '["not", "valid", "json"]',  # Invalid JSON
            },
        ):
            result = loader._apply_env_overrides(config.copy())

        # Valid JSON should be parsed
        assert result["api_keys"] == {"openai": "key1", "anthropic": "key2"}
        # Valid JSON array should be parsed
        assert result["debug"] == ["not", "valid", "json"]

    def test_env_override_invalid_json(self):
        """Test invalid JSON in environment overrides."""
        loader = ConfigLoader()

        config = {}

        with patch.dict(
            os.environ,
            {
                "LUCA_API_KEYS": '{"broken": json without quotes}',  # Invalid JSON
            },
        ):
            result = loader._apply_env_overrides(config.copy())

        # Invalid JSON should be kept as string
        assert result["api_keys"] == '{"broken": json without quotes}'

    def test_env_override_single_part_json(self):
        """Test JSON parsing for single-part top-level keys."""
        loader = ConfigLoader()

        config = {}

        with patch.dict(
            os.environ,
            {
                "LUCA_ENVIRONMENT": '{"invalid": json}',  # Invalid JSON
            },
        ):
            result = loader._apply_env_overrides(config.copy())

        # Invalid JSON should be kept as string
        assert result["environment"] == '{"invalid": json}'

    def test_env_override_components_non_standard(self):
        """Test components override with non-standard path length."""
        loader = ConfigLoader()

        config = {}

        with patch.dict(
            os.environ,
            {
                "LUCA_COMPONENTS_SIMPLE": "value",  # Only 2 parts
                "LUCA_COMPONENTS_VERY_LONG_NESTED_PATH": "value",  # 5 parts
            },
        ):
            result = loader._apply_env_overrides(config.copy())

        # These should go through standard navigation
        assert result["components"]["simple"] == "value"
        assert result["components"]["very"]["long"]["nested"]["path"] == "value"

    def test_env_override_break_on_non_dict(self):
        """Test that navigation breaks when encountering non-dict."""
        loader = ConfigLoader()

        config = {"components": {"tool_registry": "not_a_dict"}}

        with patch.dict(
            os.environ, {"LUCA_COMPONENTS_TOOL_REGISTRY_VERSION_CHECK": "true"}
        ):
            result = loader._apply_env_overrides(config.copy())

        # Should not be able to set nested value
        assert result["components"]["tool_registry"] == "not_a_dict"

    def test_load_with_defaults_file(self, tmp_path):
        """Test loading with defaults file specified."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create defaults file
        defaults_file = config_dir / "base.yaml"
        with open(defaults_file, "w") as f:
            yaml.dump({"log_level": "WARNING"}, f)

        # No main config file
        loader = ConfigLoader(config_dir=config_dir)

        # Should load defaults
        config = loader.load(defaults_file="base.yaml")
        assert config.log_level == "WARNING"

    def test_load_no_config_no_env(self, tmp_path):
        """Test loading fails when no config and no env overrides."""
        loader = ConfigLoader(config_dir=tmp_path)

        with pytest.raises(ConfigurationError) as exc_info:
            loader.load(apply_env_overrides=False)

        assert "not found" in str(exc_info.value)

    def test_validation_error_multiple_fields(self, tmp_path):
        """Test validation error with multiple invalid fields."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create config with multiple invalid values
        invalid_config = {
            "agents": {
                "temperature": 5.0,  # Too high
                "max_retries": -1,  # Negative
                "timeout_seconds": 0,  # Too low
                "system_prompt": "Test",
            },
            "log_level": "INVALID",  # Not in allowed values
        }

        yaml_file = config_dir / "luca.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(invalid_config, f)

        loader = ConfigLoader(config_dir=config_dir)

        with pytest.raises(ConfigurationError) as exc_info:
            loader.load()

        error_str = str(exc_info.value)
        assert "validation failed" in error_str
        # Check that error payload contains details
        assert exc_info.value.error_payload is not None

    def test_save_without_extension(self, tmp_path):
        """Test saving config without file extension."""
        loader = ConfigLoader(config_dir=tmp_path)

        config = ConfigSchema()

        # Save without extension
        loader.save(config, "myconfig")

        # Should add .yaml extension
        saved_file = tmp_path / "myconfig.yaml"
        assert saved_file.exists()

    def test_save_creates_directory(self, tmp_path):
        """Test that save creates directory if it doesn't exist."""
        config_dir = tmp_path / "new" / "config"
        loader = ConfigLoader(config_dir=config_dir)

        config = ConfigSchema()

        # Directory doesn't exist yet
        assert not config_dir.exists()

        # Save should create it
        loader.save(config, "test.yaml")

        assert config_dir.exists()
        assert (config_dir / "test.yaml").exists()

    def test_load_with_defaults_not_found(self, tmp_path):
        """Test loading when defaults file is not found."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create main config
        main_file = config_dir / "luca.yaml"
        with open(main_file, "w") as f:
            yaml.dump({"debug": True, "agents": {"system_prompt": "Test"}}, f)

        loader = ConfigLoader(config_dir=config_dir)

        # Defaults file doesn't exist, but should not fail
        config = loader.load(defaults_file="nonexistent.yaml")
        assert config.debug is True

    def test_cached_config(self, tmp_path):
        """Test that config is cached after first load."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        yaml_file = config_dir / "luca.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump({"debug": True, "agents": {"system_prompt": "Test"}}, f)

        loader = ConfigLoader(config_dir=config_dir)

        # First load
        config1 = loader.load()

        # Modify the file
        with open(yaml_file, "w") as f:
            yaml.dump({"debug": False, "agents": {"system_prompt": "Changed"}}, f)

        # Second load should return cached version
        config2 = loader.load()
        assert config2.debug is True  # Still the old value
        assert config1 is config2  # Same object

    def test_components_env_override_missing_parts(self):
        """Test components override when parts are missing."""
        loader = ConfigLoader()

        config = {}

        with patch.dict(
            os.environ,
            {
                "LUCA_COMPONENTS_CONTEXT": "value",  # Only 2 parts, not 4
            },
        ):
            result = loader._apply_env_overrides(config.copy())

        # Should use standard navigation
        assert result["components"]["context"] == "value"

    def test_load_defaults_only_no_main(self, tmp_path):
        """Test loading with only defaults when main config doesn't exist."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create defaults file
        defaults_file = config_dir / "defaults.yaml"
        with open(defaults_file, "w") as f:
            yaml.dump({"log_level": "DEBUG", "agents": {"system_prompt": "Default"}}, f)

        # No main config file exists
        loader = ConfigLoader(config_dir=config_dir)

        # Should load just defaults
        config = loader.load(defaults_file="defaults.yaml")
        assert config.log_level == "DEBUG"
