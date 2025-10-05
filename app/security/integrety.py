# app/security/integrity.py
from __future__ import annotations
import hashlib, json, os
from typing import List, Dict, Tuple
import structlog

log = structlog.get_logger(__name__)

def sha256(path: str) -> str:
    digest, _ = sha256_of_file(path)
    return digest

def _repo_root() -> str:
    # .../app/security -> .../app -> .../
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def sha256_of_file(path: str) -> Tuple[str, int]:
    h = hashlib.sha256()
    total = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
            total += len(chunk)
    return h.hexdigest(), total

def verify_checksums(manifest_path: str, strict: bool = True) -> List[Dict[str, str]]:
    problems: List[Dict[str, str]] = []
    base = _repo_root()

    with open(manifest_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    entries = data.get("files", []) if isinstance(data, dict) else data
    for entry in entries:
        rel = entry["path"]
        expected_sha = entry["sha256"].lower()
        expected_bytes = int(entry.get("bytes", -1))
        full = os.path.join(base, rel)

        if not os.path.exists(full):
            problems.append({"path": rel, "error": "missing"})
            continue

        actual_sha, actual_bytes = sha256_of_file(full)

        ok = (actual_sha.lower() == expected_sha) and (
            expected_bytes == -1 or expected_bytes == actual_bytes
        )

        if not ok:
            # --- Windows newline fallback: if only CRLF vs LF differs, accept it ---
            try:
                with open(full, "rb") as f2:
                    raw = f2.read()
                norm = raw.replace(b"\r\n", b"\n")
                norm_sha = hashlib.sha256(norm).hexdigest().lower()
                norm_bytes = len(norm)
                if norm_sha == expected_sha and (expected_bytes == -1 or expected_bytes == norm_bytes):
                    # treat as OK (newline-only difference)
                    ok = True
            except Exception as e:
                log.debug("integrity_crlf_normalize_failed", path=rel, error=str(e))

        if not ok:
            if actual_sha.lower() != expected_sha:
                problems.append({"path": rel, "error": "sha256 mismatch"})
            if expected_bytes != -1 and expected_bytes != actual_bytes:
                problems.append({"path": rel, "error": f"size mismatch: {actual_bytes} != {expected_bytes}"})

    if problems:
        for p in problems:
            log.error("integrity_check_failed", **p)
        if strict:
            raise RuntimeError(f"Integrity check failed for {len(problems)} file(s)")
        else:
            log.warning("integrity_check_problems", count=len(problems))
    else:
        log.info("integrity_ok", count=len(entries))
    return problems

def enforce_integrity_from_env() -> None:
    """
    If INTEGRITY_MANIFEST is set, verify it.
    STRICT_INTEGRITY=true -> raise on problems (crash on startup)
    otherwise -> only warn in logs.
    """
    manifest = os.getenv("INTEGRITY_MANIFEST")
    if not manifest:
        return
    strict = os.getenv("STRICT_INTEGRITY", "false").lower() == "true"
    verify_checksums(manifest, strict=strict)
