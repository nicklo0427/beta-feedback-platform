from __future__ import annotations

from fastapi.testclient import TestClient


def test_device_profile_reputation_api_returns_summary_metrics(client: TestClient) -> None:
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

    client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Assigned task",
            "device_profile_id": device_profile_id,
            "status": "assigned",
        },
    )
    submitted_task_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Submitted task",
            "device_profile_id": device_profile_id,
            "status": "submitted",
        },
    )
    submitted_task_id = submitted_task_response.json()["id"]

    client.post(
        f"/api/v1/tasks/{submitted_task_id}/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
        },
    )

    response = client.get(f"/api/v1/device-profiles/{device_profile_id}/reputation")

    assert response.status_code == 200
    assert response.json()["device_profile_id"] == device_profile_id
    assert response.json()["tasks_assigned_count"] == 2
    assert response.json()["tasks_submitted_count"] == 1
    assert response.json()["feedback_submitted_count"] == 1
    assert response.json()["submission_rate"] == 0.5
    assert response.json()["last_feedback_at"]
    assert response.json()["updated_at"]


def test_campaign_reputation_api_returns_zero_state_for_existing_campaign(
    client: TestClient,
) -> None:
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

    response = client.get(f"/api/v1/campaigns/{campaign_id}/reputation")

    assert response.status_code == 200
    assert response.json() == {
        "campaign_id": campaign_id,
        "tasks_total_count": 0,
        "tasks_closed_count": 0,
        "feedback_received_count": 0,
        "closure_rate": 0.0,
        "last_feedback_at": None,
        "updated_at": campaign_response.json()["updated_at"],
    }


def test_reputation_api_returns_not_found_for_missing_anchor(client: TestClient) -> None:
    device_profile_response = client.get("/api/v1/device-profiles/dp_missing/reputation")

    assert device_profile_response.status_code == 404
    assert device_profile_response.json() == {
        "code": "resource_not_found",
        "message": "Device profile not found.",
        "details": {
            "resource": "device_profile",
            "id": "dp_missing",
        },
    }

    campaign_response = client.get("/api/v1/campaigns/camp_missing/reputation")

    assert campaign_response.status_code == 404
    assert campaign_response.json() == {
        "code": "resource_not_found",
        "message": "Campaign not found.",
        "details": {
            "resource": "campaign",
            "id": "camp_missing",
        },
    }
