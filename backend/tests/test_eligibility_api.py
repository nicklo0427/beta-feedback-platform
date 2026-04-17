from __future__ import annotations

from fastapi.testclient import TestClient

from app.modules.accounts.schemas import AccountCreate
from app.modules.accounts.service import create_account
from app.modules.campaigns.schemas import CampaignCreate
from app.modules.campaigns.service import create_campaign
from app.modules.device_profiles.schemas import DeviceProfileCreate
from app.modules.device_profiles.service import create_device_profile
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project


def _create_developer_account(name: str = "Dev Owner"):
    return create_account(AccountCreate(display_name=name, role="developer"))


def _create_tester_account(name: str = "Tester Owner"):
    return create_account(AccountCreate(display_name=name, role="tester"))


def _actor_headers(actor_id: str) -> dict[str, str]:
    return {"X-Actor-Id": actor_id}


def _create_device_profile_for_tester(
    tester_id: str,
    *,
    name: str = "iPhone 15",
    platform: str = "ios",
    os_name: str = "iOS",
    os_version: str | None = "17.4",
    install_channel: str | None = None,
):
    return create_device_profile(
        DeviceProfileCreate(
            name=name,
            platform=platform,
            device_model="Device Model",
            os_name=os_name,
            os_version=os_version,
            install_channel=install_channel,
        ),
        current_actor_id=tester_id,
    )


def test_eligibility_rules_crud_flow_returns_expected_shapes(client: TestClient) -> None:
    developer = _create_developer_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios", "android"],
        ),
        current_actor_id=developer.id,
    )
    campaign_id = campaign.id

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
        headers=_actor_headers(developer.id),
    )

    assert create_response.status_code == 201
    created_rule = create_response.json()
    eligibility_rule_id = created_rule["id"]

    assert created_rule["campaign_id"] == campaign_id
    assert created_rule["platform"] == "ios"
    assert created_rule["is_active"] is True
    assert created_rule["created_at"]
    assert created_rule["updated_at"]

    list_response = client.get(
        f"/api/v1/campaigns/{campaign_id}/eligibility-rules",
        headers=_actor_headers(developer.id),
    )

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

    detail_response = client.get(
        f"/api/v1/eligibility-rules/{eligibility_rule_id}",
        headers=_actor_headers(developer.id),
    )

    assert detail_response.status_code == 200
    assert detail_response.json() == created_rule

    patch_response = client.patch(
        f"/api/v1/eligibility-rules/{eligibility_rule_id}",
        json={
            "install_channel": "app-store-connect",
            "is_active": False,
        },
        headers=_actor_headers(developer.id),
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

    missing_response = client.get(
        f"/api/v1/eligibility-rules/{eligibility_rule_id}",
        headers=_actor_headers(developer.id),
    )

    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "code": "resource_not_found",
        "message": "Eligibility rule not found.",
        "details": {
            "resource": "eligibility_rule",
            "id": eligibility_rule_id,
        },
    }


