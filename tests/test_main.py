from fastapi.testclient import TestClient

from config import settings
from gestor.main import app

client = TestClient(app)


def test_health_main() -> None:
    headers = {"Authorization": settings.API_TOKEN}
    response = client.get("/", headers=headers)
    assert 200 == response.status_code


def test_health_api() -> None:
    headers = {"Authorization": settings.API_TOKEN}
    response = client.get("/api", headers=headers)
    assert 200 == response.status_code


def test_health_webhooks() -> None:
    headers = {"Authorization": settings.API_TOKEN}
    response = client.get("/webhooks", headers=headers)
    assert 200 == response.status_code
