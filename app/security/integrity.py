import hashlib, json, pathlib
from fastapi import HTTPException

def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""): h.update(chunk)
    return h.hexdigest()

def assert_file_checksum(path: str, checksums_file: str = "checksums.json"):
    p = pathlib.Path(checksums_file)
    if not p.exists():
        return
    data = json.loads(p.read_text(encoding="utf-8"))
    expected = data.get(path)
    if not expected:
        raise HTTPException(500, f"No checksum entry for {path}")
    actual = sha256(path)
    if actual != expected:
        raise HTTPException(500, f"Integrity check failed for {path}")