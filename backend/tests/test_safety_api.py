from __future__ import annotations

from fastapi.testclient import TestClient

from app.modules.accounts.schemas import AccountCreate
from app.modules.accounts.service import create_account
from app.modules.campaigns.schemas import CampaignCreate
from app.modules.campaigns.service import create_campaign
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project


def _create_developer_account(name: str = "Dev Owner"):
    return create_account(AccountCreate(display_name=name, role="developer"))


def _create_tester_account(name: str = "Tester Owner"):
    return create_account(AccountCreate(display_name=name, role="tester"))


def _actor_headers(actor_id: str) -> dict[str, str]:
    return {"X-Actor-Id": actor_id}


def test_campaign_safety_crud_flow_returns_expected_shapes(client: TestClient) -> None:
    developer = _create_developer_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )

    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        ),
        current_actor_id=developer.id,
    )
    campaign_id = campaign.id

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
        headers=_actor_headers(developer.id),
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
        headers=_actor_headers(developer.id),
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


def test_campaign_safety_create_requires_current_actor(client: TestClient) -> None:
    response = client.post(
        "/api/v1/campaigns/camp_123/safety",
        json={
            "distribution_channel": "testflight",
            "source_label": "TestFlight",
            "risk_level": "low",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "missing_actor_context",
        "message": "Current actor is required.",
        "details": {
            "header": "X-Actor-Id",
        },
    }


def test_campaign_safety_create_rejects_duplicate_resource(client: TestClient) -> None:
    developer = _create_developer_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        ),
        current_actor_id=developer.id,
    )
    campaign_id = campaign.id

    client.post(
        f"/api/v1/campaigns/{campaign_id}/safety",
        json={
            "distribution_channel": "testflight",
            "source_label": "TestFlight",
            "risk_level": "low",
        },
        headers=_actor_headers(developer.id),
    )

    response = client.post(
        f"/api/v1/campaigns/{campaign_id}/safety",
        json={
            "distribution_channel": "manual_invite",
            "source_label": "Manual invite",
            "risk_level": "high",
        },
        headers=_actor_headers(developer.id),
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


def test_campaign_safety_create_rejects_non_developer_actor(client: TestClient) -> None:
    developer = _create_developer_account()
    tester = _create_tester_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        ),
        current_actor_id=developer.id,
    )

    response = client.post(
        f"/api/v1/campaigns/{campaign.id}/safety",
        json={
            "distribution_channel": "testflight",
            "source_label": "TestFlight",
            "risk_level": "low",
        },
        headers=_actor_headers(tester.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "forbidden_actor_role",
        "message": "Developer role is required for this operation.",
        "details": {
            "actor_id": tester.id,
            "actor_role": "tester",
            "required_role": "developer",
        },
    }


def test_campaign_safety_patch_rejects_unknown_fields(client: TestClient) -> None:
    developer = _create_developer_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        ),
        current_actor_id=developer.id,
    )
    campaign_id = campaign.id

    client.post(
        f"/api/v1/campaigns/{campaign_id}/safety",
        json={
            "distribution_channel": "testflight",
            "source_label": "TestFlight",
            "risk_level": "low",
        },
        headers=_actor_headers(developer.id),
    )

    response = client.patch(
        f"/api/v1/campaigns/{campaign_id}/safety",
        json={"campaign_id": "camp_other"},
        headers=_actor_headers(developer.id),
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


def test_campaign_safety_patch_rejects_actor_without_campaign_ownership(
    client: TestClient,
) -> None:
    owner = _create_developer_account("Owner Dev")
    other_developer = _create_developer_account("Other Dev")
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=owner.id,
    )
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        ),
        current_actor_id=owner.id,
    )

    client.post(
        f"/api/v1/campaigns/{campaign.id}/safety",
        json={
            "distribution_channel": "testflight",
            "source_label": "TestFlight",
            "risk_level": "low",
        },
        headers=_actor_headers(owner.id),
    )

    response = client.patch(
        f"/api/v1/campaigns/{campaign.id}/safety",
        json={"risk_level": "medium"},
        headers=_actor_headers(other_developer.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "ownership_mismatch",
        "message": "Current actor does not own the target resource.",
        "details": {
            "actor_id": other_developer.id,
            "resource": "campaign_safety",
            "ownership_anchor": {
                "resource": "project",
                "id": project.id,
                "owner_account_id": owner.id,
            },
        },
    }
