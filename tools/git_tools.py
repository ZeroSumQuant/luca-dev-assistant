"""Git helpers for Luca – subprocess-only, no extra deps."""

import shlex
import subprocess
from pathlib import Path

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
    """
    _run("git add -A")
    out = _run(f'git commit -m "{message}"')
    return out.split()[-1]  # last token is the SHA
