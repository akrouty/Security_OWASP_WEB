import re
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.a09
def test_auth_failures_metric_increments():
    # bad login
    client.post("/signup", json={"username":"meter","password":"Strong#123","role":"candidate"})
    r = client.post("/login", json={"username":"meter","password":"WRONG"})
    assert r.status_code == 401

    # check /metrics scraped text contains the counter
    m = client.get("/metrics")
    assert m.status_code == 200
    body = m.text
    # example line: auth_failures_total{reason="invalid_credentials"} 1.0
    assert 'auth_failures_total{reason="invalid_credentials"}' in body

@pytest.mark.a09
def test_rate_limit_metric_increments():
    # intentionally hammer /login to trigger rate limit
    for _ in range(10):
        client.post("/login", json={"username":"nobody","password":"nope"})
    m = client.get("/metrics")
    assert m.status_code == 200
    assert 'rate_limit_hits_total{bucket="login"}' in m.text
