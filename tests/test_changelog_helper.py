"""
Tests for the changelog_helper module.
"""

import os
import sys

# Add the parent directory to sys.path to allow importing modules
path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, path)

# Now we can import our module
from tools.changelog_helper import format_commit_message  # noqa: E402


def test_format_commit_message_simple():
    """Test simple commit message formatting."""
    msg = format_commit_message("feat", None, "add new feature")
    assert msg == "feat: add new feature"


def test_format_commit_message_with_scope():
    """Test commit message formatting with scope."""
    msg = format_commit_message("fix", "docker", "resolve permission issue")
    assert msg == "fix(docker): resolve permission issue"


def test_format_commit_message_with_body():
    """Test commit message formatting with body."""
    msg = format_commit_message(
        "feat",
        "changelog",
        "improve commit message formatting",
        "This adds a helper module to ensure commit messages follow the "
        "Conventional Commits format.",
    )
    expected = (
        "feat(changelog): improve commit message formatting\n\n"
        "This adds a helper module to ensure commit messages follow the "
        "Conventional Commits format.\n\n"
    )
    assert msg == expected


def test_format_commit_message_with_footer():
    """Test commit message formatting with footer."""
    msg = format_commit_message(
        "fix",
        "api",
        "handle authentication error",
        "Improves error handling for API authentication failures.",
        "BREAKING CHANGE: Auth API now returns structured error objects",
    )
    expected = (
        "fix(api): handle authentication error\n\n"
        "Improves error handling for API authentication failures.\n\n"
        "BREAKING CHANGE: Auth API now returns structured error objects"
    )
    assert msg == expected
