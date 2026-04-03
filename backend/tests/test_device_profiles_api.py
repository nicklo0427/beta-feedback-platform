from __future__ import annotations

from fastapi.testclient import TestClient


def test_device_profiles_crud_flow_returns_expected_shapes(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/device-profiles",
        json={
            "name": "QA iPhone 15",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
            "os_version": "18.1",
            "browser_name": "Safari",
            "browser_version": "18.0",
            "locale": "zh-TW",
            "notes": "Internal device",
        },
    )

    assert create_response.status_code == 201
    created_device_profile = create_response.json()
    device_profile_id = created_device_profile["id"]

    assert created_device_profile["name"] == "QA iPhone 15"
    assert created_device_profile["platform"] == "ios"
    assert created_device_profile["device_model"] == "iPhone 15 Pro"
    assert created_device_profile["os_name"] == "iOS"
    assert created_device_profile["created_at"]
    assert created_device_profile["updated_at"]

    list_response = client.get("/api/v1/device-profiles")

    assert list_response.status_code == 200
    assert list_response.json() == {
        "items": [
            {
                "id": device_profile_id,
                "name": "QA iPhone 15",
                "platform": "ios",
                "device_model": "iPhone 15 Pro",
                "os_name": "iOS",
                "updated_at": created_device_profile["updated_at"],
            }
        ],
        "total": 1,
    }

    detail_response = client.get(f"/api/v1/device-profiles/{device_profile_id}")

    assert detail_response.status_code == 200
    assert detail_response.json() == created_device_profile

    patch_response = client.patch(
        f"/api/v1/device-profiles/{device_profile_id}",
        json={
            "browser_name": "Safari Technology Preview",
            "notes": "Updated note",
        },
    )

    assert patch_response.status_code == 200
    patched_device_profile = patch_response.json()
    assert patched_device_profile["id"] == device_profile_id
    assert patched_device_profile["browser_name"] == "Safari Technology Preview"
    assert patched_device_profile["notes"] == "Updated note"

    delete_response = client.delete(f"/api/v1/device-profiles/{device_profile_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    missing_response = client.get(f"/api/v1/device-profiles/{device_profile_id}")

    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "code": "resource_not_found",
        "message": "Device profile not found.",
        "details": {
            "resource": "device_profile",
            "id": device_profile_id,
        },
    }


def test_device_profile_patch_rejects_unknown_fields(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/device-profiles",
        json={
            "name": "QA Web Chrome",
            "platform": "web",
            "device_model": "MacBook Pro",
            "os_name": "macOS",
        },
    )
    device_profile_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/device-profiles/{device_profile_id}",
        json={"unknown_field": "x"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "validation_error",
        "message": "Request validation failed.",
        "details": {
            "fields": [
                {
                    "field": "unknown_field",
                    "message": "Extra inputs are not permitted",
                }
            ]
        },
    }


def test_device_profile_delete_conflicts_when_tasks_exist(client: TestClient) -> None:
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
            "title": "Validate onboarding flow",
            "device_profile_id": device_profile_id,
            "status": "assigned",
        },
    )

    response = client.delete(f"/api/v1/device-profiles/{device_profile_id}")

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Device profile cannot be deleted while tasks exist.",
        "details": {
            "resource": "device_profile",
            "id": device_profile_id,
            "related_resource": "task",
        },
    }
