import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def signup(u,p,r): return client.post("/signup", json={"username":u,"password":p,"role":r})
def login(u,p):    return client.post("/login",  json={"username":u,"password":p})

@pytest.mark.a07
def test_password_policy_blocks_weak():
    r = signup("weakuser","weak","candidate")
    assert r.status_code == 400

@pytest.mark.a07
def test_refresh_flow_rotate_and_logout():
    # strong pass to satisfy policy
    signup("refreshy","Strong#123","candidate")
    r = login("refreshy","Strong#123"); assert r.status_code == 200
    token1 = r.json()["access_token"]

    # first refresh via cookie
    r2 = client.post("/refresh")
    assert r2.status_code == 200
    token2 = r2.json()["access_token"]
    assert token2 != token1

    # logout revokes the cookie/JTI
    r3 = client.post("/logout")
    assert r3.status_code in (200,204)

    # another refresh should fail now
    r4 = client.post("/refresh")
    assert r4.status_code == 401

@pytest.mark.a07
def test_refresh_token_cannot_call_me():
    signup("rtypetest","Strong#123","candidate")
    r = login("rtypetest","Strong#123"); assert r.status_code == 200
    # get the refresh cookie value
    rt = client.cookies.get("refresh_token")
    assert rt is not None
    # using refresh as bearer must fail
    r2 = client.get("/me", headers={"Authorization": f"Bearer {rt}"})
    assert r2.status_code == 401
