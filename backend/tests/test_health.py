from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.config import clear_settings_cache
from app.main import app


def test_health_check_returns_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "beta-feedback-platform-backend",
        "environment": "development",
        "database_configured": False,
        "persistence_mode": "memory",
        "auth_mode": "session_with_header_fallback",
    }


def test_health_defaults_to_session_only_in_beta_environment(monkeypatch) -> None:
    monkeypatch.setenv("BFP_APP_ENV", "beta")
    monkeypatch.delenv("BFP_AUTH_MODE", raising=False)
    monkeypatch.delenv("BFP_AUTH_DEV_ACTOR_HEADER_FALLBACK_ENABLED", raising=False)
    clear_settings_cache()

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json()["environment"] == "beta"
        assert response.json()["auth_mode"] == "session_only"
    finally:
        clear_settings_cache()


def test_health_allows_explicit_fallback_override_in_qa_environment(monkeypatch) -> None:
    monkeypatch.setenv("BFP_APP_ENV", "qa")
    monkeypatch.setenv("BFP_AUTH_MODE", "session_with_header_fallback")
    monkeypatch.delenv("BFP_AUTH_DEV_ACTOR_HEADER_FALLBACK_ENABLED", raising=False)
    clear_settings_cache()

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json()["environment"] == "qa"
        assert response.json()["auth_mode"] == "session_with_header_fallback"
    finally:
        clear_settings_cache()
