from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.accounts.schemas import AccountCreate
from app.modules.accounts.service import create_account
from app.modules.campaigns.schemas import CampaignCreate
from app.modules.campaigns.service import create_campaign
from app.modules.device_profiles.schemas import DeviceProfileCreate, DeviceProfilePlatform
from app.modules.device_profiles.service import create_device_profile
from app.modules.eligibility.schemas import EligibilityRuleCreate, EligibilityRulePlatform
from app.modules.eligibility.service import create_eligibility_rule
from app.modules.participation_requests.schemas import (
    ParticipationRequestCreate,
    ParticipationRequestStatus,
    ParticipationRequestTaskCreate,
    ParticipationRequestUpdate,
)
from app.modules.participation_requests.service import (
    create_task_from_participation_request,
    create_participation_request,
    get_participation_request,
    list_participation_requests,
    update_participation_request,
)
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project


def _create_developer_account(name: str = "Dev Owner"):
    return create_account(AccountCreate(display_name=name, role="developer"))


def _create_tester_account(name: str = "QA Tester"):
    return create_account(AccountCreate(display_name=name, role="tester"))


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
            platform=EligibilityRulePlatform.IOS,
            os_name="iOS",
            install_channel="testflight",
        ),
        current_actor_id=developer.id,
    )
    qualified_device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA iPhone 15",
            platform=DeviceProfilePlatform.IOS,
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
            platform=DeviceProfilePlatform.IOS,
            device_model="iPhone 15 Pro",
            os_name="iOS",
            install_channel="internal-build",
            os_version="17.4",
        ),
        current_actor_id=tester.id,
    )
    return developer, tester, campaign, qualified_device_profile, ineligible_device_profile


def test_participation_request_service_create_and_list_mine() -> None:
    _, tester, campaign, qualified_device_profile, _ = _seed_participation_context()

    created_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(
            device_profile_id=qualified_device_profile.id,
            note="Happy to help test the onboarding flow.",
        ),
        tester.id,
    )
    listed_requests = list_participation_requests(mine=True, current_actor_id=tester.id)

    assert created_request.campaign_id == campaign.id
    assert created_request.campaign_name == campaign.name
    assert created_request.tester_account_id == tester.id
    assert created_request.device_profile_id == qualified_device_profile.id
    assert created_request.device_profile_name == qualified_device_profile.name
    assert created_request.status == ParticipationRequestStatus.PENDING
    assert created_request.note == "Happy to help test the onboarding flow."
    assert created_request.decision_note is None
    assert created_request.assignment_status == "not_assigned"
    assert listed_requests.total == 1
    assert listed_requests.items[0].id == created_request.id


def test_participation_request_service_lists_review_queue_for_owned_campaigns() -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    other_developer = _create_developer_account("Other Dev")
    other_project = create_project(
        ProjectCreate(name="Other Project"),
        current_actor_id=other_developer.id,
    )
    other_campaign = create_campaign(
        CampaignCreate(
            project_id=other_project.id,
            name="Other Campaign",
            target_platforms=["ios"],
        ),
        current_actor_id=other_developer.id,
    )

    owned_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(device_profile_id=qualified_device_profile.id),
        tester.id,
    )
    other_tester = _create_tester_account("Other Tester")
    other_device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA iPhone 15 Other",
            platform=DeviceProfilePlatform.IOS,
            device_model="iPhone 15 Pro",
            os_name="iOS",
            install_channel="testflight",
            os_version="17.4",
        ),
        current_actor_id=other_tester.id,
    )
    create_participation_request(
        other_campaign.id,
        ParticipationRequestCreate(device_profile_id=other_device_profile.id),
        other_tester.id,
    )

    review_queue = list_participation_requests(
        review_mine=True,
        current_actor_id=developer.id,
    )

    assert review_queue.total == 1
    assert review_queue.items[0].id == owned_request.id
    assert review_queue.items[0].campaign_id == campaign.id
    assert review_queue.items[0].assignment_status == "not_assigned"


def test_participation_request_service_returns_enriched_detail_for_owned_developer() -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    created_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(
            device_profile_id=qualified_device_profile.id,
            note="I can cover onboarding and retention flows.",
        ),
        tester.id,
    )

    detail = get_participation_request(created_request.id, developer.id)

    assert detail.id == created_request.id
    assert detail.tester_account.id == tester.id
    assert detail.tester_account.display_name == tester.display_name
    assert detail.tester_account_summary.tester_summary is not None
    assert detail.device_profile.id == qualified_device_profile.id
    assert detail.device_profile_reputation.device_profile_id == qualified_device_profile.id
    assert detail.qualification_snapshot.device_profile_id == qualified_device_profile.id
    assert detail.campaign.id == campaign.id
    assert detail.campaign_reputation.campaign_id == campaign.id
    assert detail.assignment_status == "not_assigned"


