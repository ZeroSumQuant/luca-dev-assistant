"""Comprehensive tests for input validation module."""

import pytest

from luca_core.validation import (
    ValidationError,
    validate_environment_var,
    validate_file_content,
    validate_file_path,
    validate_json_data,
    validate_prompt,
    validate_shell_command,
    validate_sql_input,
    validate_url,
)


class TestFilePathValidation:
    """Test file path validation."""

    def test_valid_relative_path(self, tmp_path):
        """Test validation of valid relative paths."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        # Use base_dir to allow absolute paths
        result = validate_file_path(str(test_file), must_exist=True, base_dir=tmp_path)
        assert result == test_file.resolve()

    def test_empty_path(self):
        """Test that empty paths are rejected."""
        with pytest.raises(ValidationError, match="Path cannot be empty"):
            validate_file_path("")

    def test_path_traversal_attack(self):
        """Test that path traversal attempts are blocked."""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "test/../../../etc/passwd",
        ]

        for path in dangerous_paths:
            with pytest.raises(ValidationError, match="forbidden pattern"):
                validate_file_path(path)

    def test_absolute_path_rejection(self):
        """Test that absolute paths are rejected when not allowed."""
        import platform

        # Test Unix-style absolute paths
        if platform.system() != "Windows":
            unix_paths = ["/etc/passwd", "//server/share/file"]
            for path in unix_paths:
                with pytest.raises(ValidationError, match="Absolute paths not allowed"):
                    validate_file_path(path)

        # Windows paths won't be detected as absolute on Unix systems
        # but they should still be rejected by path validation

    def test_control_characters(self):
        """Test that paths with control characters are rejected."""
        with pytest.raises(ValidationError, match="forbidden pattern"):
            validate_file_path("test\x00file.txt")

    def test_path_length_limit(self):
        """Test that overly long paths are rejected."""
        long_path = "a" * 5000
        with pytest.raises(ValidationError, match="Path too long"):
            validate_file_path(long_path)

    def test_base_directory_constraint(self, tmp_path):
        """Test that paths outside base directory are rejected."""
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        outside_file = tmp_path / "outside.txt"
        outside_file.write_text("test")

        with pytest.raises(ValidationError, match="outside base directory"):
            validate_file_path(str(outside_file), base_dir=base_dir)

    def test_must_exist_constraint(self):
        """Test that non-existent paths fail when must_exist=True."""
        with pytest.raises(ValidationError, match="does not exist"):
            validate_file_path("nonexistent.txt", must_exist=True)

    def test_directory_constraint(self, tmp_path):
        """Test that directories are rejected when not allowed."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        with pytest.raises(ValidationError, match="is a directory"):
            validate_file_path(
                str(test_dir), allow_directories=False, base_dir=tmp_path
            )


class TestFileContentValidation:
    """Test file content validation."""

    def test_valid_string_content(self):
        """Test validation of valid string content."""
        content = "This is valid content"
        result = validate_file_content(content)
        assert result == content

    def test_valid_bytes_content(self):
        """Test validation of valid bytes content."""
        content = b"This is valid bytes"
        result = validate_file_content(content)
        assert result == content

    def test_size_limit(self):
        """Test that content exceeding size limit is rejected."""
        large_content = "a" * 1000
        with pytest.raises(ValidationError, match="Content too large"):
            validate_file_content(large_content, max_size=100)

    def test_null_bytes_in_string(self):
        """Test that null bytes in strings are rejected."""
        with pytest.raises(ValidationError, match="null bytes"):
            validate_file_content("test\x00content")


