import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.security.crypto import secret_strength_ok

client = TestClient(app)

def signup(client, u, p, r):
    return client.post("/signup", json={"username": u, "password": p, "role": r})

def login(client, u, p):
    r = client.post("/login", json={"username": u, "password": p})
    assert r.status_code == 200
    return r.json()["access_token"]

@pytest.mark.a02
def test_secret_strength_checker():
    ok, _ = secret_strength_ok("x"*40)
    assert ok is True
    ok, _ = secret_strength_ok("short")
    assert ok is False
    ok, _ = secret_strength_ok("dev-unsafe-change-me")
    assert ok is False

@pytest.mark.a02
def test_tampered_jwt_is_rejected():
    # create a user and get a valid token
    signup(client, "admin", "Admin#123", "admin")
    token = login(client, "admin", "Admin#123")

    # tamper the token: flip one character in the signature part
    parts = token.split(".")
    assert len(parts) == 3
    sig = parts[2]
    flipped = ("A" if sig[-1] != "A" else "B")
    bad = ".".join(parts[:2] + [sig[:-1] + flipped])

    r = client.get("/me", headers={"Authorization": f"Bearer {bad}"})
    assert r.status_code == 401  # signature check failed