def test_participation_request_service_rejects_duplicate_pending_request() -> None:
    _, tester, campaign, qualified_device_profile, _ = _seed_participation_context()

    create_participation_request(
        campaign.id,
        ParticipationRequestCreate(device_profile_id=qualified_device_profile.id),
        tester.id,
    )

    with pytest.raises(AppError) as exc_info:
        create_participation_request(
            campaign.id,
            ParticipationRequestCreate(device_profile_id=qualified_device_profile.id),
            tester.id,
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "duplicate_pending_participation_request"
    assert error.details["campaign_id"] == campaign.id
    assert error.details["device_profile_id"] == qualified_device_profile.id


def test_participation_request_service_rejects_ineligible_device_profile() -> None:
    _, tester, campaign, _, ineligible_device_profile = _seed_participation_context()

    with pytest.raises(AppError) as exc_info:
        create_participation_request(
            campaign.id,
            ParticipationRequestCreate(device_profile_id=ineligible_device_profile.id),
            tester.id,
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "participation_not_qualified"
    assert error.details["device_profile_id"] == ineligible_device_profile.id
    assert error.details["reason_codes"] == ["install_channel_mismatch"]


def test_participation_request_service_rejects_detail_for_unowned_developer() -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    other_developer = _create_developer_account("Other Dev")
    created_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(device_profile_id=qualified_device_profile.id),
        tester.id,
    )

    with pytest.raises(AppError) as exc_info:
        get_participation_request(created_request.id, other_developer.id)

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "ownership_mismatch"


def test_participation_request_service_supports_withdrawing_own_pending_request() -> None:
    _, tester, campaign, qualified_device_profile, _ = _seed_participation_context()

    created_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(device_profile_id=qualified_device_profile.id),
        tester.id,
    )

    updated_request = update_participation_request(
        created_request.id,
        ParticipationRequestUpdate(status="withdrawn"),
        tester.id,
    )

    assert updated_request.id == created_request.id
    assert updated_request.status == ParticipationRequestStatus.WITHDRAWN
    assert updated_request.updated_at >= created_request.updated_at


def test_participation_request_service_supports_developer_accepting_pending_request() -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    created_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(device_profile_id=qualified_device_profile.id),
        tester.id,
    )

    decided_request = update_participation_request(
        created_request.id,
        ParticipationRequestUpdate(
            status="accepted",
            decision_note="This device profile matches the current beta scope.",
        ),
        developer.id,
    )

    assert decided_request.status == ParticipationRequestStatus.ACCEPTED
    assert decided_request.decision_note == "This device profile matches the current beta scope."
    assert decided_request.decided_at is not None
    assert decided_request.updated_at >= created_request.updated_at


def test_participation_request_service_review_queue_keeps_accepted_requests_until_task_is_created() -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    created_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(device_profile_id=qualified_device_profile.id),
        tester.id,
    )

    update_participation_request(
        created_request.id,
        ParticipationRequestUpdate(status="accepted"),
        developer.id,
    )

    review_queue = list_participation_requests(
        review_mine=True,
        current_actor_id=developer.id,
    )

    assert review_queue.total == 1
    assert review_queue.items[0].id == created_request.id
    assert review_queue.items[0].status == ParticipationRequestStatus.ACCEPTED
    assert review_queue.items[0].linked_task_id is None
    assert review_queue.items[0].assignment_status == "not_assigned"


def test_participation_request_service_can_create_task_from_accepted_request() -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    created_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(
            device_profile_id=qualified_device_profile.id,
            note="I can cover the onboarding and retention flows.",
        ),
        tester.id,
    )
    accepted_request = update_participation_request(
        created_request.id,
        ParticipationRequestUpdate(status="accepted"),
        developer.id,
    )

    created_task = create_task_from_participation_request(
        accepted_request.id,
        ParticipationRequestTaskCreate(
            title="Validate accepted candidate flow",
            instruction_summary="Focus on onboarding regressions.",
            status="assigned",
        ),
        developer.id,
    )
    refreshed_request = get_participation_request(accepted_request.id, developer.id)
    review_queue = list_participation_requests(
        review_mine=True,
        current_actor_id=developer.id,
    )

    assert created_task.campaign_id == campaign.id
    assert created_task.device_profile_id == qualified_device_profile.id
    assert created_task.status == "assigned"
    assert refreshed_request.linked_task_id == created_task.id
    assert refreshed_request.assignment_created_at is not None
    assert refreshed_request.assignment_status == "task_created"
    assert review_queue.total == 0


