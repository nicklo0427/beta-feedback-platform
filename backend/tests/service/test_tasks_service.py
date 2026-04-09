from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.accounts.schemas import AccountCreate, AccountRole
from app.modules.accounts.service import create_account
from app.modules.campaigns.schemas import CampaignCreate
from app.modules.campaigns.service import create_campaign
from app.modules.device_profiles.schemas import DeviceProfileCreate, DeviceProfilePlatform
from app.modules.device_profiles.service import create_device_profile
from app.modules.eligibility.schemas import (
    EligibilityRuleCreate,
    EligibilityRulePlatform,
    EligibilityRuleUpdate,
)
from app.modules.eligibility.service import create_eligibility_rule, update_eligibility_rule
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project
from app.modules.feedback.schemas import FeedbackCategory, FeedbackCreate, FeedbackSeverity
from app.modules.feedback.service import create_feedback
from app.modules.tasks.schemas import TaskCreate, TaskStatus, TaskUpdate
from app.modules.tasks.service import (
    create_task,
    delete_task,
    ensure_task_exists,
    get_task,
    list_tasks,
    update_task,
)


def test_task_service_create_and_list_supports_filters() -> None:
    project = create_project(ProjectCreate(name="HabitQuest"))
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )
    device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA iPhone 15",
            platform=DeviceProfilePlatform.IOS,
            device_model="iPhone 15 Pro",
            os_name="iOS",
        )
    )

    created_task = create_task(
        campaign.id,
        TaskCreate(
            title="Validate onboarding flow",
            device_profile_id=device_profile.id,
            status=TaskStatus.ASSIGNED,
        ),
    )
    create_task(
        campaign.id,
        TaskCreate(
            title="Check marketing landing page copy",
            status=TaskStatus.OPEN,
        ),
    )

    listed_tasks = list_tasks(
        campaign_id=campaign.id,
        device_profile_id=device_profile.id,
        status_filter=TaskStatus.ASSIGNED,
    )

    assert listed_tasks.total == 1
    assert listed_tasks.items[0].id == created_task.id
    assert listed_tasks.items[0].campaign_id == campaign.id
    assert listed_tasks.items[0].device_profile_id == device_profile.id
    assert listed_tasks.items[0].status == TaskStatus.ASSIGNED


def test_task_service_list_supports_mine_filter_for_owned_device_profiles() -> None:
    project = create_project(ProjectCreate(name="HabitQuest"))
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )
    tester = create_account(
        AccountCreate(display_name="QA Tester", role=AccountRole.TESTER)
    )
    other_tester = create_account(
        AccountCreate(display_name="QA Backup", role=AccountRole.TESTER)
    )
    owned_device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA iPhone 15",
            platform=DeviceProfilePlatform.IOS,
            device_model="iPhone 15 Pro",
            os_name="iOS",
        ),
        tester.id,
    )
    other_device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA Pixel 9",
            platform=DeviceProfilePlatform.ANDROID,
            device_model="Pixel 9",
            os_name="Android",
        ),
        other_tester.id,
    )
    owned_task = create_task(
        campaign.id,
        TaskCreate(
            title="Validate onboarding flow",
            device_profile_id=owned_device_profile.id,
            status=TaskStatus.ASSIGNED,
        ),
    )
    create_task(
        campaign.id,
        TaskCreate(
            title="Check pricing CTA",
            device_profile_id=other_device_profile.id,
            status=TaskStatus.ASSIGNED,
        ),
    )

    listed_tasks = list_tasks(
        mine=True,
        current_actor_id=tester.id,
        status_filter=TaskStatus.ASSIGNED,
    )

    assert listed_tasks.total == 1
    assert listed_tasks.items[0].id == owned_task.id
    assert listed_tasks.items[0].device_profile_id == owned_device_profile.id
    assert listed_tasks.items[0].qualification_context is not None
    assert listed_tasks.items[0].qualification_context.device_profile_id == (
        owned_device_profile.id
    )
    assert listed_tasks.items[0].qualification_context.device_profile_name == (
        owned_device_profile.name
    )
    assert listed_tasks.items[0].qualification_context.qualification_status == "qualified"
    assert listed_tasks.items[0].qualification_context.qualification_drift is False


