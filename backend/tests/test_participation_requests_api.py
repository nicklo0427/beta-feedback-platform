from __future__ import annotations

from fastapi.testclient import TestClient

from app.modules.accounts.schemas import AccountCreate
from app.modules.accounts.service import create_account
from app.modules.campaigns.schemas import CampaignCreate
from app.modules.campaigns.service import create_campaign
from app.modules.device_profiles.schemas import DeviceProfileCreate
from app.modules.device_profiles.service import create_device_profile
from app.modules.eligibility.schemas import EligibilityRuleCreate
from app.modules.eligibility.service import create_eligibility_rule
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project


def _create_developer_account(name: str = "Dev Owner"):
    return create_account(AccountCreate(display_name=name, role="developer"))


def _create_tester_account(name: str = "QA Tester"):
    return create_account(AccountCreate(display_name=name, role="tester"))


def _actor_headers(actor_id: str) -> dict[str, str]:
    return {"X-Actor-Id": actor_id}


def _seed_participation_context():
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
    create_eligibility_rule(
        campaign.id,
        EligibilityRuleCreate(
            platform="ios",
            os_name="iOS",
            install_channel="testflight",
        ),
        current_actor_id=developer.id,
    )
    qualified_device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA iPhone 15",
            platform="ios",
            device_model="iPhone 15 Pro",
            os_name="iOS",
            install_channel="testflight",
            os_version="17.4",
        ),
        current_actor_id=tester.id,
    )
    ineligible_device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA iPhone 15 Internal",
            platform="ios",
            device_model="iPhone 15 Pro",
            os_name="iOS",
            install_channel="internal-build",
            os_version="17.4",
        ),
        current_actor_id=tester.id,
    )
    return developer, tester, campaign, qualified_device_profile, ineligible_device_profile


def test_participation_requests_api_create_list_review_and_withdraw_flow(
    client: TestClient,
) -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()

    create_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/participation-requests",
        json={
            "device_profile_id": qualified_device_profile.id,
            "note": "Happy to help validate the onboarding flow.",
        },
        headers=_actor_headers(tester.id),
    )

    assert create_response.status_code == 201
    created_request = create_response.json()
    request_id = created_request["id"]
    assert created_request["campaign_id"] == campaign.id
    assert created_request["campaign_name"] == campaign.name
    assert created_request["tester_account_id"] == tester.id
    assert created_request["device_profile_id"] == qualified_device_profile.id
    assert created_request["status"] == "pending"

    review_queue_response = client.get(
        "/api/v1/participation-requests?review_mine=true",
        headers=_actor_headers(developer.id),
    )

    assert review_queue_response.status_code == 200
    assert review_queue_response.json() == {
        "items": [created_request],
        "total": 1,
    }

    accept_response = client.patch(
        f"/api/v1/participation-requests/{request_id}",
        json={
            "status": "accepted",
            "decision_note": "Your current device profile is a good fit.",
        },
        headers=_actor_headers(developer.id),
    )

    assert accept_response.status_code == 200
    accepted_request = accept_response.json()
    assert accepted_request["status"] == "accepted"
    assert accepted_request["decision_note"] == "Your current device profile is a good fit."
    assert accepted_request["decided_at"] is not None
    assert accepted_request["assignment_status"] == "not_assigned"

    review_queue_after_accept = client.get(
        "/api/v1/participation-requests?review_mine=true",
        headers=_actor_headers(developer.id),
    )

    assert review_queue_after_accept.status_code == 200
    assert review_queue_after_accept.json() == {
        "items": [accepted_request],
        "total": 1,
    }

    list_response = client.get(
        "/api/v1/participation-requests?mine=true",
        headers=_actor_headers(tester.id),
    )

    assert list_response.status_code == 200
    assert list_response.json() == {
        "items": [accepted_request],
        "total": 1,
    }


def test_participation_request_detail_returns_enriched_candidate_snapshot(
    client: TestClient,
) -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()

    create_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/participation-requests",
        json={
            "device_profile_id": qualified_device_profile.id,
            "note": "I can help validate onboarding and retention flows.",
        },
        headers=_actor_headers(tester.id),
    )
    request_id = create_response.json()["id"]

    detail_response = client.get(
        f"/api/v1/participation-requests/{request_id}",
        headers=_actor_headers(developer.id),
    )

    assert detail_response.status_code == 200
    payload = detail_response.json()
    assert payload["id"] == request_id
    assert payload["tester_account"]["id"] == tester.id
    assert payload["tester_account_summary"]["account_id"] == tester.id
    assert payload["device_profile"]["id"] == qualified_device_profile.id
    assert (
        payload["device_profile_reputation"]["device_profile_id"]
        == qualified_device_profile.id
    )
    assert payload["qualification_snapshot"]["device_profile_id"] == qualified_device_profile.id
    assert payload["campaign"]["id"] == campaign.id
    assert payload["campaign_reputation"]["campaign_id"] == campaign.id
    assert payload["linked_task_id"] is None
    assert payload["assignment_created_at"] is None
    assert payload["assignment_status"] == "not_assigned"


