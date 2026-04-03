from __future__ import annotations

from fastapi.testclient import TestClient


def test_tasks_crud_flow_supports_filters_and_submitted_at(client: TestClient) -> None:
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "HabitQuest"},
    )
    project_id = project_response.json()["id"]

    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project_id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
    )
    campaign_id = campaign_response.json()["id"]

    device_profile_response = client.post(
        "/api/v1/device-profiles",
        json={
            "name": "QA iPhone 15",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
        },
    )
    device_profile_id = device_profile_response.json()["id"]

    create_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Validate onboarding flow",
            "instruction_summary": "Verify the welcome experience.",
            "device_profile_id": device_profile_id,
            "status": "assigned",
        },
    )

    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task["id"]

    assert created_task["campaign_id"] == campaign_id
    assert created_task["device_profile_id"] == device_profile_id
    assert created_task["title"] == "Validate onboarding flow"
    assert created_task["status"] == "assigned"
    assert created_task["submitted_at"] is None

    list_response = client.get(
        f"/api/v1/tasks?campaign_id={campaign_id}&device_profile_id={device_profile_id}&status=assigned"
    )

    assert list_response.status_code == 200
    assert list_response.json() == {
        "items": [
            {
                "id": task_id,
                "campaign_id": campaign_id,
                "device_profile_id": device_profile_id,
                "title": "Validate onboarding flow",
                "status": "assigned",
                "updated_at": created_task["updated_at"],
            }
        ],
        "total": 1,
    }

    detail_response = client.get(f"/api/v1/tasks/{task_id}")
    assert detail_response.status_code == 200
    assert detail_response.json() == created_task

    patch_in_progress_response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "in_progress"},
    )
    assert patch_in_progress_response.status_code == 200
    in_progress_task = patch_in_progress_response.json()
    assert in_progress_task["status"] == "in_progress"
    assert in_progress_task["submitted_at"] is None

    patch_submitted_response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "submitted"},
    )
    assert patch_submitted_response.status_code == 200
    submitted_task = patch_submitted_response.json()
    assert submitted_task["status"] == "submitted"
    assert submitted_task["submitted_at"] is not None

    delete_response = client.delete(f"/api/v1/tasks/{task_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""


def test_task_create_requires_existing_campaign(client: TestClient) -> None:
    response = client.post(
        "/api/v1/campaigns/camp_missing/tasks",
        json={
            "title": "Validate onboarding flow",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "resource_not_found",
        "message": "Campaign not found.",
        "details": {
            "resource": "campaign",
            "id": "camp_missing",
        },
    }


def test_task_patch_rejects_campaign_id_updates(client: TestClient) -> None:
    project_response = client.post("/api/v1/projects", json={"name": "HabitQuest"})
    project_id = project_response.json()["id"]
    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project_id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
    )
    campaign_id = campaign_response.json()["id"]
    task_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={"title": "Validate onboarding flow"},
    )
    task_id = task_response.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"campaign_id": "camp_other"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "validation_error",
        "message": "Request validation failed.",
        "details": {
            "fields": [
                {
                    "field": "campaign_id",
                    "message": "Extra inputs are not permitted",
                }
            ]
        },
    }


def test_task_patch_rejects_illegal_status_transition(client: TestClient) -> None:
    project_response = client.post("/api/v1/projects", json={"name": "HabitQuest"})
    project_id = project_response.json()["id"]
    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project_id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
    )
    campaign_id = campaign_response.json()["id"]
    device_profile_response = client.post(
        "/api/v1/device-profiles",
        json={
            "name": "QA iPhone 15",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
        },
    )
    device_profile_id = device_profile_response.json()["id"]
    task_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": device_profile_id,
            "status": "assigned",
        },
    )
    task_id = task_response.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "submitted"},
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Task status transition is not allowed.",
        "details": {
            "resource": "task",
            "current_status": "assigned",
            "next_status": "submitted",
        },
    }


def test_task_delete_conflicts_when_feedback_exists(client: TestClient) -> None:
    project_response = client.post("/api/v1/projects", json={"name": "HabitQuest"})
    project_id = project_response.json()["id"]
    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project_id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
    )
    campaign_id = campaign_response.json()["id"]
    task_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={"title": "Validate onboarding flow"},
    )
    task_id = task_response.json()["id"]

    client.post(
        f"/api/v1/tasks/{task_id}/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
        },
    )

    response = client.delete(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Task cannot be deleted while feedback exists.",
        "details": {
            "resource": "task",
            "id": task_id,
            "related_resource": "feedback",
        },
    }