def test_task_service_detail_includes_qualification_context_and_drift_warning() -> None:
    developer = create_account(
        AccountCreate(display_name="Dev Owner", role=AccountRole.DEVELOPER)
    )
    tester = create_account(
        AccountCreate(display_name="QA Tester", role=AccountRole.TESTER)
    )
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
    rule = create_eligibility_rule(
        campaign.id,
        EligibilityRuleCreate(
            platform=EligibilityRulePlatform.IOS,
            os_name="iOS",
            os_version_min="17.0",
        ),
        developer.id,
    )
    device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA iPhone 15",
            platform=DeviceProfilePlatform.IOS,
            device_model="iPhone 15 Pro",
            os_name="iOS",
            os_version="17.4",
        ),
        tester.id,
    )
    task = create_task(
        campaign.id,
        TaskCreate(
            title="Validate onboarding flow",
            device_profile_id=device_profile.id,
            status=TaskStatus.ASSIGNED,
        ),
        developer.id,
    )

    detail_before_drift = get_task(task.id)
    assert detail_before_drift.qualification_context is not None
    assert detail_before_drift.qualification_context.device_profile_id == device_profile.id
    assert detail_before_drift.qualification_context.device_profile_name == device_profile.name
    assert detail_before_drift.qualification_context.qualification_status == "qualified"
    assert detail_before_drift.qualification_context.matched_rule_id == rule.id
    assert detail_before_drift.qualification_context.qualification_drift is False

    update_eligibility_rule(
        rule.id,
        EligibilityRuleUpdate(
            platform=EligibilityRulePlatform.ANDROID,
            os_name="Android",
        ),
        developer.id,
    )

    detail_after_drift = get_task(task.id)
    assert detail_after_drift.qualification_context is not None
    assert detail_after_drift.qualification_context.qualification_status == "not_qualified"
    assert detail_after_drift.qualification_context.matched_rule_id is None
    assert detail_after_drift.qualification_context.reason_summary == (
        "主要未符合條件：平台不符合目前活動條件；作業系統不符合目前活動條件。"
    )
    assert detail_after_drift.qualification_context.qualification_drift is True


def test_task_service_list_mine_returns_empty_when_actor_has_no_owned_device_profiles() -> None:
    tester = create_account(
        AccountCreate(display_name="QA Tester", role=AccountRole.TESTER)
    )

    listed_tasks = list_tasks(
        mine=True,
        current_actor_id=tester.id,
    )

    assert listed_tasks.total == 0
    assert listed_tasks.items == []


def test_task_service_list_mine_requires_current_actor() -> None:
    with pytest.raises(AppError) as exc_info:
        list_tasks(mine=True)

    error = exc_info.value
    assert error.status_code == status.HTTP_400_BAD_REQUEST
    assert error.code == "missing_actor_context"
    assert error.details == {
        "header": "X-Actor-Id",
    }


