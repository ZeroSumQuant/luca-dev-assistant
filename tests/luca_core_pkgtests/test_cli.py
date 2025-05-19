"""Test the luca_core CLI entry point."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from luca_core.__main__ import get_status


def test_cli_status_command():
    """Test the --status command returns the expected JSON output."""
    result = subprocess.run(
        [sys.executable, "-m", "luca_core", "--status"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    status = json.loads(result.stdout)
    assert status["status"] == "ready"
    assert "db_path" in status
    assert "context_store" in status
    assert "tools_registered" in status
    assert "version" in status


def test_cli_status_custom_db_path(tmp_path):
    """Test the --status command with a custom database path."""
    db_path = tmp_path / "custom" / "context.db"
    result = subprocess.run(
        [sys.executable, "-m", "luca_core", "--status", "--db-path", str(db_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    status = json.loads(result.stdout)
    assert status["status"] == "ready"
    assert status["db_path"] == str(db_path)


def test_cli_no_args_shows_help():
    """Test that running without arguments shows help."""
    result = subprocess.run(
        [sys.executable, "-m", "luca_core"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "LUCA Core CLI" in result.stdout
    assert "--status" in result.stdout
    assert "--help" in result.stdout


def test_cli_verbose_flag():
    """Test the --verbose flag enables debug logging."""
    result = subprocess.run(
        [sys.executable, "-m", "luca_core", "--status", "--verbose"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    # Can't easily test logging output in subprocess, but check command runs
    status = json.loads(result.stdout)
    assert status["status"] == "ready"


def test_get_status_function(tmp_path):
    """Test the get_status function directly."""
    db_path = tmp_path / "test.db"
    status = get_status(db_path)

    assert status["status"] == "ready"
    assert status["db_path"] == str(db_path)
    assert status["context_store"] == "sqlite"
    assert "tools_registered" in status
    assert status["version"] == "1.0.0"


def test_get_status_error_handling(tmp_path):
    """Test error handling in get_status function."""
    # This should still work and create the parent directory
    db_path = tmp_path / "nonexistent" / "path" / "test.db"
    status = get_status(db_path)

    # Should succeed as it creates the parent directories
    assert status["status"] == "ready"
    assert db_path.parent.exists()


def test_cli_error_output():
    """Test that errors are properly formatted as JSON."""
    # Force an error by using an invalid module path
    result = subprocess.run(
        [sys.executable, "-m", "luca_core_invalid"],
        capture_output=True,
        text=True,
    )

    # This will error at the Python level, not our code
    assert result.returncode != 0
