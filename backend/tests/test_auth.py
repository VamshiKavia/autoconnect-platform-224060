from fastapi.testclient import TestClient


def assert_token_response(resp):
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "token_type" in body
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert body["access_token"].startswith("mocktoken-")
    return body


def test_login_and_mirror(client: TestClient):
    payload = {"email": "login_test@example.com", "password": "Password123!"}

    r1 = client.post("/auth/login", json=payload)
    b1 = assert_token_response(r1)

    r2 = client.post("/api/auth/login", json=payload)
    b2 = assert_token_response(r2)

    # For the same email, token could be the same format; don't require equality, just shape
    assert b1["token_type"] == b2["token_type"] == "bearer"


def test_register_and_mirror_idempotent(client: TestClient):
    payload = {
        "email": "register_test@example.com",
        "password": "Password123!",
        "name": "Register Test",
    }

    r1 = client.post("/auth/register", json=payload)
    assert r1.status_code in (200, 201)
    b1 = r1.json()
    assert "access_token" in b1 and b1["access_token"].startswith("mocktoken-")
    assert b1.get("token_type") == "bearer"
    assert "user" in b1 and b1["user"]["email"] == payload["email"]

    # Duplicate registration should be idempotent and still succeed in mock
    r2 = client.post("/auth/register", json=payload)
    assert r2.status_code in (200, 201)
    b2 = r2.json()
    assert "access_token" in b2 and b2["access_token"].startswith("mocktoken-")
    assert b2.get("token_type") == "bearer"
    assert "user" in b2 and b2["user"]["email"] == payload["email"]

    # API-prefixed mirror
    r3 = client.post("/api/auth/register", json=payload)
    assert r3.status_code in (200, 201)
    b3 = r3.json()
    assert "access_token" in b3 and b3["access_token"].startswith("mocktoken-")
    assert b3.get("token_type") == "bearer"
    assert "user" in b3 and b3["user"]["email"] == payload["email"]


def test_logout_if_available(client: TestClient):
    # The mock backend has /auth/logout accepting optional authorization in body and returns {"ok": True}
    payload = {"email": "logout_test@example.com", "password": "Password123!"}
    login_resp = client.post("/auth/login", json=payload)
    body = login_resp.json()
    token = body["access_token"]

    # Try logout by passing Authorization-like string in body
    out = client.post("/auth/logout", json={"authorization": f"Bearer {token}"})
    assert out.status_code == 200
    assert out.json() == {"ok": True}
