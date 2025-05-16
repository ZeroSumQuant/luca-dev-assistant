"""Safe file read/write helpers for Luca.

All paths are locked to the repo root; attempts to escape raise ValueError.
"""

from pathlib import Path, PurePosixPath

# repo root = parent of the tools/ directory
ROOT = Path(__file__).resolve().parent.parent


def _safe(path: str) -> Path:
    """
    Validate and resolve a file path to ensure it's within the repository root.

    Args:
        path: A string representing a file path relative to the repository root

    Returns:
        A resolved Path object that is guaranteed to be within the repository

    Raises:
        ValueError: If the path would escape the repository root
    """
    full = (ROOT / PurePosixPath(path)).resolve()
    if ROOT not in full.parents and full != ROOT:
        raise ValueError(f"Path {path} escapes repository root")
    return full


def read_text(path: str) -> str:
    """
    Return UTF-8 text from <path> (relative to repo root).

    Args:
        path: A string representing a file path relative to the repository root

    Returns:
        The contents of the file as a UTF-8 encoded string

    Raises:
        ValueError: If the path would escape the repository root
        FileNotFoundError: If the file does not exist
    """
    return _safe(path).read_text(encoding="utf-8")


def write_text(path: str, txt: str) -> str:
    """
    Overwrite <path> with UTF-8 text and confirm bytes written.

    Args:
        path: A string representing a file path relative to the repository root
        txt: The string content to write to the file

    Returns:
        A confirmation string with the number of bytes written and the path

    Raises:
        ValueError: If the path would escape the repository root
    """
    _safe(path).write_text(txt, encoding="utf-8")
    return f"Wrote {len(txt)} bytes to {path}"