def test_task_service_create_requires_existing_campaign() -> None:
    with pytest.raises(AppError) as exc_info:
        create_task(
            "camp_missing",
            TaskCreate(title="Validate onboarding flow"),
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert error.code == "resource_not_found"
    assert error.details == {
        "resource": "campaign",
        "id": "camp_missing",
    }


def test_task_service_create_requires_existing_device_profile_when_provided() -> None:
    project = create_project(ProjectCreate(name="HabitQuest"))
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )

    with pytest.raises(AppError) as exc_info:
        create_task(
            campaign.id,
            TaskCreate(
                title="Validate onboarding flow",
                device_profile_id="dp_missing",
            ),
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert error.code == "resource_not_found"
    assert error.details == {
        "resource": "device_profile",
        "id": "dp_missing",
    }


def test_task_service_create_rejects_ineligible_assignment() -> None:
    project = create_project(ProjectCreate(name="HabitQuest"))
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )
    device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA Pixel 9",
            platform=DeviceProfilePlatform.ANDROID,
            device_model="Pixel 9",
            os_name="Android",
            os_version="14.0",
        )
    )
    create_eligibility_rule(
        campaign.id,
        EligibilityRuleCreate(
            platform=EligibilityRulePlatform.IOS,
            os_name="iOS",
            os_version_min="17.0",
        ),
    )

    with pytest.raises(AppError) as exc_info:
        create_task(
            campaign.id,
            TaskCreate(
                title="Validate onboarding flow",
                device_profile_id=device_profile.id,
                status=TaskStatus.ASSIGNED,
            ),
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "assignment_not_eligible"
    assert error.details == {
        "campaign_id": campaign.id,
        "device_profile_id": device_profile.id,
        "qualification_status": "not_qualified",
        "matched_rule_id": None,
        "reason_codes": [
            "platform_mismatch",
            "os_name_mismatch",
            "os_version_below_min",
        ],
        "reason_summary": (
            "主要未符合條件：平台不符合目前活動條件；"
            "作業系統不符合目前活動條件；"
            "作業系統版本低於最低要求。"
        ),
    }


def test_task_service_rejects_illegal_status_transition() -> None:
    project = create_project(ProjectCreate(name="HabitQuest"))
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )
    device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA iPhone 15",
            platform=DeviceProfilePlatform.IOS,
            device_model="iPhone 15 Pro",
            os_name="iOS",
        )
    )
    created_task = create_task(
        campaign.id,
        TaskCreate(
            title="Validate onboarding flow",
            device_profile_id=device_profile.id,
            status=TaskStatus.ASSIGNED,
        ),
    )

    with pytest.raises(AppError) as exc_info:
        update_task(
            created_task.id,
            TaskUpdate(status=TaskStatus.SUBMITTED),
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "conflict"
    assert error.details == {
        "resource": "task",
        "current_status": "assigned",
        "next_status": "submitted",
    }


def test_task_service_update_rejects_ineligible_device_profile_assignment() -> None:
    project = create_project(ProjectCreate(name="HabitQuest"))
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )
    create_eligibility_rule(
        campaign.id,
        EligibilityRuleCreate(
            platform=EligibilityRulePlatform.IOS,
            os_name="iOS",
            os_version_min="17.0",
        ),
    )
    eligible_device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA iPhone 15",
            platform=DeviceProfilePlatform.IOS,
            device_model="iPhone 15 Pro",
            os_name="iOS",
            os_version="17.4",
        )
    )
    ineligible_device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA Pixel 9",
            platform=DeviceProfilePlatform.ANDROID,
            device_model="Pixel 9",
            os_name="Android",
            os_version="14.0",
        )
    )
    created_task = create_task(
        campaign.id,
        TaskCreate(
            title="Validate onboarding flow",
            device_profile_id=eligible_device_profile.id,
            status=TaskStatus.ASSIGNED,
        ),
    )

    with pytest.raises(AppError) as exc_info:
        update_task(
            created_task.id,
            TaskUpdate(device_profile_id=ineligible_device_profile.id),
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "assignment_not_eligible"
    assert error.details == {
        "campaign_id": campaign.id,
        "device_profile_id": ineligible_device_profile.id,
        "qualification_status": "not_qualified",
        "matched_rule_id": None,
        "reason_codes": [
            "platform_mismatch",
            "os_name_mismatch",
            "os_version_below_min",
        ],
        "reason_summary": (
            "主要未符合條件：平台不符合目前活動條件；"
            "作業系統不符合目前活動條件；"
            "作業系統版本低於最低要求。"
        ),
    }


def test_task_service_writes_submitted_at_when_entering_submitted() -> None:
    project = create_project(ProjectCreate(name="HabitQuest"))
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )
    device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA iPhone 15",
            platform=DeviceProfilePlatform.IOS,
            device_model="iPhone 15 Pro",
            os_name="iOS",
        )
    )
    created_task = create_task(
        campaign.id,
        TaskCreate(
            title="Validate onboarding flow",
            device_profile_id=device_profile.id,
            status=TaskStatus.ASSIGNED,
        ),
    )

    in_progress_task = update_task(
        created_task.id,
        TaskUpdate(status=TaskStatus.IN_PROGRESS),
    )
    submitted_task = update_task(
        created_task.id,
        TaskUpdate(status=TaskStatus.SUBMITTED),
    )

    assert in_progress_task.submitted_at is None
    assert submitted_task.status == TaskStatus.SUBMITTED
    assert submitted_task.submitted_at is not None


def test_task_service_delete_removes_the_resource() -> None:
    project = create_project(ProjectCreate(name="HabitQuest"))
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )
    created_task = create_task(
        campaign.id,
        TaskCreate(title="Validate onboarding flow"),
    )

    delete_task(created_task.id)

    with pytest.raises(AppError) as exc_info:
        ensure_task_exists(created_task.id)

    assert exc_info.value.code == "resource_not_found"


def test_task_service_delete_rejects_task_with_feedback() -> None:
    project = create_project(ProjectCreate(name="HabitQuest"))
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )
    task = create_task(
        campaign.id,
        TaskCreate(title="Validate onboarding flow"),
    )
    create_feedback(
        task.id,
        FeedbackCreate(
            summary="App crashes on launch",
            severity=FeedbackSeverity.HIGH,
            category=FeedbackCategory.BUG,
        ),
    )

    with pytest.raises(AppError) as exc_info:
        delete_task(task.id)

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "conflict"
    assert error.details == {
        "resource": "task",
        "id": task.id,
        "related_resource": "feedback",
    }
