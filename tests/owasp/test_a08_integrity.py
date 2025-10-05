import pytest
from pathlib import Path
from app.security.integrety import verify_checksums, _repo_root

pytestmark = pytest.mark.a08

def test_integrity_ok():
    """Current manifest should verify cleanly."""
    root = Path(_repo_root())
    problems = verify_checksums(str(root / "integrity.json"), strict=False)
    assert problems == []

def test_integrity_detects_tamper_and_restore():
    """If we tamper with an asset, the check should flag it; after restore, OK again."""
    root = Path(_repo_root())
    asset = root / "assets" / "demo.txt"
    manifest = root / "integrity.json"

    original = asset.read_text(encoding="utf-8")

    try:
        # tamper
        asset.write_text(original + "\nTAMPER", encoding="utf-8")
        problems = verify_checksums(str(manifest), strict=False)
        assert problems and any(p["error"].startswith("sha256") for p in problems)
    finally:
        # restore original to avoid breaking other tests
        asset.write_text(original, encoding="utf-8")

    # verify OK again after restore
    problems = verify_checksums(str(manifest), strict=False)
    assert problems == []
