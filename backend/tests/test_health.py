from fastapi.testclient import TestClient


def test_health_root_ok(client: TestClient):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    # Validate expected health keys
    assert body.get("status") == "ok"
    assert body.get("service") == "car-company-backend"
    assert "time" in body and isinstance(body["time"], str)


def test_ws_help_docs_guide(client: TestClient):
    # Optional health/doc guide endpoint
    resp = client.get("/docs/guide")
    assert resp.status_code == 200
    data = resp.json()
    # Basic shape
    assert "websocket" in data
    assert "note" in data