def test_eligibility_create_requires_current_actor(client: TestClient) -> None:
    response = client.post(
        "/api/v1/campaigns/camp_123/eligibility-rules",
        json={
            "platform": "ios",
            "os_name": "iOS",
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


def test_eligibility_read_requires_current_actor(client: TestClient) -> None:
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

    client.post(
        f"/api/v1/campaigns/{campaign.id}/eligibility-rules",
        json={"platform": "ios"},
        headers=_actor_headers(developer.id),
    )

    response = client.get(f"/api/v1/campaigns/{campaign.id}/eligibility-rules")

    assert response.status_code == 400
    assert response.json() == {
        "code": "missing_actor_context",
        "message": "Current actor is required.",
        "details": {
            "header": "X-Actor-Id",
        },
    }


def test_eligibility_create_requires_existing_campaign(client: TestClient) -> None:
    developer = _create_developer_account()
    response = client.post(
        "/api/v1/campaigns/camp_missing/eligibility-rules",
        json={
            "platform": "ios",
            "os_name": "iOS",
        },
        headers=_actor_headers(developer.id),
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


def test_eligibility_create_rejects_non_developer_actor(client: TestClient) -> None:
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
        f"/api/v1/campaigns/{campaign.id}/eligibility-rules",
        json={"platform": "ios"},
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


def test_eligibility_patch_rejects_campaign_id_updates(client: TestClient) -> None:
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

    rule_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/eligibility-rules",
        json={"platform": "ios"},
        headers=_actor_headers(developer.id),
    )
    eligibility_rule_id = rule_response.json()["id"]

    response = client.patch(
        f"/api/v1/eligibility-rules/{eligibility_rule_id}",
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


def test_eligibility_patch_rejects_actor_without_campaign_ownership(
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

    rule_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/eligibility-rules",
        json={"platform": "ios"},
        headers=_actor_headers(owner.id),
    )
    eligibility_rule_id = rule_response.json()["id"]

    response = client.patch(
        f"/api/v1/eligibility-rules/{eligibility_rule_id}",
        json={"is_active": False},
        headers=_actor_headers(other_developer.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "ownership_mismatch",
        "message": "Current actor does not own the target resource.",
        "details": {
            "actor_id": other_developer.id,
            "resource": "eligibility_rule",
            "ownership_anchor": {
                "resource": "project",
                "id": project.id,
                "owner_account_id": owner.id,
            },
        },
    }


def test_campaign_qualification_results_returns_current_tester_results(
    client: TestClient,
) -> None:
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
    matching_device_profile = _create_device_profile_for_tester(
        tester.id,
        name="iPhone 15 Pro",
        platform="ios",
        os_name="iOS",
        os_version="17.4",
        install_channel="testflight",
    )
    failing_device_profile = _create_device_profile_for_tester(
        tester.id,
        name="iPhone 15",
        platform="ios",
        os_name="iOS",
        os_version="17.4",
        install_channel="app-store-connect",
    )

    rule_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/eligibility-rules",
        json={
            "platform": "ios",
            "os_name": "iOS",
            "os_version_min": "17.0",
            "install_channel": "testflight",
        },
        headers=_actor_headers(developer.id),
    )
    rule_id = rule_response.json()["id"]

    response = client.get(
        f"/api/v1/campaigns/{campaign.id}/qualification-results?mine=true",
        headers=_actor_headers(tester.id),
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "device_profile_id": matching_device_profile.id,
                "device_profile_name": matching_device_profile.name,
                "qualification_status": "qualified",
                "matched_rule_id": rule_id,
                "reason_codes": [],
                "reason_summary": "符合目前活動的資格條件。",
            },
            {
                "device_profile_id": failing_device_profile.id,
                "device_profile_name": failing_device_profile.name,
                "qualification_status": "not_qualified",
                "matched_rule_id": None,
                "reason_codes": [
                    "install_channel_mismatch",
                ],
                "reason_summary": "主要未符合條件：安裝渠道不符合目前活動條件。",
            },
        ],
        "total": 2,
    }


def test_campaign_qualification_results_require_current_actor(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/campaigns/camp_123/qualification-results?mine=true")

    assert response.status_code == 400
    assert response.json() == {
        "code": "missing_actor_context",
        "message": "Current actor is required.",
        "details": {
            "header": "X-Actor-Id",
        },
    }


def test_campaign_qualification_results_reject_non_tester_actor(
    client: TestClient,
) -> None:
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

    response = client.get(
        f"/api/v1/campaigns/{campaign.id}/qualification-results?mine=true",
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "forbidden_actor_role",
        "message": "Tester role is required for this operation.",
        "details": {
            "actor_id": developer.id,
            "actor_role": "developer",
            "required_role": "tester",
        },
    }


def test_campaign_qualification_results_return_empty_when_no_owned_device_profiles(
    client: TestClient,
) -> None:
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

    response = client.get(
        f"/api/v1/campaigns/{campaign.id}/qualification-results?mine=true",
        headers=_actor_headers(tester.id),
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [],
        "total": 0,
    }


def test_campaign_qualification_check_returns_preview_for_campaign_owner(
    client: TestClient,
) -> None:
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
    device_profile = _create_device_profile_for_tester(
        tester.id,
        name="iPhone 15 Pro",
        platform="ios",
        os_name="iOS",
        os_version="17.4",
        install_channel="testflight",
    )
    rule_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/eligibility-rules",
        json={
            "platform": "ios",
            "os_name": "iOS",
            "os_version_min": "17.0",
            "install_channel": "testflight",
        },
        headers=_actor_headers(developer.id),
    )
    rule_id = rule_response.json()["id"]

    response = client.get(
        f"/api/v1/campaigns/{campaign.id}/qualification-check?device_profile_id={device_profile.id}",
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 200
    assert response.json() == {
        "device_profile_id": device_profile.id,
        "device_profile_name": device_profile.name,
        "qualification_status": "qualified",
        "matched_rule_id": rule_id,
        "reason_codes": [],
        "reason_summary": "符合目前活動的資格條件。",
    }


def test_campaign_qualification_check_returns_fail_result_for_ineligible_device_profile(
    client: TestClient,
) -> None:
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
    device_profile = _create_device_profile_for_tester(
        tester.id,
        name="iPhone 15",
        platform="ios",
        os_name="iOS",
        os_version="17.4",
        install_channel="app-store-connect",
    )
    client.post(
        f"/api/v1/campaigns/{campaign.id}/eligibility-rules",
        json={
            "platform": "ios",
            "os_name": "iOS",
            "os_version_min": "17.0",
            "install_channel": "testflight",
        },
        headers=_actor_headers(developer.id),
    )

    response = client.get(
        f"/api/v1/campaigns/{campaign.id}/qualification-check?device_profile_id={device_profile.id}",
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 200
    assert response.json() == {
        "device_profile_id": device_profile.id,
        "device_profile_name": device_profile.name,
        "qualification_status": "not_qualified",
        "matched_rule_id": None,
        "reason_codes": ["install_channel_mismatch"],
        "reason_summary": "主要未符合條件：安裝渠道不符合目前活動條件。",
    }
