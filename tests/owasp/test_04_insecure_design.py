import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.security.settings import RATE_LIMIT_LOGIN_MAX, BODY_MAX_BYTES

client = TestClient(app)

def signup(u,p,r):
    return client.post("/signup", json={"username":u,"password":p,"role":r})

@pytest.mark.a04
def test_login_rate_limit_429_after_threshold():
    # create a user (if your signup is in-memory; OK for this test)
    signup("rl_user","Pass#123","candidate")
    # hit login with wrong password until limit exceeded
    for i in range(RATE_LIMIT_LOGIN_MAX):
        r = client.post("/login", json={"username":"rl_user","password":"wrong"})
        assert r.status_code in (401, 429)
        if r.status_code == 429:
            break
    # one more attempt should be 429
    r = client.post("/login", json={"username":"rl_user","password":"wrong"})
    assert r.status_code == 429
    assert r.headers.get("Retry-After") is not None

@pytest.mark.a04
def test_body_size_limit_returns_413():
    big = "A" * (BODY_MAX_BYTES + 100)
    r = client.post("/debug/echojson", json={"x": big})
    assert r.status_code == 413