def test_participation_request_api_can_create_task_from_accepted_request(
    client: TestClient,
) -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()

    create_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/participation-requests",
        json={
            "device_profile_id": qualified_device_profile.id,
            "note": "I can help cover onboarding and retention flows.",
        },
        headers=_actor_headers(tester.id),
    )
    request_id = create_response.json()["id"]

    accept_response = client.patch(
        f"/api/v1/participation-requests/{request_id}",
        json={"status": "accepted"},
        headers=_actor_headers(developer.id),
    )
    assert accept_response.status_code == 200

    create_task_response = client.post(
        f"/api/v1/participation-requests/{request_id}/tasks",
        json={
            "title": "Validate accepted participation request",
            "instruction_summary": "Focus on onboarding polish.",
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )

    assert create_task_response.status_code == 201
    created_task = create_task_response.json()
    assert created_task["campaign_id"] == campaign.id
    assert created_task["device_profile_id"] == qualified_device_profile.id
    assert created_task["status"] == "assigned"

    detail_response = client.get(
        f"/api/v1/participation-requests/{request_id}",
        headers=_actor_headers(developer.id),
    )

    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["linked_task_id"] == created_task["id"]
    assert detail_payload["assignment_created_at"] is not None
    assert detail_payload["assignment_status"] == "task_created"


def test_participation_request_task_bridge_rejects_non_accepted_request(
    client: TestClient,
) -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()

    create_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/participation-requests",
        json={"device_profile_id": qualified_device_profile.id},
        headers=_actor_headers(tester.id),
    )
    request_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/participation-requests/{request_id}/tasks",
        json={"title": "Should fail"},
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "participation_request_not_accepted",
        "message": "Only accepted participation requests can be turned into tasks.",
        "details": {
            "resource": "participation_request",
            "id": request_id,
            "current_status": "pending",
            "required_status": "accepted",
        },
    }


def test_participation_request_task_bridge_rejects_duplicate_linked_task(
    client: TestClient,
) -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()

    create_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/participation-requests",
        json={"device_profile_id": qualified_device_profile.id},
        headers=_actor_headers(tester.id),
    )
    request_id = create_response.json()["id"]
    client.patch(
        f"/api/v1/participation-requests/{request_id}",
        json={"status": "accepted"},
        headers=_actor_headers(developer.id),
    )

    first_task_response = client.post(
        f"/api/v1/participation-requests/{request_id}/tasks",
        json={"title": "First linked task"},
        headers=_actor_headers(developer.id),
    )
    first_task_id = first_task_response.json()["id"]

    duplicate_response = client.post(
        f"/api/v1/participation-requests/{request_id}/tasks",
        json={"title": "Duplicate linked task"},
        headers=_actor_headers(developer.id),
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "code": "participation_request_task_already_created",
        "message": "This participation request already has a linked task.",
        "details": {
            "resource": "participation_request",
            "id": request_id,
            "linked_task_id": first_task_id,
        },
    }


def test_participation_request_review_queue_requires_current_actor(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/participation-requests?review_mine=true")

    assert response.status_code == 400
    assert response.json() == {
        "code": "missing_actor_context",
        "message": "Current actor is required.",
        "details": {
            "header": "X-Actor-Id",
        },
    }


def test_participation_request_detail_rejects_unowned_developer(
    client: TestClient,
) -> None:
    _, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    other_developer = _create_developer_account("Other Dev")

    create_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/participation-requests",
        json={"device_profile_id": qualified_device_profile.id},
        headers=_actor_headers(tester.id),
    )
    request_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/participation-requests/{request_id}",
        headers=_actor_headers(other_developer.id),
    )

    assert response.status_code == 409
    assert response.json()["code"] == "ownership_mismatch"


