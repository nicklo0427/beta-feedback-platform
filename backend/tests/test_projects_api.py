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
