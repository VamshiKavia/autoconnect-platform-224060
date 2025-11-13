from fastapi.testclient import TestClient


def test_profile_requires_auth(client: TestClient):
    r = client.get("/profile")
    assert r.status_code == 401
    body = r.json()
    # FastAPI default structure
    assert "detail" in body


def test_profile_round_trip(client: TestClient, fake_credentials):
    # Register to get token
    reg = client.post(
        "/auth/register",
        json={
            "email": fake_credentials["email"],
            "password": fake_credentials["password"],
            "name": fake_credentials["name"],
        },
    )
    assert reg.status_code in (200, 201)
    token = reg.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # GET profile
    get_resp = client.get("/profile", headers=headers)
    assert get_resp.status_code == 200
    profile = get_resp.json()
    assert profile["email"] == fake_credentials["email"]

    # Update profile via PUT
    updated = {
        "email": profile["email"],
        "name": profile["name"] + " Updated",
        "bio": "Test bio",
        "phone": "+1-555-0199",
        "created_at": profile.get("created_at"),
    }
    put_resp = client.put("/profile", headers=headers, json=updated)
    assert put_resp.status_code == 200
    new_profile = put_resp.json()
    assert new_profile["name"] == updated["name"]
    assert new_profile["bio"] == updated["bio"]
    assert new_profile["phone"] == updated["phone"]

    # Verify persisted by subsequent GET
    get_resp2 = client.get("/profile", headers=headers)
    assert get_resp2.status_code == 200
    profile2 = get_resp2.json()
    assert profile2["name"] == updated["name"]
    assert profile2["bio"] == updated["bio"]
    assert profile2["phone"] == updated["phone"]
