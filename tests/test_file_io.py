"""Tests for file_io module"""

import os
import tempfile
from pathlib import Path

import pytest

from tools.file_io import ROOT, _safe, read_text, write_text


def test_safe_path_valid():
    """Test that _safe validates a path within the repo root"""
    test_path = "README.md"
    result = _safe(test_path)
    assert isinstance(result, Path)
    assert result.is_relative_to(ROOT)


def test_safe_path_escape():
    """Test that _safe raises ValueError for paths outside repo root"""
    test_path = "../../../etc/passwd"
    with pytest.raises(
        ValueError, match="(escapes repository root|Path validation failed)"
    ):
        _safe(test_path)


def test_read_write_roundtrip():
    """Test file read/write roundtrip functionality"""
    # Create a temporary file inside the repo for testing
    test_content = "Test file content\nLine 2\nLine 3"

    # Use a path inside the repo
    with tempfile.NamedTemporaryFile(dir=ROOT, delete=False) as temp_file:
        temp_path = os.path.basename(temp_file.name)

    try:
        # Test write_text
        result = write_text(temp_path, test_content)
        assert isinstance(result, str)
        assert str(len(test_content)) in result
        assert temp_path in result

        # Test read_text
        content = read_text(temp_path)
        assert content == test_content
    finally:
        # Clean up
        os.unlink(os.path.join(ROOT, temp_path))
