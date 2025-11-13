from fastapi.testclient import TestClient


def test_list_cars(client: TestClient):
    r = client.get("/cars")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        item = data[0]
        for key in ["id", "name", "type", "year", "price", "is_new"]:
            assert key in item


def test_list_services(client: TestClient):
    r = client.get("/services")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        item = data[0]
        for key in ["id", "name", "price", "duration_min"]:
            assert key in item


def test_list_parts(client: TestClient):
    r = client.get("/parts")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        item = data[0]
        for key in ["id", "name", "sku", "price"]:
            assert key in item


def test_list_service_centers(client: TestClient):
    r = client.get("/service-centers")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        item = data[0]
        for key in ["id", "name", "address", "lat", "lng", "phone"]:
            assert key in item
