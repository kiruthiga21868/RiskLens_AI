"""
Sprint 1 smoke tests: verify the server boots and endpoints respond.

WHY TestClient
    FastAPI ships a TestClient (built on httpx) that runs the whole
    app in-process - no live server needed. Tests are fast and CI-safe.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """GET / should return a welcome message and docs link."""
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["message"].startswith("Welcome to RiskLens")


def test_health_endpoint():
    """GET /api/v1/health should report an 'ok' service."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "RiskLens AI"
    assert float(body["uptime_seconds"]) >= 0.0


def test_openapi_schema_exposed():
    """The OpenAPI schema must be published for Swagger UI."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "RiskLens AI"
