from fastapi.testclient import TestClient

from main import app


def test_root_and_health():
    client = TestClient(app)
    root = client.get("/")
    health = client.get("/health")
    assert root.status_code == 200
    assert root.json()["data_policy"] == "real_data_only"
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"
