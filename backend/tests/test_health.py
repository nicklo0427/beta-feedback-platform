from fastapi.testclient import TestClient


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
