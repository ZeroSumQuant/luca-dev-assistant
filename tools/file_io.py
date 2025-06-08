"""Safe file read/write helpers for Luca.

All paths are locked to the repo root; attempts to escape raise ValueError.
Enhanced with comprehensive input validation for security.
"""

from pathlib import Path, PurePosixPath
from typing import Optional

from luca_core.validation import (
    ValidationError,
    validate_file_content,
    validate_file_path,
)

# repo root = parent of the tools/ directory
ROOT = Path(__file__).resolve().parent.parent

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB default for reads
MAX_WRITE_SIZE = 5 * 1024 * 1024  # 5MB default for writes


def _safe(path: str) -> Path:
    """
    Validate and resolve a file path to ensure it's within the repository root.

    Args:
        path: A string representing a file path relative to the repository root

    Returns:
        A resolved Path object that is guaranteed to be within the repository

    Raises:
        ValueError: If the path would escape the repository root
        ValidationError: If the path fails validation checks
    """
    try:
        # First apply our comprehensive validation
        validate_file_path(
            path,
            must_exist=False,  # Don't require existence here
            allow_directories=True,  # Let caller decide
            base_dir=ROOT,  # Ensure within repo root
        )

        # Additional check for our specific use case
        full = (ROOT / PurePosixPath(path)).resolve()
        if ROOT not in full.parents and full != ROOT:
            raise ValueError(f"Path {path} escapes repository root")

        return full
    except ValidationError as e:
        # Check if it's a path traversal error
        if "outside base directory" in str(e):
            raise ValueError(f"Path {path} escapes repository root")
        # Re-raise as ValueError for backward compatibility
        raise ValueError(f"Path validation failed: {e}")


def read_text(path: str, max_size: Optional[int] = None) -> str:
    """
    Return UTF-8 text from <path> (relative to repo root).

    Args:
        path: A string representing a file path relative to the repository root
        max_size: Maximum file size to read (defaults to MAX_FILE_SIZE)

    Returns:
        The contents of the file as a UTF-8 encoded string

    Raises:
        ValueError: If the path would escape the repository root
        ValidationError: If the file is too large or content validation fails
        FileNotFoundError: If the file does not exist
    """
    safe_path = _safe(path)

    # Check file size before reading
    if safe_path.exists():
        file_size = safe_path.stat().st_size
        max_allowed = max_size or MAX_FILE_SIZE
        if file_size > max_allowed:
            raise ValidationError(
                f"File too large: {file_size} bytes > {max_allowed} bytes"
            )

    # Read the file
    content = safe_path.read_text(encoding="utf-8")

    # Validate content
    validated_content = validate_file_content(
        content, max_size=max_size or MAX_FILE_SIZE
    )

    # Ensure we return a string (validate_file_content preserves type)
    assert isinstance(validated_content, str)
    return validated_content


def write_text(path: str, txt: str, max_size: Optional[int] = None) -> str:
    """
    Overwrite <path> with UTF-8 text and confirm bytes written.

    Args:
        path: A string representing a file path relative to the repository root
        txt: The string content to write to the file
        max_size: Maximum content size to write (defaults to MAX_WRITE_SIZE)

    Returns:
        A confirmation string with the number of bytes written and the path

    Raises:
        ValueError: If the path would escape the repository root
        ValidationError: If content is too large or validation fails
        OSError: If there's insufficient disk space
    """
    # Validate content before writing
    validated_content = validate_file_content(txt, max_size=max_size or MAX_WRITE_SIZE)

    safe_path = _safe(path)

    # Create parent directories if needed
    safe_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the validated content (ensure it's a string)
    assert isinstance(validated_content, str)
    safe_path.write_text(validated_content, encoding="utf-8")

    return f"Wrote {len(validated_content)} bytes to {path}"
