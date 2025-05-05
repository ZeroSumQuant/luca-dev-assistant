"""Safe file read/write helpers for Luca (replaces the removed DirectoryReadTool).

All paths are locked to the repo root; attempts to step outside raise ValueError.
"""

from pathlib import Path, PurePosixPath

# repo root = parent of the tools/ directory
ROOT = Path(__file__).resolve().parent.parent


def _safe(path: str) -> Path:
    full = (ROOT / PurePosixPath(path)).resolve()
    if ROOT not in full.parents and full != ROOT:
        raise ValueError(f"Path {path} escapes repository root")
    return full


def read_text(path: str) -> str:
    """Return UTF-8 text from <path> (relative to repo root)."""
    return _safe(path).read_text(encoding="utf-8")


def write_text(path: str, txt: str) -> str:
    """Overwrite <path> with UTF-8 text and confirm bytes written."""
    _safe(path).write_text(txt, encoding="utf-8")
    return f"Wrote {len(txt)} bytes to {path}"
