from __future__ import annotations

from app.modules.accounts.schemas import AccountCreate, AccountRole
from app.modules.accounts.service import create_account, get_account_summary
from app.modules.campaigns.schemas import CampaignCreate, TargetPlatform
from app.modules.campaigns.service import create_campaign
from app.modules.device_profiles.schemas import (
    DeviceProfileCreate,
    DeviceProfilePlatform,
)
from app.modules.device_profiles.service import create_device_profile
from app.modules.feedback.schemas import (
    FeedbackCategory,
    FeedbackCreate,
    FeedbackReviewStatus,
    FeedbackSeverity,
    FeedbackUpdate,
)
from app.modules.feedback.service import create_feedback, update_feedback
from app.modules.participation_requests.schemas import (
    ParticipationRequestCreate,
    ParticipationRequestStatus,
    ParticipationRequestUpdate,
)
from app.modules.participation_requests.service import (
    create_participation_request,
    update_participation_request,
)
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project
from app.modules.tasks.schemas import TaskCreate, TaskStatus
from app.modules.tasks.service import create_task


def _create_dual_role_account():
    return create_account(
        AccountCreate(
            display_name="Dual Role Builder",
            role=AccountRole.DEVELOPER,
            roles=[AccountRole.DEVELOPER, AccountRole.TESTER],
        )
    )


def _create_dual_role_campaign_and_device_profile():
    account = _create_dual_role_account()
    project = create_project(
        ProjectCreate(name="Dual Role Project"),
        current_actor_id=account.id,
    )
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Dual Role Campaign",
            target_platforms=[TargetPlatform.IOS],
        ),
        current_actor_id=account.id,
    )
    device_profile = create_device_profile(
        DeviceProfileCreate(
            name="Dual Role iPhone",
            platform=DeviceProfilePlatform.IOS,
            device_model="iPhone 15",
            os_name="iOS",
        ),
        current_actor_id=account.id,
    )
    return account, project, campaign, device_profile


def test_dual_role_account_can_own_project_campaign_and_device_profile() -> None:
    account, project, campaign, device_profile = _create_dual_role_campaign_and_device_profile()

    assert project.owner_account_id == account.id
    assert campaign.project_id == project.id
    assert device_profile.owner_account_id == account.id


def test_dual_role_account_can_request_and_review_participation() -> None:
    account, _, campaign, device_profile = _create_dual_role_campaign_and_device_profile()

    request = create_participation_request(
        campaign.id,
        ParticipationRequestCreate(device_profile_id=device_profile.id),
        current_actor_id=account.id,
    )
    reviewed_request = update_participation_request(
        request.id,
        ParticipationRequestUpdate(
            status=ParticipationRequestStatus.ACCEPTED,
            decision_note="Looks good.",
        ),
        current_actor_id=account.id,
    )

    assert request.tester_account_id == account.id
    assert reviewed_request.status == ParticipationRequestStatus.ACCEPTED


def test_dual_role_account_can_submit_and_review_feedback() -> None:
    account, _, campaign, device_profile = _create_dual_role_campaign_and_device_profile()
    task = create_task(
        campaign.id,
        TaskCreate(
            title="Try onboarding",
            device_profile_id=device_profile.id,
            status=TaskStatus.ASSIGNED,
        ),
        current_actor_id=account.id,
    )
    feedback = create_feedback(
        task.id,
        FeedbackCreate(
            summary="The onboarding copy is clear.",
            severity=FeedbackSeverity.LOW,
            category=FeedbackCategory.USABILITY,
        ),
        current_actor_id=account.id,
    )

    reviewed_feedback = update_feedback(
        feedback.id,
        FeedbackUpdate(
            review_status=FeedbackReviewStatus.REVIEWED,
            developer_note="Thanks for checking this.",
        ),
        current_actor_id=account.id,
    )

    assert feedback.device_profile_id == device_profile.id
    assert reviewed_feedback.review_status == FeedbackReviewStatus.REVIEWED
    assert reviewed_feedback.developer_note == "Thanks for checking this."


def test_dual_role_account_summary_returns_developer_and_tester_summaries() -> None:
    account, project, campaign, device_profile = _create_dual_role_campaign_and_device_profile()
    task = create_task(
        campaign.id,
        TaskCreate(
            title="Try onboarding",
            device_profile_id=device_profile.id,
            status=TaskStatus.ASSIGNED,
        ),
        current_actor_id=account.id,
    )
    create_feedback(
        task.id,
        FeedbackCreate(
            summary="The onboarding copy is clear.",
            severity=FeedbackSeverity.LOW,
            category=FeedbackCategory.USABILITY,
        ),
        current_actor_id=account.id,
    )

    summary = get_account_summary(account.id)

    assert summary.role == AccountRole.DEVELOPER
    assert summary.roles == [AccountRole.DEVELOPER, AccountRole.TESTER]
    assert summary.developer_summary is not None
    assert summary.developer_summary.owned_projects_count == 1
    assert summary.developer_summary.recent_projects[0].id == project.id
    assert summary.tester_summary is not None
    assert summary.tester_summary.owned_device_profiles_count == 1
    assert summary.tester_summary.recent_device_profiles[0].id == device_profile.id
