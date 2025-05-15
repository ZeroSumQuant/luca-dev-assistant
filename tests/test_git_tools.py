"""Tests for git_tools module"""

import shlex
from unittest.mock import MagicMock, patch

import pytest

from tools.git_tools import _run, get_git_diff, git_commit


def test_run_success():
    """Test successful command execution with _run"""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "command output\n"

    with patch('subprocess.run', return_value=mock_result) as mock_run:
        result = _run("git status")

        # Verify subprocess.run was called with the right arguments
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert shlex.split("git status") == args[0]
        assert kwargs["check"] is False

        # Verify the result is as expected
        assert result == "command output"


def test_run_failure():
    """Test command execution failure with _run"""
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "error message\n"

    with patch('subprocess.run', return_value=mock_result):
        with pytest.raises(RuntimeError, match="failed: error message"):
            _run("git invalid-command")


def test_get_git_diff():
    """Test get_git_diff combines unstaged and staged changes"""
    # Setup mocks
    with patch('tools.git_tools._run') as mock_run:
        mock_run.side_effect = ["unstaged changes", "staged changes"]

        result = get_git_diff()

        # Verify _run was called with correct arguments
        assert mock_run.call_count == 2
        mock_run.assert_any_call("git diff")
        mock_run.assert_any_call("git diff --staged")

        # Verify result combines both outputs
        assert "unstaged changes" in result
        assert "staged changes" in result
        assert "--- unstaged ---" in result
        assert "--- staged ---" in result


def test_git_commit():
    """Test git_commit stages and commits changes"""
    with patch('tools.git_tools._run') as mock_run:
        mock_run.side_effect = ["", "commit abc123def456"]

        commit_message = "feat: add new functionality"
        sha = git_commit(commit_message)

        # Verify _run was called with the correct arguments
        assert mock_run.call_count == 2
        mock_run.assert_any_call("git add -A")
        mock_run.assert_any_call(f'git commit -m "{commit_message}"')

        # Verify the SHA is parsed correctly
        assert sha == "abc123def456"