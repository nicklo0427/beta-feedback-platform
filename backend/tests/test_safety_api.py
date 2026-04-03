from __future__ import annotations

from fastapi.testclient import TestClient


def test_campaign_safety_crud_flow_returns_expected_shapes(client: TestClient) -> None:
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

    create_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/safety",
        json={
            "distribution_channel": "testflight",
            "source_label": "TestFlight",
            "source_url": "https://testflight.apple.com/join/example",
            "risk_level": "low",
            "official_channel_only": True,
            "risk_note": "Use the official invite link only.",
        },
    )

    assert create_response.status_code == 201
    created_safety = create_response.json()

    assert created_safety["campaign_id"] == campaign_id
    assert created_safety["distribution_channel"] == "testflight"
    assert created_safety["source_label"] == "TestFlight"
    assert created_safety["risk_level"] == "low"
    assert created_safety["review_status"] == "pending"
    assert created_safety["official_channel_only"] is True
    assert created_safety["created_at"]
    assert created_safety["updated_at"]

    get_response = client.get(f"/api/v1/campaigns/{campaign_id}/safety")

    assert get_response.status_code == 200
    assert get_response.json() == created_safety

    patch_response = client.patch(
        f"/api/v1/campaigns/{campaign_id}/safety",
        json={
            "risk_level": "medium",
            "review_status": "approved",
            "risk_note": "Reviewed and approved for trusted testers.",
        },
    )

    assert patch_response.status_code == 200
    patched_safety = patch_response.json()
    assert patched_safety["campaign_id"] == campaign_id
    assert patched_safety["distribution_channel"] == "testflight"
    assert patched_safety["risk_level"] == "medium"
    assert patched_safety["review_status"] == "approved"
    assert patched_safety["risk_note"] == "Reviewed and approved for trusted testers."

    delete_response = client.delete(f"/api/v1/campaigns/{campaign_id}/safety")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    missing_response = client.get(f"/api/v1/campaigns/{campaign_id}/safety")
    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "code": "resource_not_found",
        "message": "Campaign safety not found.",
        "details": {
            "resource": "campaign_safety",
            "campaign_id": campaign_id,
        },
    }


def test_campaign_safety_create_rejects_duplicate_resource(client: TestClient) -> None:
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

    response = client.post(
        f"/api/v1/campaigns/{campaign_id}/safety",
        json={
            "distribution_channel": "manual_invite",
            "source_label": "Manual invite",
            "risk_level": "high",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Campaign safety already exists.",
        "details": {
            "resource": "campaign_safety",
            "campaign_id": campaign_id,
        },
    }


def test_campaign_safety_patch_rejects_unknown_fields(client: TestClient) -> None:
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

    response = client.patch(
        f"/api/v1/campaigns/{campaign_id}/safety",
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
