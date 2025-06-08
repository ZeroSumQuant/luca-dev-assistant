"""Tests for file I/O with input validation."""

import pytest

from tools.file_io import ValidationError, read_text, write_text


class TestFileIOValidation:
    """Test file I/O operations with validation."""

    def test_read_file_size_limit(self):
        """Test that large files are rejected when reading."""
        from tools.file_io import ROOT

        # Create a test file within the repo
        test_file = ROOT / "test_large_file.txt"
        try:
            # Create a file larger than the limit
            large_content = "a" * (11 * 1024 * 1024)  # 11MB
            test_file.write_text(large_content)

            # Should fail with default limit (10MB)
            with pytest.raises(ValidationError, match="File too large"):
                read_text("test_large_file.txt")

            # Should work with higher limit
            content = read_text("test_large_file.txt", max_size=12 * 1024 * 1024)
            assert len(content) == len(large_content)

        finally:
            # Clean up
            if test_file.exists():
                test_file.unlink()

    def test_read_nonexistent_file(self):
        """Test reading non-existent file."""
        with pytest.raises(FileNotFoundError):
            read_text("nonexistent/file.txt")

    def test_read_with_null_bytes(self):
        """Test that files with null bytes are handled."""
        from tools.file_io import ROOT

        # Create a test file within the repo
        test_file = ROOT / "test_null_file.txt"
        try:
            test_file.write_bytes(b"test\x00content")

            # Should reject due to null bytes in content validation
            with pytest.raises(ValidationError, match="null bytes"):
                read_text("test_null_file.txt")

        finally:
            # Clean up
            if test_file.exists():
                test_file.unlink()

    def test_write_size_limit(self, tmp_path):
        """Test that large content is rejected when writing."""
        from tools.file_io import ROOT

        # Create a path within repo
        test_file = ROOT / "test_write_large.txt"
        rel_path = "test_write_large.txt"

        try:
            # Create content larger than default write limit (5MB)
            large_content = "a" * (6 * 1024 * 1024)

            # Should fail with default limit
            with pytest.raises(ValidationError, match="Content too large"):
                write_text(rel_path, large_content)

            # Should work with higher limit
            result = write_text(rel_path, large_content, max_size=7 * 1024 * 1024)
            assert "Wrote" in result
            assert str(len(large_content)) in result

        finally:
            # Clean up
            if test_file.exists():
                test_file.unlink()

    def test_write_creates_directories(self, tmp_path):
        """Test that write creates parent directories."""
        from tools.file_io import ROOT

        # Create nested path within repo
        nested_path = ROOT / "test_nested" / "deep" / "file.txt"
        rel_path = "test_nested/deep/file.txt"

        try:
            result = write_text(rel_path, "test content")
            assert "Wrote" in result
            assert nested_path.exists()
            assert nested_path.read_text() == "test content"

        finally:
            # Clean up
            import shutil

            if (ROOT / "test_nested").exists():
                shutil.rmtree(ROOT / "test_nested")

    def test_path_traversal_prevention(self):
        """Test that path traversal attacks are prevented."""
        dangerous_paths = [
            "../../../etc/passwd",
            "test/../../../../../../etc/passwd",
            "/etc/passwd",
        ]

        for path in dangerous_paths:
            with pytest.raises(
                ValueError, match="(escapes repository root|Path validation failed)"
            ):
                read_text(path)

            with pytest.raises(
                ValueError, match="(escapes repository root|Path validation failed)"
            ):
                write_text(path, "content")
