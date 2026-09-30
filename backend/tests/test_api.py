"""
Full-stack integration tests for RiskLens AI (Sprint 2+).

These hit the real app + DB (SQLite) through FastAPI's TestClient,
verifying the whole request chain: auth -> detection -> health -> reports.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def auth(client):
    """Register + login a fresh user, return auth headers."""
    r = client.post("/api/v1/auth/register", json={
        "username": "tester", "email": "tester@example.com",
        "full_name": "Test User", "password": "SecurePass123!",
    })
    if r.status_code == 409:  # already registered from a prior run
        r = client.post("/api/v1/auth/login", json={"username": "tester", "password": "SecurePass123!"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    assert client.get("/api/v1/health").status_code == 200


def test_register_login(client, auth):
    me = client.get("/api/v1/auth/me", headers=auth)
    assert me.status_code == 200
    assert me.json()["username"] == "tester"


def test_url_scan_persists(client, auth):
    r = client.post("/api/v1/url", json={"url": "http://evil-example.xyz/verify"},
                    headers=auth)
    assert r.status_code == 200
    body = r.json()
    assert body["prediction"] in {"legitimate", "phishing"}
    assert 0 <= body["confidence"] <= 1
    assert 0 <= body["risk_score"] <= 100
    assert "explanation" in body
    assert "recommendation" in body
    assert "feature_importance" in body


def test_email_scan(client, auth):
    r = client.post("/api/v1/email", json={"content": "URGENT: WIN FREE PRIZE now!"},
                    headers=auth)
    assert r.status_code == 200


def test_credential_scan(client, auth):
    r = client.post("/api/v1/credential", json={"password": "password123"}, headers=auth)
    assert r.status_code == 200
    assert r.json()["prediction"] == "weak"


def test_dashboard(client, auth):
    r = client.get("/api/v1/dashboard", headers=auth)
    assert r.status_code == 200
    body = r.json()
    assert "health_score" in body
    assert "components" in body


def test_threat_history(client, auth):
    r = client.get("/api/v1/threats", headers=auth)
    assert r.status_code == 200
    assert r.json()["total"] >= 3


def test_reports(client, auth):
    assert client.get("/api/v1/reports/csv", headers=auth).status_code == 200
    assert client.get("/api/v1/reports/pdf", headers=auth).status_code == 200


def test_admin_guard(client, auth):
    # normal user must be forbidden
    assert client.get("/api/v1/admin/stats", headers=auth).status_code == 403


def test_unauthorized_blocked(client):
    assert client.get("/api/v1/dashboard").status_code in (401, 403)