class TestURLValidation:
    """Test URL validation."""

    def test_valid_urls(self):
        """Test validation of various valid URLs."""
        valid_urls = [
            "http://example.com",
            "https://example.com/path",
            "ws://localhost:8080",
            "wss://secure.example.com",
            "file:///path/to/file",
            "http://example.com:8080/path?query=value#fragment",
        ]

        for url in valid_urls:
            result = validate_url(url)
            assert result == url

    def test_empty_url(self):
        """Test that empty URLs are rejected."""
        with pytest.raises(ValidationError, match="URL cannot be empty"):
            validate_url("")

    def test_invalid_scheme(self):
        """Test that URLs with disallowed schemes are rejected."""
        with pytest.raises(ValidationError, match="scheme.*not allowed"):
            validate_url("ftp://example.com")

    def test_missing_netloc(self):
        """Test that URLs without network location are rejected."""
        with pytest.raises(ValidationError, match="missing network location"):
            validate_url("http://")

    def test_forbidden_characters(self):
        """Test that URLs with forbidden characters are rejected."""
        dangerous_urls = [
            "http://example.com/../admin",
            "http://example.com\x00",
        ]

        for url in dangerous_urls:
            with pytest.raises(ValidationError, match="forbidden characters"):
                validate_url(url)

    def test_custom_allowed_schemes(self):
        """Test URL validation with custom allowed schemes."""
        # FTP not in default allowed schemes
        with pytest.raises(ValidationError):
            validate_url("ftp://example.com")

        # But works with custom schemes
        result = validate_url("ftp://example.com", allowed_schemes={"ftp"})
        assert result == "ftp://example.com"


class TestPromptValidation:
    """Test user prompt validation."""

    def test_valid_prompt(self):
        """Test validation of valid prompts."""
        prompt = "This is a valid prompt"
        result = validate_prompt(prompt)
        assert result == prompt

    def test_empty_prompt(self):
        """Test that empty prompts are rejected."""
        with pytest.raises(ValidationError, match="Prompt cannot be empty"):
            validate_prompt("")

    def test_length_limit(self):
        """Test that overly long prompts are rejected."""
        long_prompt = "a" * 20000
        with pytest.raises(ValidationError, match="Prompt too long"):
            validate_prompt(long_prompt)

    def test_html_stripping(self):
        """Test that HTML is stripped when requested."""
        prompt = "Hello <script>alert('xss')</script> world"
        result = validate_prompt(prompt, strip_html=True)
        assert result == "Hello  world"

    def test_null_bytes(self):
        """Test that prompts with null bytes are rejected."""
        with pytest.raises(ValidationError, match="null bytes"):
            validate_prompt("test\x00prompt")

    def test_whitespace_trimming(self):
        """Test that whitespace is trimmed."""
        prompt = "  Hello world  \n"
        result = validate_prompt(prompt)
        assert result == "Hello world"


class TestShellCommandValidation:
    """Test shell command validation."""

    def test_valid_commands(self):
        """Test validation of safe commands."""
        safe_commands = [
            "ls -la",
            "git status",
            "echo hello",
            "python script.py",
        ]

        for cmd in safe_commands:
            result = validate_shell_command(cmd)
            assert result == cmd

    def test_empty_command(self):
        """Test that empty commands are rejected."""
        with pytest.raises(ValidationError, match="Command cannot be empty"):
            validate_shell_command("")

    def test_dangerous_rm_commands(self):
        """Test that dangerous rm commands are blocked."""
        dangerous_commands = [
            "ls; rm -rf /",
            "echo test && rm -rf ~",
            "cat file | rm -rf .",
        ]

        for cmd in dangerous_commands:
            with pytest.raises(ValidationError, match="dangerous pattern"):
                validate_shell_command(cmd)

    def test_command_substitution(self):
        """Test that command substitution is blocked."""
        dangerous_commands = [
            "echo `whoami`",
            "echo $(cat /etc/passwd)",
        ]

        for cmd in dangerous_commands:
            with pytest.raises(ValidationError, match="dangerous pattern"):
                validate_shell_command(cmd)

    def test_pipe_restriction(self):
        """Test pipe restriction when not allowed."""
        with pytest.raises(ValidationError, match="dangerous pattern"):
            validate_shell_command("ls | grep test", allow_pipes=False)

        # Should work when allowed
        result = validate_shell_command("ls | grep test", allow_pipes=True)
        assert result == "ls | grep test"

    def test_redirect_restriction(self):
        """Test redirect restriction when not allowed."""
        redirects = ["ls > file", "cat < input", "echo >> log", "cmd 2> error"]

        for cmd in redirects:
            with pytest.raises(ValidationError, match="dangerous pattern"):
                validate_shell_command(cmd, allow_redirects=False)

        # Should work when allowed
        for cmd in redirects:
            result = validate_shell_command(cmd, allow_redirects=True)
            assert result == cmd


