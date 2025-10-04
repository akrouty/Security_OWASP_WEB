import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.mark.a05
def test_security_headers_present_on_health():
    c = TestClient(app)
    r = c.get("/health")
    h = r.headers
    assert "content-security-policy" in {k.lower() for k in h.keys()}
    assert h.get("X-Frame-Options") == "DENY"
    assert h.get("X-Content-Type-Options") == "nosniff"
    assert h.get("Referrer-Policy") == "no-referrer"
