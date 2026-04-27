from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.accounts.schemas import AccountCreate, AccountRole, AccountUpdate
from app.modules.accounts.service import (
    create_account,
    delete_account,
    ensure_account_exists,
    get_account_for_actor,
    get_account_summary,
    get_account_summary_for_actor,
    list_accounts,
    update_account,
)
from app.modules.campaigns.schemas import CampaignCreate, TargetPlatform
from app.modules.campaigns.service import create_campaign
from app.modules.device_profiles.schemas import DeviceProfileCreate, DeviceProfilePlatform
from app.modules.device_profiles.service import create_device_profile
from app.modules.feedback.schemas import (
    FeedbackCategory,
    FeedbackCreate,
    FeedbackReviewStatus,
    FeedbackSeverity,
)
from app.modules.feedback.service import create_feedback
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project
from app.modules.tasks.schemas import TaskCreate, TaskStatus
from app.modules.tasks.service import create_task


def test_account_service_create_and_list_returns_expected_items() -> None:
    created_account = create_account(
        AccountCreate(
            display_name="Alice QA",
            role=AccountRole.TESTER,
            bio="Mobile web tester",
        )
    )

    listed_accounts = list_accounts()

    assert listed_accounts.total == 1
    assert listed_accounts.items[0].id == created_account.id
    assert listed_accounts.items[0].display_name == "Alice QA"
    assert listed_accounts.items[0].role == AccountRole.TESTER
    assert listed_accounts.items[0].roles == [AccountRole.TESTER]


def test_account_service_create_can_store_dual_roles() -> None:
    created_account = create_account(
        AccountCreate(
            display_name="Dual Role User",
            role=AccountRole.DEVELOPER,
            roles=[AccountRole.DEVELOPER, AccountRole.TESTER],
        )
    )

    assert created_account.role == AccountRole.DEVELOPER
    assert created_account.roles == [AccountRole.DEVELOPER, AccountRole.TESTER]


def test_account_service_ensure_exists_raises_not_found() -> None:
    with pytest.raises(AppError) as exc_info:
        ensure_account_exists("acct_missing")

    error = exc_info.value
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert error.code == "resource_not_found"
    assert error.details == {
        "resource": "account",
        "id": "acct_missing",
    }


def test_account_service_update_changes_only_provided_fields() -> None:
    created_account = create_account(
        AccountCreate(
            display_name="Alice QA",
            role=AccountRole.TESTER,
            bio="Original bio",
            locale="en-US",
        )
    )

    updated_account = update_account(
        created_account.id,
        AccountUpdate(
            display_name="Alice Mobile QA",
            bio="Updated bio",
        ),
    )

    assert updated_account.id == created_account.id
    assert updated_account.role == AccountRole.TESTER
    assert updated_account.roles == [AccountRole.TESTER]
    assert updated_account.display_name == "Alice Mobile QA"
    assert updated_account.bio == "Updated bio"
    assert updated_account.locale == "en-US"


def test_account_service_update_roles_can_change_primary_fallback() -> None:
    created_account = create_account(
        AccountCreate(
            display_name="Dual Role User",
            role=AccountRole.DEVELOPER,
            roles=[AccountRole.DEVELOPER, AccountRole.TESTER],
        )
    )

    updated_account = update_account(
        created_account.id,
        AccountUpdate(roles=[AccountRole.TESTER]),
    )

    assert updated_account.role == AccountRole.TESTER
    assert updated_account.roles == [AccountRole.TESTER]


def test_account_service_delete_removes_the_resource() -> None:
    created_account = create_account(
        AccountCreate(
            display_name="Build Owner",
            role=AccountRole.DEVELOPER,
        )
    )

    delete_account(created_account.id)

    with pytest.raises(AppError) as exc_info:
        ensure_account_exists(created_account.id)

    assert exc_info.value.code == "resource_not_found"


