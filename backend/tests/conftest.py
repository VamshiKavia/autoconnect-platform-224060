import os
import pytest
from fastapi.testclient import TestClient

# Ensure environment isolation for tests
os.environ.setdefault("BACKEND_PORT", "0")
os.environ.setdefault("FRONTEND_URL", "http://testserver")

# Import the FastAPI app from backend.main (source of truth for routes)
from backend.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    Yields a FastAPI TestClient for the app.
    Session scope keeps it lightweight and consistent across tests without external services.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def fake_credentials():
    """
    Returns a unique email/password pair for tests to avoid collisions.
    """
    import uuid

    unique = uuid.uuid4().hex[:8]
    return {
        "email": f"user_{unique}@example.com",
        "password": "Password123!",
        "name": f"User{unique}",
    }


@pytest.fixture
def login_and_token(client: TestClient, fake_credentials):
    """
    Registers or logs in the fake user and returns the bearer token.
    """
    # Try register first (idempotent in this mock)
    reg_payload = {
        "email": fake_credentials["email"],
        "password": fake_credentials["password"],
        "name": fake_credentials["name"],
    }
    reg_resp = client.post("/auth/register", json=reg_payload)
    assert reg_resp.status_code in (200, 201)
    data = reg_resp.json()
    token = data.get("access_token")
    if not token:
        # Fallback to login if register didn't return token (shouldn't happen here)
        login_resp = client.post(
            "/auth/login",
            json={
                "email": fake_credentials["email"],
                "password": fake_credentials["password"],
            },
        )
        assert login_resp.status_code == 200
        token = login_resp.json().get("access_token")
    assert token and isinstance(token, str) and token.startswith("mocktoken-")
    return token
