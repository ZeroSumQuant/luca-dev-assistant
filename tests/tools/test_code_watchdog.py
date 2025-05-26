"""Tests for code watchdog functionality."""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from tools.code_watchdog import CodeValidationHandler


class TestCodeValidationHandler:
    """Test the code validation handler."""

    def test_validate_file_valid(self):
        """Test validation of a valid Python file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('Hello, world!')\n")
            f.flush()

            handler = CodeValidationHandler(Path.cwd())
            result = handler.validate_file(Path(f.name))

            assert result is True
            assert handler.get_all_errors() == {}

            Path(f.name).unlink()

    def test_validate_file_syntax_error(self):
        """Test validation of a Python file with syntax error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('Hello, world!'\n")  # Missing closing parenthesis
            f.flush()

            handler = CodeValidationHandler(Path.cwd())
            result = handler.validate_file(Path(f.name))

            assert result is False

            Path(f.name).unlink()

    def test_validate_file_import_error(self):
        """Test validation of a Python file with import error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import nonexistent_module_12345\n")
            f.flush()

            handler = CodeValidationHandler(Path.cwd())
            result = handler.validate_file(Path(f.name))

            assert result is False
            errors = handler.get_all_errors()
            assert len(errors) > 0
            # Check that at least one error contains import issue
            all_errors = []
            for file_errors in errors.values():
                all_errors.extend(file_errors)
            assert any("Cannot import" in error for error in all_errors)

            Path(f.name).unlink()

    def test_on_modified_event(self):
        """Test handling of file modification event."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            f.flush()

            handler = CodeValidationHandler(Path.cwd())

            # Mock the event
            event = Mock()
            event.src_path = f.name
            event.is_directory = False

            # Clear any previous debounce
            handler.last_check.clear()

            # Call the handler
            with patch.object(handler, "validate_file") as mock_validate:
                handler.on_modified(event)
                mock_validate.assert_called_once()

            Path(f.name).unlink()

    def test_excluded_directories(self):
        """Test that test files and hidden files are excluded."""
        handler = CodeValidationHandler(Path.cwd())

        # Test file
        event = Mock()
        event.src_path = "test_something.py"
        event.is_directory = False

        with patch.object(handler, "validate_file") as mock_validate:
            handler.on_modified(event)
            mock_validate.assert_not_called()

        # Hidden file
        event.src_path = ".hidden.py"
        with patch.object(handler, "validate_file") as mock_validate:
            handler.on_modified(event)
            mock_validate.assert_not_called()

    def test_debounce(self):
        """Test that debounce prevents rapid repeated validations."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            f.flush()

            handler = CodeValidationHandler(Path.cwd())

            # Mock the event
            event = Mock()
            event.src_path = f.name
            event.is_directory = False

            # Clear any previous debounce
            handler.last_check.clear()

            # First call should trigger validation
            with patch.object(handler, "validate_file") as mock_validate:
                handler.on_modified(event)
                assert mock_validate.call_count == 1

                # Immediate second call should be debounced
                handler.on_modified(event)
                assert mock_validate.call_count == 1

                # Wait for debounce period
                time.sleep(0.6)

                # Now it should validate again
                handler.on_modified(event)
                assert mock_validate.call_count == 2

            Path(f.name).unlink()

    def test_is_valid_import(self):
        """Test import validation logic."""
        handler = CodeValidationHandler(Path.cwd())

        # Standard library imports should be valid
        assert handler.is_valid_import("os") is True
        assert handler.is_valid_import("sys") is True
        assert handler.is_valid_import("pathlib") is True

        # Non-existent modules should be invalid
        assert handler.is_valid_import("nonexistent_module_12345") is False
        assert handler.is_valid_import("fake_module_xyz") is False
