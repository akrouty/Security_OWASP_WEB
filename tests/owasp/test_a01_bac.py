import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def signup(u,p,r): return client.post("/signup", json={"username":u,"password":p,"role":r})
def login(u,p):
    r = client.post("/login", json={"username":u,"password":p}); assert r.status_code==200
    return r.json()["access_token"]
def auth_get(t,u):  return client.get(u,  headers={"Authorization": f"Bearer {t}"})
def auth_post(t,u,b):return client.post(u, json=b, headers={"Authorization": f"Bearer {t}"})

@pytest.mark.a01
def test_private_router_requires_auth():
    assert client.get("/applications").status_code == 403  # deny-by-default works

@pytest.mark.a01
def test_admin_only_and_anti_idor():
    assert signup("admin","Admin#123","admin").status_code == 200
    assert signup("cyrine","Cyrine#123","candidate").status_code == 200
    assert signup("ahmed","Ahmed#123","candidate").status_code == 200

    t_admin  = login("admin","Admin#123")
    t_cyrine = login("cyrine","Cyrine#123")
    t_ahmed  = login("ahmed","Ahmed#123")

    assert auth_get(t_admin,  "/admin/stats").status_code == 200
    assert auth_get(t_cyrine, "/admin/stats").status_code == 403

    assert auth_get(t_cyrine, "/users/cyrine").status_code == 200
    assert auth_get(t_cyrine, "/users/admin").status_code == 403
    assert auth_get(t_admin,  "/users/cyrine").status_code == 200

    r = auth_post(t_cyrine, "/applications", {"title":"Junior Python Dev","description":"Backend track"})
    assert r.status_code == 200
    app_id = r.json()["id"]

    assert auth_get(t_cyrine, f"/applications/{app_id}").status_code == 200
    assert auth_get(t_ahmed,  f"/applications/{app_id}").status_code == 403
    assert auth_get(t_admin,  f"/applications/{app_id}").status_code == 200
