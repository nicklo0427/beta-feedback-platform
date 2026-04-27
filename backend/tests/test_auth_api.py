from __future__ import annotations

from fastapi.testclient import TestClient


def test_auth_register_login_logout_and_me_flow(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "Release Owner",
            "role": "developer",
            "email": "owner@example.com",
            "password": "supersecret",
        },
    )

    assert register_response.status_code == 201
    assert register_response.cookies.get("bfp_session")
    assert register_response.json()["account"] == {
        "id": register_response.json()["account"]["id"],
        "display_name": "Release Owner",
        "role": "developer",
        "roles": ["developer"],
        "email": "owner@example.com",
        "is_active": True,
    }

    me_response = client.get("/api/v1/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["account"]["email"] == "owner@example.com"

    logout_response = client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 204

    me_after_logout_response = client.get("/api/v1/auth/me")
    assert me_after_logout_response.status_code == 401
    assert me_after_logout_response.json() == {
        "code": "unauthenticated",
        "message": "Authentication is required.",
        "details": None,
    }

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "owner@example.com",
            "password": "supersecret",
        },
    )
    assert login_response.status_code == 200
    assert login_response.cookies.get("bfp_session")
    assert login_response.json()["account"]["id"] == register_response.json()["account"]["id"]


def test_auth_register_accepts_dual_roles(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "Dual Mode Builder",
            "roles": ["developer", "tester"],
            "email": "dual@example.com",
            "password": "supersecret",
        },
    )

    assert response.status_code == 201
    assert response.json()["account"]["role"] == "developer"
    assert response.json()["account"]["roles"] == ["developer", "tester"]

    me_response = client.get("/api/v1/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["account"]["roles"] == ["developer", "tester"]


def test_auth_register_rejects_duplicate_email(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "Release Owner",
            "role": "developer",
            "email": "owner@example.com",
            "password": "supersecret",
        },
    )

    response = client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "Another Owner",
            "role": "developer",
            "email": "owner@example.com",
            "password": "supersecret",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "duplicate_email",
        "message": "This email is already registered.",
        "details": {
            "email": "owner@example.com",
        },
    }


def test_auth_login_rejects_invalid_credentials(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "QA Tester",
            "role": "tester",
            "email": "tester@example.com",
            "password": "supersecret",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "tester@example.com",
            "password": "wrong-pass",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "code": "invalid_credentials",
        "message": "Email or password is incorrect.",
        "details": None,
    }


def test_auth_session_can_drive_project_create_without_actor_header(
    client: TestClient,
) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "Release Owner",
            "role": "developer",
            "email": "owner@example.com",
            "password": "supersecret",
        },
    )

    account_id = register_response.json()["account"]["id"]

    create_project_response = client.post(
        "/api/v1/projects",
        json={
            "name": "Session-Owned Project",
        },
    )

    assert create_project_response.status_code == 201
    assert create_project_response.json()["owner_account_id"] == account_id

    mine_response = client.get("/api/v1/projects?mine=true")
    assert mine_response.status_code == 200
    assert mine_response.json()["total"] == 1
    assert mine_response.json()["items"][0]["owner_account_id"] == account_id