def test_participation_request_review_queue_rejects_tester_actor(
    client: TestClient,
) -> None:
    _, tester, _, _, _ = _seed_participation_context()

    response = client.get(
        "/api/v1/participation-requests?review_mine=true",
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


def test_participation_request_create_requires_current_actor(client: TestClient) -> None:
    response = client.post(
        "/api/v1/campaigns/camp_123/participation-requests",
        json={"device_profile_id": "dp_123"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "missing_actor_context",
        "message": "Current actor is required.",
        "details": {
            "header": "X-Actor-Id",
        },
    }


def test_participation_request_create_rejects_developer_actor(client: TestClient) -> None:
    developer, _, campaign, qualified_device_profile, _ = _seed_participation_context()

    response = client.post(
        f"/api/v1/campaigns/{campaign.id}/participation-requests",
        json={"device_profile_id": qualified_device_profile.id},
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


def test_participation_request_create_rejects_ineligible_device_profile(
    client: TestClient,
) -> None:
    _, tester, campaign, _, ineligible_device_profile = _seed_participation_context()

    response = client.post(
        f"/api/v1/campaigns/{campaign.id}/participation-requests",
        json={"device_profile_id": ineligible_device_profile.id},
        headers=_actor_headers(tester.id),
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload["code"] == "participation_not_qualified"
    assert payload["details"]["device_profile_id"] == ineligible_device_profile.id
    assert payload["details"]["reason_codes"] == ["install_channel_mismatch"]


def test_participation_request_create_rejects_duplicate_pending_request(
    client: TestClient,
) -> None:
    _, tester, campaign, qualified_device_profile, _ = _seed_participation_context()

    first_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/participation-requests",
        json={"device_profile_id": qualified_device_profile.id},
        headers=_actor_headers(tester.id),
    )
    first_request = first_response.json()

    duplicate_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/participation-requests",
        json={"device_profile_id": qualified_device_profile.id},
        headers=_actor_headers(tester.id),
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "code": "duplicate_pending_participation_request",
        "message": "Pending participation request already exists for this campaign and device profile.",
        "details": {
            "campaign_id": campaign.id,
            "tester_account_id": tester.id,
            "device_profile_id": qualified_device_profile.id,
            "existing_request_id": first_request["id"],
            "existing_status": "pending",
        },
    }


def test_participation_request_withdraw_rejects_non_owner_tester(client: TestClient) -> None:
    _, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    other_tester = _create_tester_account("Other Tester")

    create_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/participation-requests",
        json={"device_profile_id": qualified_device_profile.id},
        headers=_actor_headers(tester.id),
    )
    request_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/participation-requests/{request_id}",
        json={"status": "withdrawn"},
        headers=_actor_headers(other_tester.id),
    )

    assert response.status_code == 409
    assert response.json()["code"] == "ownership_mismatch"


def test_participation_request_decision_rejects_unowned_developer(client: TestClient) -> None:
    _, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    other_developer = _create_developer_account("Other Dev")

    create_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/participation-requests",
        json={"device_profile_id": qualified_device_profile.id},
        headers=_actor_headers(tester.id),
    )
    request_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/participation-requests/{request_id}",
        json={"status": "accepted"},
        headers=_actor_headers(other_developer.id),
    )

    assert response.status_code == 409
    assert response.json()["code"] == "ownership_mismatch"


def test_participation_request_decision_rejects_tester_actor(client: TestClient) -> None:
    _, tester, campaign, qualified_device_profile, _ = _seed_participation_context()

    create_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/participation-requests",
        json={"device_profile_id": qualified_device_profile.id},
        headers=_actor_headers(tester.id),
    )
    request_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/participation-requests/{request_id}",
        json={"status": "accepted"},
        headers=_actor_headers(tester.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "forbidden_actor_role",
        "message": "Developer role is required to review participation requests.",
        "details": {
            "actor_id": tester.id,
            "actor_role": "tester",
            "required_role": "developer",
        },
    }


def test_participation_request_decision_rejects_invalid_transition(client: TestClient) -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()

    create_response = client.post(
        f"/api/v1/campaigns/{campaign.id}/participation-requests",
        json={"device_profile_id": qualified_device_profile.id},
        headers=_actor_headers(tester.id),
    )
    request_id = create_response.json()["id"]

    client.patch(
        f"/api/v1/participation-requests/{request_id}",
        json={"status": "declined"},
        headers=_actor_headers(developer.id),
    )

    response = client.patch(
        f"/api/v1/participation-requests/{request_id}",
        json={"status": "accepted"},
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 409
    assert response.json()["code"] == "invalid_participation_transition"
