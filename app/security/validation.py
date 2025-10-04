from __future__ import annotations
from pathlib import Path

def safe_join(base: Path, user_path: str) -> Path:
    """
    Join base + user_path and ensure result stays inside base (no '../').
    Raise ValueError if traversal is detected.
    """
    base_r = base.resolve()
    joined = (base_r / user_path).resolve()
    if not str(joined).startswith(str(base_r)):
        raise ValueError("Path traversal detected")
    return joined

def allowed_extension(filename: str, allowed: set[str]) -> bool:
    return any(filename.lower().endswith(ext.lower()) for ext in allowed)
