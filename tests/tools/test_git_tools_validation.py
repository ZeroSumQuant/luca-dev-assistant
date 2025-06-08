"""Tests for git tools with input validation."""

from unittest.mock import MagicMock, patch

import pytest

from tools.git_tools import ValidationError, git_commit


class TestGitToolsValidation:
    """Test git operations with validation."""

    def test_empty_commit_message(self):
        """Test that empty commit messages are rejected."""
        with pytest.raises(ValidationError, match="Commit message cannot be empty"):
            git_commit("")

    def test_commit_message_with_quotes(self):
        """Test that commit messages with quotes are rejected."""
        dangerous_messages = [
            'Test "message" with quotes',
            "Test 'message' with quotes",
            "Test `command` substitution",
            "Test $variable expansion",
            "Test \\ escape",
        ]

        for message in dangerous_messages:
            with pytest.raises(ValidationError, match="forbidden character"):
                git_commit(message)

    def test_commit_message_with_newlines(self):
        """Test that commit messages with newlines are rejected."""
        with pytest.raises(ValidationError, match="forbidden character"):
            git_commit("First line\nSecond line")

    def test_commit_message_with_null_bytes(self):
        """Test that commit messages with null bytes are rejected."""
        with pytest.raises(ValidationError, match="forbidden character"):
            git_commit("Test\x00message")

    def test_commit_message_length_limit(self):
        """Test that overly long commit messages are rejected."""
        long_message = "a" * 1001
        with pytest.raises(ValidationError, match="too long"):
            git_commit(long_message)

    @patch("subprocess.run")
    def test_valid_commit_message(self, mock_run):
        """Test that valid commit messages work correctly."""
        # Mock successful git commands
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "[main abc123] Test commit message\n 1 file changed"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Test valid messages
        valid_messages = [
            "Add new feature",
            "Fix bug in validation",
            "Update documentation",
            "feat(validation): Add input validation for security",
            "Test with numbers 123 and symbols !@#%^&*()-_+=",
        ]

        for message in valid_messages:
            sha = git_commit(message)
            assert sha == "changed"  # Last word from mock output

            # Verify subprocess was called correctly
            calls = mock_run.call_args_list
            commit_call = calls[-1]
            assert commit_call[0][0] == ["git", "commit", "-m", message]

    @patch("subprocess.run")
    def test_git_commit_failure_handling(self, mock_run):
        """Test that git commit failures are handled properly."""
        # Mock failed git add
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        # First call succeeds (git add)
        mock_run.side_effect = [
            mock_result,  # git add succeeds
            MagicMock(returncode=1, stderr="nothing to commit"),  # git commit fails
        ]

        with pytest.raises(RuntimeError, match="git commit failed"):
            git_commit("Test message")
