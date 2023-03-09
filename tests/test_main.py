from fastapi.testclient import TestClient

from gestor.main import app

client = TestClient(app)


def test_health_main() -> None:
    response = client.get("/")
    assert 200 == response.status_code


def test_health_api() -> None:
    response = client.get("/api")
    assert 200 == response.status_code


def test_health_webhooks() -> None:
    response = client.get("/webhooks")
    assert 200 == response.status_code
