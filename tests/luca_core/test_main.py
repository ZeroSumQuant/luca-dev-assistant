"""Tests for the luca_core.__main__ module."""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import pytest

from luca_core.__main__ import DEFAULT_DB_PATH, get_status, main


def test_get_status_success(tmp_path):
    """Test getting status successfully."""
    db_path = tmp_path / "test.db"

    with patch("luca_core.__main__.factory") as mock_factory:
        with patch("luca_core.__main__.registry") as mock_registry:
            with patch("luca_core.__main__.LucaManager") as mock_manager:
                # Set up mocks
                mock_factory.create_context_store.return_value = MagicMock()
                mock_registry.tools = {"tool1": None, "tool2": None}

                # Get status
                status = get_status(db_path)

                # Verify results
                assert status["status"] == "ready"
                assert status["db_path"] == str(db_path)
                assert status["context_store"] == "sqlite"
                assert status["tools_registered"] == 2
                assert status["version"] == "1.0.0"

                # Verify directory was created
                assert db_path.parent.exists()


def test_get_status_error(tmp_path):
    """Test getting status with error."""
    db_path = tmp_path / "test.db"

    with patch("luca_core.__main__.factory") as mock_factory:
        # Make factory raise an error
        mock_factory.create_context_store.side_effect = Exception("Test error")

        # Get status
        status = get_status(db_path)

        # Verify error status
        assert status["status"] == "error"
        assert status["error"] == "Test error"


def test_main_status_success(capsys):
    """Test main function with --status flag (success)."""
    test_args = ["luca_core", "--status"]

    with patch("sys.argv", test_args):
        with patch("luca_core.__main__.get_status") as mock_get_status:
            mock_get_status.return_value = {
                "status": "ready",
                "db_path": str(DEFAULT_DB_PATH),
                "context_store": "sqlite",
                "tools_registered": 5,
                "version": "1.0.0",
            }

            # Run main
            exit_code = main()

            # Check output
            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert output["status"] == "ready"
            assert exit_code == 0


def test_main_status_error(capsys):
    """Test main function with --status flag (error)."""
    test_args = ["luca_core", "--status"]

    with patch("sys.argv", test_args):
        with patch("luca_core.__main__.get_status") as mock_get_status:
            mock_get_status.return_value = {
                "status": "error",
                "error": "Test error",
            }

            # Run main
            exit_code = main()

            # Check output
            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert output["status"] == "error"
            assert exit_code == 1


def test_main_verbose_flag():
    """Test main function with --verbose flag."""
    test_args = ["luca_core", "--verbose", "--status"]

    with patch("sys.argv", test_args):
        with patch("logging.getLogger") as mock_logger:
            with patch("luca_core.__main__.get_status") as mock_get_status:
                mock_get_status.return_value = {"status": "ready"}

                # Run main
                main()

                # Verify verbose logging was set
                mock_logger().setLevel.assert_called_with(10)  # DEBUG level


def test_main_custom_db_path():
    """Test main function with custom --db-path."""
    custom_path = "/custom/path/db.sqlite"
    test_args = ["luca_core", "--db-path", custom_path, "--status"]

    with patch("sys.argv", test_args):
        with patch("luca_core.__main__.get_status") as mock_get_status:
            mock_get_status.return_value = {"status": "ready"}

            # Run main
            main()

            # Verify custom path was used
            mock_get_status.assert_called_with(Path(custom_path))


def test_main_no_args(capsys):
    """Test main function with no arguments (shows help)."""
    test_args = ["luca_core"]

    with patch("sys.argv", test_args):
        # Run main
        exit_code = main()

        # Check help output
        captured = capsys.readouterr()
        assert "LUCA Core CLI" in captured.out
        assert "administrative interface" in captured.out.lower()
        assert exit_code == 0


def test_main_as_module():
    """Test running as a module (__name__ == '__main__')."""
    test_args = ["luca_core", "--status"]

    with patch("sys.argv", test_args):
        with patch("sys.exit") as mock_exit:
            with patch("luca_core.__main__.main") as mock_main:
                mock_main.return_value = 0

                # Import the module to trigger if __name__ == "__main__"
                import luca_core.__main__

                # We can't really test the if __name__ == "__main__" block
                # directly, but we can ensure the module loads without error
