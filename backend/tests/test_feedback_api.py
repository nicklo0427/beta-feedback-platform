from __future__ import annotations

from fastapi.testclient import TestClient


def test_feedback_crud_flow_derives_relations_and_updates_task_status(client: TestClient) -> None:
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

    create_response = client.post(
        f"/api/v1/tasks/{task_id}/feedback",
        json={
            "summary": "App crashes on launch",
            "rating": 4,
            "severity": "high",
            "category": "bug",
            "actual_result": "App exits immediately.",
        },
    )

    assert create_response.status_code == 201
    created_feedback = create_response.json()
    feedback_id = created_feedback["id"]

    assert created_feedback["task_id"] == task_id
    assert created_feedback["campaign_id"] == campaign_id
    assert created_feedback["device_profile_id"] == device_profile_id
    assert created_feedback["summary"] == "App crashes on launch"
    assert created_feedback["submitted_at"]
    assert created_feedback["updated_at"]

    list_response = client.get(f"/api/v1/tasks/{task_id}/feedback")
    assert list_response.status_code == 200
    assert list_response.json() == {
        "items": [
            {
                "id": feedback_id,
                "task_id": task_id,
                "summary": "App crashes on launch",
                "severity": "high",
                "category": "bug",
                "submitted_at": created_feedback["submitted_at"],
            }
        ],
        "total": 1,
    }

    detail_response = client.get(f"/api/v1/feedback/{feedback_id}")
    assert detail_response.status_code == 200
    assert detail_response.json() == created_feedback

    patch_response = client.patch(
        f"/api/v1/feedback/{feedback_id}",
        json={
            "rating": 5,
            "note": "Updated after reproducing twice.",
        },
    )
    assert patch_response.status_code == 200
    patched_feedback = patch_response.json()
    assert patched_feedback["id"] == feedback_id
    assert patched_feedback["task_id"] == task_id
    assert patched_feedback["rating"] == 5
    assert patched_feedback["note"] == "Updated after reproducing twice."

    task_detail_response = client.get(f"/api/v1/tasks/{task_id}")
    assert task_detail_response.status_code == 200
    assert task_detail_response.json()["status"] == "submitted"
    assert task_detail_response.json()["submitted_at"] is not None

    delete_response = client.delete(f"/api/v1/feedback/{feedback_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""


def test_feedback_create_requires_existing_task(client: TestClient) -> None:
    response = client.post(
        "/api/v1/tasks/task_missing/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "resource_not_found",
        "message": "Task not found.",
        "details": {
            "resource": "task",
            "id": "task_missing",
        },
    }


def test_feedback_patch_rejects_immutable_relation_updates(client: TestClient) -> None:
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
    feedback_response = client.post(
        f"/api/v1/tasks/{task_id}/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
        },
    )
    feedback_id = feedback_response.json()["id"]

    response = client.patch(
        f"/api/v1/feedback/{feedback_id}",
        json={"task_id": "task_other"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "validation_error",
        "message": "Request validation failed.",
        "details": {
            "fields": [
                {
                    "field": "task_id",
                    "message": "Extra inputs are not permitted",
                }
            ]
        },
    }