def test_account_service_summary_returns_developer_owned_resources() -> None:
    developer = create_account(
        AccountCreate(
            display_name="Build Owner",
            role=AccountRole.DEVELOPER,
        )
    )
    project = create_project(
        ProjectCreate(
            name="Owned Project",
            description="Owned by developer",
        ),
        current_actor_id=developer.id,
    )
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Owned Campaign",
            description="Owned campaign",
            target_platforms=[TargetPlatform.IOS],
            version_label="0.9.0",
        ),
        current_actor_id=developer.id,
    )

    summary = get_account_summary(developer.id)

    assert summary.account_id == developer.id
    assert summary.role == AccountRole.DEVELOPER
    assert summary.developer_summary is not None
    assert summary.tester_summary is None
    assert summary.developer_summary.owned_projects_count == 1
    assert summary.developer_summary.owned_campaigns_count == 1
    assert summary.developer_summary.feedback_to_review_count == 0
    assert summary.developer_summary.recent_projects[0].id == project.id
    assert summary.developer_summary.recent_campaigns[0].id == campaign.id


def test_account_service_summary_returns_tester_collaboration_footprint() -> None:
    developer = create_account(
        AccountCreate(
            display_name="Dev",
            role=AccountRole.DEVELOPER,
        )
    )
    tester = create_account(
        AccountCreate(
            display_name="Tester",
            role=AccountRole.TESTER,
        )
    )
    project = create_project(
        ProjectCreate(
            name="Owned Project",
        ),
        current_actor_id=developer.id,
    )
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Campaign",
            target_platforms=[TargetPlatform.IOS],
        ),
        current_actor_id=developer.id,
    )
    device_profile = create_device_profile(
        DeviceProfileCreate(
            name="Owned Device",
            platform=DeviceProfilePlatform.IOS,
            device_model="iPhone 15",
            os_name="iOS",
        ),
        current_actor_id=tester.id,
    )
    task = create_task(
        campaign.id,
        TaskCreate(
            title="Assigned Task",
            device_profile_id=device_profile.id,
            status=TaskStatus.ASSIGNED,
        ),
        current_actor_id=developer.id,
    )
    feedback = create_feedback(
        task.id,
        FeedbackCreate(
            summary="Needs follow-up",
            severity=FeedbackSeverity.MEDIUM,
            category=FeedbackCategory.USABILITY,
        ),
        current_actor_id=tester.id,
    )

    summary = get_account_summary(tester.id)

    assert summary.account_id == tester.id
    assert summary.role == AccountRole.TESTER
    assert summary.developer_summary is None
    assert summary.tester_summary is not None
    assert summary.tester_summary.owned_device_profiles_count == 1
    assert summary.tester_summary.assigned_tasks_count == 1
    assert summary.tester_summary.submitted_feedback_count == 1
    assert summary.tester_summary.recent_device_profiles[0].id == device_profile.id
    assert summary.tester_summary.recent_tasks[0].id == task.id
    assert summary.tester_summary.recent_feedback[0].id == feedback.id
    assert (
        summary.tester_summary.recent_feedback[0].review_status
        == FeedbackReviewStatus.SUBMITTED
    )


def test_account_service_read_visibility_requires_current_actor() -> None:
    tester = create_account(
        AccountCreate(
            display_name="Visible Tester",
            role=AccountRole.TESTER,
        )
    )

    with pytest.raises(AppError) as exc_info:
        get_account_for_actor(tester.id, None)

    error = exc_info.value
    assert error.status_code == status.HTTP_400_BAD_REQUEST
    assert error.code == "missing_actor_context"
    assert error.details == {
        "header": "X-Actor-Id",
    }


def test_account_service_read_visibility_rejects_other_actor() -> None:
    tester = create_account(
        AccountCreate(
            display_name="Visible Tester",
            role=AccountRole.TESTER,
        )
    )
    other_actor = create_account(
        AccountCreate(
            display_name="Other Actor",
            role=AccountRole.DEVELOPER,
        )
    )

    with pytest.raises(AppError) as exc_info:
        get_account_summary_for_actor(tester.id, other_actor.id)

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "ownership_mismatch"
    assert error.details == {
        "actor_id": other_actor.id,
        "resource": "account",
        "ownership_anchor": {
            "resource": "account",
            "id": tester.id,
            "owner_account_id": tester.id,
        },
    }