def test_participation_request_service_rejects_creating_task_before_request_is_accepted() -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    created_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(device_profile_id=qualified_device_profile.id),
        tester.id,
    )

    with pytest.raises(AppError) as exc_info:
        create_task_from_participation_request(
            created_request.id,
            ParticipationRequestTaskCreate(title="Should not work"),
            developer.id,
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "participation_request_not_accepted"
    assert error.details["current_status"] == "pending"


def test_participation_request_service_rejects_duplicate_task_bridge() -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    created_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(device_profile_id=qualified_device_profile.id),
        tester.id,
    )
    accepted_request = update_participation_request(
        created_request.id,
        ParticipationRequestUpdate(status="accepted"),
        developer.id,
    )
    created_task = create_task_from_participation_request(
        accepted_request.id,
        ParticipationRequestTaskCreate(title="Create linked task"),
        developer.id,
    )

    with pytest.raises(AppError) as exc_info:
        create_task_from_participation_request(
            accepted_request.id,
            ParticipationRequestTaskCreate(title="Create duplicate linked task"),
            developer.id,
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "participation_request_task_already_created"
    assert error.details["linked_task_id"] == created_task.id


def test_participation_request_service_supports_developer_declining_pending_request() -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    created_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(device_profile_id=qualified_device_profile.id),
        tester.id,
    )

    decided_request = update_participation_request(
        created_request.id,
        ParticipationRequestUpdate(
            status="declined",
            decision_note="We are currently prioritizing a different install channel.",
        ),
        developer.id,
    )

    assert decided_request.status == ParticipationRequestStatus.DECLINED
    assert decided_request.decision_note == "We are currently prioritizing a different install channel."
    assert decided_request.decided_at is not None


def test_participation_request_service_rejects_withdrawing_other_testers_request() -> None:
    _, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    other_tester = _create_tester_account("Other Tester")

    created_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(device_profile_id=qualified_device_profile.id),
        tester.id,
    )

    with pytest.raises(AppError) as exc_info:
        update_participation_request(
            created_request.id,
            ParticipationRequestUpdate(status="withdrawn"),
            other_tester.id,
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "ownership_mismatch"


def test_participation_request_service_rejects_tester_review_action() -> None:
    _, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    created_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(device_profile_id=qualified_device_profile.id),
        tester.id,
    )

    with pytest.raises(AppError) as exc_info:
        update_participation_request(
            created_request.id,
            ParticipationRequestUpdate(status="accepted"),
            tester.id,
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "forbidden_actor_role"
    assert error.details["required_role"] == "developer"


def test_participation_request_service_rejects_developer_review_for_unowned_campaign() -> None:
    _, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    other_developer = _create_developer_account("Other Dev")
    created_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(device_profile_id=qualified_device_profile.id),
        tester.id,
    )

    with pytest.raises(AppError) as exc_info:
        update_participation_request(
            created_request.id,
            ParticipationRequestUpdate(status="accepted"),
            other_developer.id,
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "ownership_mismatch"


def test_participation_request_service_rejects_invalid_transition_after_decision() -> None:
    developer, tester, campaign, qualified_device_profile, _ = _seed_participation_context()
    created_request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(device_profile_id=qualified_device_profile.id),
        tester.id,
    )
    update_participation_request(
        created_request.id,
        ParticipationRequestUpdate(status="accepted"),
        developer.id,
    )

    with pytest.raises(AppError) as exc_info:
        update_participation_request(
            created_request.id,
            ParticipationRequestUpdate(status="declined"),
            developer.id,
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "invalid_participation_transition"
    assert error.details["current_status"] == "accepted"
    assert error.details["next_status"] == "declined"


def test_participation_request_service_list_requires_exactly_one_queue_selector() -> None:
    developer = _create_developer_account()

    with pytest.raises(AppError) as exc_info:
        list_participation_requests(
            mine=False,
            review_mine=False,
            current_actor_id=developer.id,
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_400_BAD_REQUEST
    assert error.code == "invalid_query"
