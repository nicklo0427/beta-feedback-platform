from __future__ import annotations

from fastapi.testclient import TestClient


def test_eligibility_rules_crud_flow_returns_expected_shapes(client: TestClient) -> None:
    project_response = client.post("/api/v1/projects", json={"name": "HabitQuest"})
    project_id = project_response.json()["id"]

    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project_id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios", "android"],
        },
    )
    campaign_id = campaign_response.json()["id"]

    create_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/eligibility-rules",
        json={
            "platform": "ios",
            "os_name": "iOS",
            "os_version_min": "17.0",
            "os_version_max": "18.2",
            "install_channel": "testflight",
            "is_active": True,
        },
    )

    assert create_response.status_code == 201
    created_rule = create_response.json()
    eligibility_rule_id = created_rule["id"]

    assert created_rule["campaign_id"] == campaign_id
    assert created_rule["platform"] == "ios"
    assert created_rule["is_active"] is True
    assert created_rule["created_at"]
    assert created_rule["updated_at"]

    list_response = client.get(f"/api/v1/campaigns/{campaign_id}/eligibility-rules")

    assert list_response.status_code == 200
    assert list_response.json() == {
        "items": [
            {
                "id": eligibility_rule_id,
                "campaign_id": campaign_id,
                "platform": "ios",
                "os_name": "iOS",
                "install_channel": "testflight",
                "is_active": True,
                "updated_at": created_rule["updated_at"],
            }
        ],
        "total": 1,
    }

    detail_response = client.get(f"/api/v1/eligibility-rules/{eligibility_rule_id}")

    assert detail_response.status_code == 200
    assert detail_response.json() == created_rule

    patch_response = client.patch(
        f"/api/v1/eligibility-rules/{eligibility_rule_id}",
        json={
            "install_channel": "app-store-connect",
            "is_active": False,
        },
    )

    assert patch_response.status_code == 200
    patched_rule = patch_response.json()
    assert patched_rule["id"] == eligibility_rule_id
    assert patched_rule["campaign_id"] == campaign_id
    assert patched_rule["install_channel"] == "app-store-connect"
    assert patched_rule["is_active"] is False

    delete_response = client.delete(f"/api/v1/eligibility-rules/{eligibility_rule_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    missing_response = client.get(f"/api/v1/eligibility-rules/{eligibility_rule_id}")

    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "code": "resource_not_found",
        "message": "Eligibility rule not found.",
        "details": {
            "resource": "eligibility_rule",
            "id": eligibility_rule_id,
        },
    }


def test_eligibility_create_requires_existing_campaign(client: TestClient) -> None:
    response = client.post(
        "/api/v1/campaigns/camp_missing/eligibility-rules",
        json={
            "platform": "ios",
            "os_name": "iOS",
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


def test_eligibility_patch_rejects_campaign_id_updates(client: TestClient) -> None:
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

    rule_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/eligibility-rules",
        json={"platform": "ios"},
    )
    eligibility_rule_id = rule_response.json()["id"]

    response = client.patch(
        f"/api/v1/eligibility-rules/{eligibility_rule_id}",
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