class TestSQLInputValidation:
    """Test SQL input validation."""

    def test_valid_inputs(self):
        """Test validation of safe SQL inputs."""
        safe_inputs = [
            "username123",
            "test@example.com",
            "John Doe",
            "12345",
        ]

        for value in safe_inputs:
            result = validate_sql_input(value)
            assert result == value

    def test_sql_injection_patterns(self):
        """Test that SQL injection patterns are blocked."""
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            '"; DELETE FROM data; --',
            "1' OR '1'='1",
            "admin'--",
            "1 UNION SELECT * FROM passwords",
            "/* comment */ SELECT",
        ]

        for value in dangerous_inputs:
            with pytest.raises(ValidationError, match="dangerous SQL pattern"):
                validate_sql_input(value)

    def test_non_string_input(self):
        """Test that non-string inputs are rejected."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_sql_input(123)


class TestJSONDataValidation:
    """Test JSON data validation."""

    def test_valid_json_string(self):
        """Test validation of valid JSON string."""
        json_str = '{"name": "test", "value": 123}'
        result = validate_json_data(json_str)
        assert result == {"name": "test", "value": 123}

    def test_valid_dict(self):
        """Test validation of valid dictionary."""
        data = {"name": "test", "value": 123}
        result = validate_json_data(data)
        assert result == data

    def test_invalid_json_string(self):
        """Test that invalid JSON strings are rejected."""
        with pytest.raises(ValidationError, match="Invalid JSON"):
            validate_json_data('{"invalid": json}')

    def test_size_limit(self):
        """Test that overly large JSON is rejected."""
        large_json = '{"data": "' + "a" * 1000 + '"}'
        with pytest.raises(ValidationError, match="JSON too large"):
            validate_json_data(large_json, max_size=100)

    def test_non_object_json(self):
        """Test that non-object JSON is rejected."""
        with pytest.raises(ValidationError, match="must be an object"):
            validate_json_data("[1, 2, 3]")

    def test_required_fields(self):
        """Test validation of required fields."""
        data = {"name": "test"}

        # Should pass without required fields
        validate_json_data(data)

        # Should fail with missing required fields
        with pytest.raises(ValidationError, match="Missing required fields: value"):
            validate_json_data(data, required_fields={"name", "value"})


class TestEnvironmentVariableValidation:
    """Test environment variable validation."""

    def test_string_validation(self):
        """Test string environment variable validation."""
        result = validate_environment_var("TEST_VAR", "value", var_type="string")
        assert result == "value"

        # Test None
        result = validate_environment_var("TEST_VAR", None, var_type="string")
        assert result is None

    def test_boolean_validation(self):
        """Test boolean environment variable validation."""
        true_values = ["true", "1", "yes", "on", "True", "YES", "ON"]
        false_values = ["false", "0", "no", "off", "False", "NO", "OFF"]

        for value in true_values:
            result = validate_environment_var("TEST_VAR", value, var_type="bool")
            assert result is True

        for value in false_values:
            result = validate_environment_var("TEST_VAR", value, var_type="bool")
            assert result is False

        # Invalid boolean
        with pytest.raises(ValidationError, match="Invalid boolean"):
            validate_environment_var("TEST_VAR", "maybe", var_type="bool")

    def test_integer_validation(self):
        """Test integer environment variable validation."""
        result = validate_environment_var("TEST_VAR", "123", var_type="int")
        assert result == 123

        # Invalid integer
        with pytest.raises(ValidationError, match="Invalid integer"):
            validate_environment_var("TEST_VAR", "abc", var_type="int")

    def test_path_validation(self, tmp_path):
        """Test path environment variable validation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        # For environment variables, we expect absolute paths to work
        # Let's create a relative path from current directory
        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = validate_environment_var("TEST_VAR", "test.txt", var_type="path")
            assert result == test_file.resolve()
        finally:
            os.chdir(old_cwd)

    def test_allowed_values(self):
        """Test validation with allowed values."""
        result = validate_environment_var(
            "TEST_VAR", "dev", var_type="string", allowed_values={"dev", "prod", "test"}
        )
        assert result == "dev"

        # Invalid value
        with pytest.raises(ValidationError, match="Invalid value.*Allowed"):
            validate_environment_var(
                "TEST_VAR", "staging", var_type="string", allowed_values={"dev", "prod"}
            )

    def test_unknown_type(self):
        """Test that unknown types are rejected."""
        with pytest.raises(ValidationError, match="Unknown var_type"):
            validate_environment_var("TEST_VAR", "value", var_type="unknown")
