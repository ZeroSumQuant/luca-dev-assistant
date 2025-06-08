"""Core validation functions for external data inputs."""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass


# Configuration constants
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_PROMPT_LENGTH = 10000  # characters
MAX_PATH_LENGTH = 4096  # typical filesystem limit
ALLOWED_SCHEMES = {"http", "https", "ws", "wss", "file"}
FORBIDDEN_PATH_PATTERNS = [
    r"\.\.[\\/]",  # Path traversal
    r"[\x00-\x1f]",  # Control characters
]
# Note: We allow absolute paths when base_dir is specified
# as they'll be validated against the base directory


def validate_file_path(
    path: Union[str, Path],
    must_exist: bool = False,
    allow_directories: bool = True,
    base_dir: Optional[Path] = None,
) -> Path:
    """Validate a file path for safety and constraints.

    Args:
        path: The path to validate
        must_exist: Whether the path must already exist
        allow_directories: Whether to allow directory paths
        base_dir: If provided, ensure path is within this directory

    Returns:
        Validated Path object

    Raises:
        ValidationError: If validation fails
    """
    if not path:
        raise ValidationError("Path cannot be empty")

    # Convert to string for validation
    path_str = str(path)

    # Check length
    if len(path_str) > MAX_PATH_LENGTH:
        raise ValidationError(f"Path too long: {len(path_str)} > {MAX_PATH_LENGTH}")

    # Check for forbidden patterns
    for pattern in FORBIDDEN_PATH_PATTERNS:
        if re.search(pattern, path_str):
            raise ValidationError(f"Path contains forbidden pattern: {pattern}")

    # Convert to Path object
    try:
        path_obj = Path(path_str)
    except Exception as e:
        raise ValidationError(f"Invalid path: {e}")

    # Resolve to absolute path safely
    try:
        # Use resolve() to get absolute path and resolve symlinks
        resolved_path = path_obj.resolve()
    except Exception as e:
        raise ValidationError(f"Cannot resolve path: {e}")

    # If no base directory specified, reject absolute paths
    if not base_dir and path_obj.is_absolute():
        raise ValidationError("Absolute paths not allowed without base_dir")

    # Check if within base directory
    if base_dir:
        base_dir = Path(base_dir).resolve()
        try:
            resolved_path.relative_to(base_dir)
        except ValueError:
            raise ValidationError(
                f"Path '{resolved_path}' is outside base directory '{base_dir}'"
            )

    # Check existence if required
    if must_exist and not resolved_path.exists():
        raise ValidationError(f"Path does not exist: {resolved_path}")

    # Check if it's a directory when not allowed
    if not allow_directories and resolved_path.exists() and resolved_path.is_dir():
        raise ValidationError(f"Path is a directory: {resolved_path}")

    return resolved_path


def validate_file_content(
    content: Union[str, bytes],
    max_size: Optional[int] = None,
    allowed_types: Optional[set] = None,
) -> Union[str, bytes]:
    """Validate file content for safety and constraints.

    Args:
        content: The file content to validate
        max_size: Maximum allowed size in bytes
        allowed_types: Set of allowed MIME types (if None, all allowed)

    Returns:
        Validated content

    Raises:
        ValidationError: If validation fails
    """
    if max_size is None:
        max_size = MAX_FILE_SIZE

    # Check size
    size = len(content.encode("utf-8") if isinstance(content, str) else content)
    if size > max_size:
        raise ValidationError(f"Content too large: {size} > {max_size} bytes")

    # Check for null bytes in strings
    if isinstance(content, str) and "\x00" in content:
        raise ValidationError("Content contains null bytes")

    # TODO: Add MIME type checking if needed

    return content


def validate_url(url: str, allowed_schemes: Optional[set] = None) -> str:
    """Validate a URL for safety and correctness.

    Args:
        url: The URL to validate
        allowed_schemes: Set of allowed URL schemes

    Returns:
        Validated URL

    Raises:
        ValidationError: If validation fails
    """
    if not url:
        raise ValidationError("URL cannot be empty")

    if allowed_schemes is None:
        allowed_schemes = ALLOWED_SCHEMES

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValidationError(f"Invalid URL: {e}")

    # Check scheme
    if parsed.scheme not in allowed_schemes:
        raise ValidationError(
            f"URL scheme '{parsed.scheme}' not allowed. "
            f"Allowed: {', '.join(allowed_schemes)}"
        )

    # Check for basic validity
    if not parsed.netloc and parsed.scheme not in {"file"}:
        raise ValidationError("URL missing network location")

    # Check for suspicious patterns
    if ".." in url or "\x00" in url:
        raise ValidationError("URL contains forbidden characters")

    return url


