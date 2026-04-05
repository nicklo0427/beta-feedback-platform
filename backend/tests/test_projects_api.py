from __future__ import annotations

from fastapi.testclient import TestClient


def test_projects_crud_flow_returns_expected_shapes(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/projects",
        json={
            "name": "HabitQuest",
            "description": "Cross-platform habit tracking app beta program.",
        },
    )

    assert create_response.status_code == 201
    created_project = create_response.json()
    project_id = created_project["id"]

    assert created_project["name"] == "HabitQuest"
    assert created_project["description"] == (
        "Cross-platform habit tracking app beta program."
    )
    assert created_project["created_at"]
    assert created_project["updated_at"]

    list_response = client.get("/api/v1/projects")

    assert list_response.status_code == 200
    assert list_response.json() == {
        "items": [
            {
                "id": project_id,
                "name": "HabitQuest",
                "description": "Cross-platform habit tracking app beta program.",
                "updated_at": created_project["updated_at"],
            }
        ],
        "total": 1,
    }

    detail_response = client.get(f"/api/v1/projects/{project_id}")

    assert detail_response.status_code == 200
    assert detail_response.json() == created_project

    patch_response = client.patch(
        f"/api/v1/projects/{project_id}",
        json={"description": "Updated project summary."},
    )

    assert patch_response.status_code == 200
    patched_project = patch_response.json()
    assert patched_project["id"] == project_id
    assert patched_project["name"] == "HabitQuest"
    assert patched_project["description"] == "Updated project summary."

    delete_response = client.delete(f"/api/v1/projects/{project_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    missing_response = client.get(f"/api/v1/projects/{project_id}")

    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "code": "resource_not_found",
        "message": "Project not found.",
        "details": {
            "resource": "project",
            "id": project_id,
        },
    }


def test_project_create_assigns_owner_from_current_actor_header(client: TestClient) -> None:
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "Dev Lead",
            "role": "developer",
        },
    )
    account_id = account_response.json()["id"]

    response = client.post(
        "/api/v1/projects",
        headers={"X-Actor-Id": account_id},
        json={"name": "HabitQuest"},
    )

    assert response.status_code == 201
    assert response.json()["owner_account_id"] == account_id


def test_projects_list_supports_mine_filter(client: TestClient) -> None:
    first_account_response = client.post(
        "/api/v1/accounts",
        json={"display_name": "Dev A", "role": "developer"},
    )
    second_account_response = client.post(
        "/api/v1/accounts",
        json={"display_name": "Dev B", "role": "developer"},
    )
    first_account_id = first_account_response.json()["id"]
    second_account_id = second_account_response.json()["id"]

    client.post(
        "/api/v1/projects",
        headers={"X-Actor-Id": first_account_id},
        json={"name": "HabitQuest"},
    )
    client.post(
        "/api/v1/projects",
        headers={"X-Actor-Id": second_account_id},
        json={"name": "FocusFlow"},
    )

    response = client.get(
        "/api/v1/projects?mine=true",
        headers={"X-Actor-Id": first_account_id},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["owner_account_id"] == first_account_id


def test_projects_mine_filter_requires_current_actor_header(client: TestClient) -> None:
    response = client.get("/api/v1/projects?mine=true")

    assert response.status_code == 400
    assert response.json() == {
        "code": "missing_actor_context",
        "message": "Current actor is required.",
        "details": {
            "header": "X-Actor-Id",
        },
    }


def test_projects_mine_filter_rejects_invalid_actor(client: TestClient) -> None:
    response = client.get(
        "/api/v1/projects?mine=true",
        headers={"X-Actor-Id": "acct_missing"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "resource_not_found",
        "message": "Account not found.",
        "details": {
            "resource": "account",
            "id": "acct_missing",
        },
    }


def test_project_create_rejects_non_developer_actor(client: TestClient) -> None:
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "QA Tester",
            "role": "tester",
        },
    )
    account_id = account_response.json()["id"]

    response = client.post(
        "/api/v1/projects",
        headers={"X-Actor-Id": account_id},
        json={"name": "HabitQuest"},
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Developer account is required to own a project.",
        "details": {
            "resource": "project",
            "account_id": account_id,
            "expected_role": "developer",
            "actual_role": "tester",
        },
    }
