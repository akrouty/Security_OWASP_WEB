import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.a10
def test_block_localhost():
    r = client.get("/fetch", params={"url": "http://127.0.0.1/"})
    assert r.status_code in (400, 403)

@pytest.mark.a10
def test_block_file_scheme():
    r = client.get("/fetch", params={"url": "file:///etc/passwd"})
    assert r.status_code == 400

@pytest.mark.a10
def test_block_link_local():
    r = client.get("/fetch", params={"url": "http://169.254.169.254/latest/meta-data/"})
    assert r.status_code in (400, 403)