def validate_prompt(
    prompt: str,
    max_length: Optional[int] = None,
    strip_html: bool = True,
) -> str:
    """Validate user prompt/input for safety.

    Args:
        prompt: The user prompt to validate
        max_length: Maximum allowed length
        strip_html: Whether to strip HTML tags

    Returns:
        Validated prompt

    Raises:
        ValidationError: If validation fails
    """
    if not prompt:
        raise ValidationError("Prompt cannot be empty")

    if max_length is None:
        max_length = MAX_PROMPT_LENGTH

    # Check length
    if len(prompt) > max_length:
        raise ValidationError(f"Prompt too long: {len(prompt)} > {max_length}")

    # Strip HTML if requested
    if strip_html:
        # More comprehensive HTML stripping
        # Remove script tags and their content
        prompt = re.sub(
            r"<script[^>]*>.*?</script>", "", prompt, flags=re.DOTALL | re.IGNORECASE
        )
        # Remove style tags and their content
        prompt = re.sub(
            r"<style[^>]*>.*?</style>", "", prompt, flags=re.DOTALL | re.IGNORECASE
        )
        # Remove remaining HTML tags
        prompt = re.sub(r"<[^>]+>", "", prompt)

    # Check for null bytes
    if "\x00" in prompt:
        raise ValidationError("Prompt contains null bytes")

    return prompt.strip()


def validate_shell_command(
    command: str,
    allow_pipes: bool = False,
    allow_redirects: bool = False,
) -> str:
    """Validate shell command for safety.

    Args:
        command: The shell command to validate
        allow_pipes: Whether to allow pipe operators
        allow_redirects: Whether to allow redirections

    Returns:
        Validated command

    Raises:
        ValidationError: If validation fails
    """
    if not command:
        raise ValidationError("Command cannot be empty")

    # Check for dangerous patterns
    dangerous_patterns = [
        r";\s*rm\s",  # rm command after semicolon
        r"&&\s*rm\s",  # rm command after &&
        r"\|\s*rm\s",  # rm command after pipe
        r"`[^`]+`",  # Command substitution
        r"\$\([^)]+\)",  # Command substitution
        r"\$\{[^}]+\}",  # Variable expansion that could be dangerous
    ]

    if not allow_pipes:
        dangerous_patterns.append(r"\|")

    if not allow_redirects:
        dangerous_patterns.extend([r">", r"<", r">>", r"2>"])

    for pattern in dangerous_patterns:
        if re.search(pattern, command):
            raise ValidationError(f"Command contains dangerous pattern: {pattern}")

    # Check for null bytes
    if "\x00" in command:
        raise ValidationError("Command contains null bytes")

    return command


def validate_sql_input(value: str, param_name: str = "input") -> str:
    """Validate SQL input to prevent injection.

    Args:
        value: The value to validate
        param_name: Name of the parameter (for error messages)

    Returns:
        Validated value

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError(f"{param_name} must be a string")

    # Check for common SQL injection patterns
    dangerous_patterns = [
        r"';",  # Quote followed by semicolon
        r'";',  # Double quote followed by semicolon
        r"--",  # SQL comment
        r"/\*",  # SQL block comment start
        r"\*/",  # SQL block comment end
        r"\bunion\b",  # UNION keyword
        r"\bdrop\b",  # DROP keyword
        r"\bdelete\b",  # DELETE keyword
        r"\binsert\b",  # INSERT keyword
        r"\bupdate\b",  # UPDATE keyword
        r"'\s*or\s*'",  # OR condition pattern
        r'"\s*or\s*"',  # OR condition pattern with double quotes
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValidationError(
                f"{param_name} contains potentially dangerous SQL pattern"
            )

    return value


def validate_json_data(
    data: Union[str, Dict[str, Any]],
    max_size: Optional[int] = None,
    required_fields: Optional[set] = None,
) -> Dict[str, Any]:
    """Validate JSON data for safety and structure.

    Args:
        data: JSON string or dict to validate
        max_size: Maximum size in bytes
        required_fields: Set of required top-level fields

    Returns:
        Validated dict

    Raises:
        ValidationError: If validation fails
    """
    # Parse if string
    if isinstance(data, str):
        if max_size and len(data.encode("utf-8")) > max_size:
            raise ValidationError(f"JSON too large: > {max_size} bytes")

        try:
            parsed = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}")
    else:
        parsed = data

    # Check type
    if not isinstance(parsed, dict):
        raise ValidationError("JSON must be an object/dict at top level")

    # Check required fields
    if required_fields:
        missing = required_fields - set(parsed.keys())
        if missing:
            raise ValidationError(f"Missing required fields: {', '.join(missing)}")

    return parsed


def validate_environment_var(
    name: str,
    value: Optional[str],
    var_type: str = "string",
    allowed_values: Optional[set] = None,
) -> Optional[Union[str, bool, int, Path]]:
    """Validate environment variable value.

    Args:
        name: Variable name (for error messages)
        value: The value to validate
        var_type: Expected type (string, bool, int, path)
        allowed_values: Set of allowed values

    Returns:
        Validated and converted value

    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        return None

    if var_type == "bool":
        if value.lower() in {"true", "1", "yes", "on"}:
            return True
        elif value.lower() in {"false", "0", "no", "off"}:
            return False
        else:
            raise ValidationError(f"Invalid boolean value for {name}: '{value}'")

    elif var_type == "int":
        try:
            return int(value)
        except ValueError:
            raise ValidationError(f"Invalid integer value for {name}: '{value}'")

    elif var_type == "path":
        return validate_file_path(value)

    elif var_type == "string":
        if allowed_values and value not in allowed_values:
            raise ValidationError(
                f"Invalid value for {name}: '{value}'. "
                f"Allowed: {', '.join(allowed_values)}"
            )
        return value

    else:
        raise ValidationError(f"Unknown var_type: {var_type}")
