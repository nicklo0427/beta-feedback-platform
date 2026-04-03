from __future__ import annotations

from fastapi.testclient import TestClient


def test_campaigns_crud_flow_supports_project_filter(client: TestClient) -> None:
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "HabitQuest"},
    )
    project_id = project_response.json()["id"]

    create_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project_id,
            "name": "Closed Beta Round 1",
            "description": "Collect onboarding feedback.",
            "target_platforms": ["ios", "android"],
            "version_label": "0.9.0-beta.1",
        },
    )

    assert create_response.status_code == 201
    created_campaign = create_response.json()
    campaign_id = created_campaign["id"]
    assert created_campaign["status"] == "draft"

    list_response = client.get("/api/v1/campaigns")
    assert list_response.status_code == 200
    assert list_response.json() == {
        "items": [
            {
                "id": campaign_id,
                "project_id": project_id,
                "name": "Closed Beta Round 1",
                "target_platforms": ["ios", "android"],
                "version_label": "0.9.0-beta.1",
                "status": "draft",
                "updated_at": created_campaign["updated_at"],
            }
        ],
        "total": 1,
    }

    filtered_response = client.get(f"/api/v1/campaigns?project_id={project_id}")
    assert filtered_response.status_code == 200
    assert filtered_response.json()["total"] == 1
    assert filtered_response.json()["items"][0]["id"] == campaign_id

    detail_response = client.get(f"/api/v1/campaigns/{campaign_id}")
    assert detail_response.status_code == 200
    assert detail_response.json() == created_campaign

    patch_response = client.patch(
        f"/api/v1/campaigns/{campaign_id}",
        json={"status": "active"},
    )
    assert patch_response.status_code == 200
    patched_campaign = patch_response.json()
    assert patched_campaign["status"] == "active"
    assert patched_campaign["project_id"] == project_id

    delete_response = client.delete(f"/api/v1/campaigns/{campaign_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    empty_list_response = client.get(f"/api/v1/campaigns?project_id={project_id}")
    assert empty_list_response.status_code == 200
    assert empty_list_response.json() == {"items": [], "total": 0}


def test_campaign_create_requires_existing_project(client: TestClient) -> None:
    response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": "proj_missing",
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "resource_not_found",
        "message": "Project not found.",
        "details": {
            "resource": "project",
            "id": "proj_missing",
        },
    }


def test_campaign_patch_rejects_project_id_updates(client: TestClient) -> None:
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

    response = client.patch(
        f"/api/v1/campaigns/{campaign_id}",
        json={"project_id": "proj_other"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "validation_error",
        "message": "Request validation failed.",
        "details": {
            "fields": [
                {
                    "field": "project_id",
                    "message": "Extra inputs are not permitted",
                }
            ]
        },
    }


def test_project_delete_conflicts_when_campaigns_exist(client: TestClient) -> None:
    project_response = client.post("/api/v1/projects", json={"name": "HabitQuest"})
    project_id = project_response.json()["id"]

    client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project_id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
    )

    response = client.delete(f"/api/v1/projects/{project_id}")

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Project cannot be deleted while campaigns exist.",
        "details": {
            "resource": "project",
            "id": project_id,
            "related_resource": "campaign",
        },
    }


def test_campaign_delete_conflicts_when_tasks_exist(client: TestClient) -> None:
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

    client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={"title": "Validate onboarding flow"},
    )

    response = client.delete(f"/api/v1/campaigns/{campaign_id}")

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Campaign cannot be deleted while tasks exist.",
        "details": {
            "resource": "campaign",
            "id": campaign_id,
            "related_resource": "task",
        },
    }


def test_campaign_delete_conflicts_when_eligibility_rules_exist(client: TestClient) -> None:
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

    client.post(
        f"/api/v1/campaigns/{campaign_id}/eligibility-rules",
        json={
            "platform": "ios",
            "os_name": "iOS",
        },
    )

    response = client.delete(f"/api/v1/campaigns/{campaign_id}")

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Campaign cannot be deleted while eligibility rules exist.",
        "details": {
            "resource": "campaign",
            "id": campaign_id,
            "related_resource": "eligibility_rule",
        },
    }


def test_campaign_delete_conflicts_when_safety_exists(client: TestClient) -> None:
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

    client.post(
        f"/api/v1/campaigns/{campaign_id}/safety",
        json={
            "distribution_channel": "testflight",
            "source_label": "TestFlight",
            "risk_level": "low",
        },
    )

    response = client.delete(f"/api/v1/campaigns/{campaign_id}")

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Campaign cannot be deleted while safety exists.",
        "details": {
            "resource": "campaign",
            "id": campaign_id,
            "related_resource": "campaign_safety",
        },
    }
