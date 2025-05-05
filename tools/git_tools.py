"""Git helpers for Luca – subprocess-only, no extra deps."""

import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run(cmd: str) -> str:
    """Run *cmd* in the repo root and return stdout (raise on non-zero)."""
    result = subprocess.run(
        shlex.split(cmd), cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"{cmd} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def get_git_diff() -> str:
    """Return the combined unstaged + staged diff for review."""
    unstaged = _run("git diff")
    staged = _run("git diff --staged")
    return f"--- unstaged ---\\n{unstaged}\\n\\n--- staged ---\\n{staged}"


def git_commit(message: str) -> str:
    """Stage everything and commit with *message*; return new commit SHA."""
    _run("git add -A")
    out = _run(f'git commit -m "{message}"')
    return out.split()[-1]  # last token is the SHA
