"""Fingerprint plugin – creates a cached "purpose map" for every .py file."""

import ast
import hashlib
import json
import os
import pathlib
from typing import Dict, List

# ---------- Configuration ----------
CACHE_DIR = pathlib.Path(".omniscience")
CACHE_FILE = CACHE_DIR / "cache.json"
FP_FILE = CACHE_DIR / "fingerprint.json"


# ---------- Helpers ----------
def sha1_bytes(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def py_files(root: pathlib.Path):
    """Yield all project .py files, excluding virtual-envs and .omniscience."""
    for p in root.rglob("*.py"):
        if ".venv" in p.parts or ".omniscience" in p.parts:
            continue
        yield p


def analyse(path: pathlib.Path) -> Dict:
    src = path.read_text(errors="ignore")
    tree = ast.parse(src or "pass")
    cls = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
    fnc = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    doclines = (ast.get_docstring(tree) or "").splitlines()
    doc = doclines[0] if doclines else ""
    return {"path": str(path), "classes": cls, "funcs": fnc, "doc": doc}


# ---------- Core ----------
def build_fingerprints(root: pathlib.Path = pathlib.Path(".")) -> List[Dict]:
    CACHE_DIR.mkdir(exist_ok=True)
    cache: Dict[str, str] = (
        json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
    )

    fingerprints: List[Dict] = []
    for file in py_files(root):
        raw = file.read_bytes()
        digest = sha1_bytes(raw)
        # Always analyze for fingerprint, but only if changed for performance
        if cache.get(str(file)) != digest:
            cache[str(file)] = digest
        fingerprints.append(analyse(file))

    # Persist cache & full fingerprint set
    CACHE_FILE.write_text(json.dumps(cache, indent=2))
    FP_FILE.write_text(json.dumps(fingerprints, indent=2))
    return fingerprints


# ---------- Plugin wrapper ----------
from omn_plugins import register


@register
class FingerprintPlugin:
    """Emits a brief index (first 10 files) for --deep runs."""

    def run(self) -> str:
        fps = build_fingerprints()[:10]
        lines = [
            f"- {fp['path']}: {', '.join(fp['classes'] + fp['funcs'])[:80]}"
            for fp in fps
        ]
        return "📇 FINGERPRINT INDEX (showing first 10 files)\n" + "\n".join(lines)
