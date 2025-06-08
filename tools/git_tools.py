"""Git helpers for Luca – subprocess-only, no extra deps.
Enhanced with input validation to prevent command injection.
"""

import shlex
import subprocess
from pathlib import Path

from luca_core.validation import ValidationError

ROOT = Path(__file__).resolve().parent.parent


def _run(cmd: str) -> str:
    """
    Run cmd in repo root, return stdout (raise on non-zero).

    Args:
        cmd: The command to execute in the repository root

    Returns:
        Standard output from command execution (whitespace stripped)

    Raises:
        RuntimeError: If command exits with non-zero status code
    """
    result = subprocess.run(
        shlex.split(cmd), cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"{cmd} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def get_git_diff() -> str:
    """
    Return combined unstaged + staged diff for review.

    Returns:
        String with both unstaged and staged changes

    Raises:
        RuntimeError: If a git command fails
    """
    unstaged = _run("git diff")
    staged = _run("git diff --staged")
    return f"--- unstaged ---\\n{unstaged}\\n\\n--- staged ---\\n{staged}"


def git_commit(message: str) -> str:
    """
    Stage everything and commit with *message*; return new commit SHA.

    Args:
        message: The commit message to use

    Returns:
        The SHA of the new commit

    Raises:
        RuntimeError: If a git command fails
        ValidationError: If the commit message contains dangerous characters
    """
    # Validate the commit message to prevent injection
    if not message:
        raise ValidationError("Commit message cannot be empty")

    # Check for dangerous characters that could break out of quotes
    dangerous_chars = ['"', "'", "`", "$", "\\", "\n", "\r", "\x00"]
    for char in dangerous_chars:
        if char in message:
            raise ValidationError(
                f"Commit message contains forbidden character: {repr(char)}"
            )

    # Additional length check
    if len(message) > 1000:
        raise ValidationError("Commit message too long (max 1000 characters)")

    _run("git add -A")

    # Use subprocess directly for better control
    result = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(f"git commit failed: {result.stderr.strip()}")

    out = result.stdout.strip()
    return out.split()[-1]  # last token is the SHA
