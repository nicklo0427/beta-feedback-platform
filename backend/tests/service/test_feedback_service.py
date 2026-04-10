from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.campaigns.schemas import CampaignCreate
from app.modules.campaigns.service import create_campaign
from app.modules.accounts.schemas import AccountCreate
from app.modules.accounts.service import create_account
from app.modules.device_profiles.schemas import DeviceProfileCreate, DeviceProfilePlatform
from app.modules.device_profiles.service import create_device_profile
from app.modules.feedback.schemas import (
    FeedbackCategory,
    FeedbackCreate,
    FeedbackQueueResponse,
    FeedbackReviewStatus,
    FeedbackSeverity,
    FeedbackUpdate,
)
from app.modules.feedback.service import (
    create_feedback,
    ensure_feedback_exists,
    get_feedback_for_actor,
    list_feedback,
    list_feedback_queue,
    update_feedback,
)
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project
from app.modules.tasks.schemas import TaskCreate, TaskStatus
from app.modules.tasks.service import create_task, get_task


def test_feedback_service_create_and_list_derives_task_relations() -> None:
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
    task = create_task(
        campaign.id,
        TaskCreate(
            title="Validate onboarding flow",
            device_profile_id=device_profile.id,
            status=TaskStatus.ASSIGNED,
        ),
    )

    created_feedback = create_feedback(
        task.id,
        FeedbackCreate(
            summary="App crashes on launch",
            rating=4,
            severity=FeedbackSeverity.HIGH,
            category=FeedbackCategory.BUG,
            actual_result="App exits immediately.",
        ),
    )

    listed_feedback = list_feedback(task.id)
    submitted_task = get_task(task.id)

    assert listed_feedback.total == 1
    assert listed_feedback.items[0].id == created_feedback.id
    assert created_feedback.task_id == task.id
    assert created_feedback.campaign_id == campaign.id
    assert created_feedback.device_profile_id == device_profile.id
    assert created_feedback.review_status == FeedbackReviewStatus.SUBMITTED
    assert created_feedback.developer_note is None
    assert created_feedback.submitted_at is not None
    assert submitted_task.status == TaskStatus.SUBMITTED
    assert submitted_task.submitted_at is not None


def test_feedback_service_create_requires_existing_task() -> None:
    with pytest.raises(AppError) as exc_info:
        create_feedback(
            "task_missing",
            FeedbackCreate(
                summary="App crashes on launch",
                severity=FeedbackSeverity.HIGH,
                category=FeedbackCategory.BUG,
            ),
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert error.code == "resource_not_found"
    assert error.details == {
        "resource": "task",
        "id": "task_missing",
    }


def test_feedback_service_ensure_exists_raises_not_found() -> None:
    with pytest.raises(AppError) as exc_info:
        ensure_feedback_exists("fb_missing")

    error = exc_info.value
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert error.code == "resource_not_found"
    assert error.details == {
        "resource": "feedback",
        "id": "fb_missing",
    }


def test_feedback_service_update_changes_only_allowed_fields() -> None:
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
        TaskCreate(
            title="Validate onboarding flow",
        ),
    )
    created_feedback = create_feedback(
        task.id,
        FeedbackCreate(
            summary="App crashes on launch",
            severity=FeedbackSeverity.HIGH,
            category=FeedbackCategory.BUG,
        ),
    )

    updated_feedback = update_feedback(
        created_feedback.id,
        FeedbackUpdate(
            rating=5,
            category=FeedbackCategory.USABILITY,
            note="Updated after second verification.",
            review_status=FeedbackReviewStatus.NEEDS_MORE_INFO,
            developer_note="Please include the exact device state before launch.",
        ),
    )

    assert updated_feedback.id == created_feedback.id
    assert updated_feedback.task_id == task.id
    assert updated_feedback.summary == "App crashes on launch"
    assert updated_feedback.rating == 5
    assert updated_feedback.category == FeedbackCategory.USABILITY
    assert updated_feedback.note == "Updated after second verification."
    assert updated_feedback.review_status == FeedbackReviewStatus.NEEDS_MORE_INFO
    assert (
        updated_feedback.developer_note
        == "Please include the exact device state before launch."
    )
    assert updated_feedback.resubmitted_at is None


def test_feedback_service_resubmission_resets_review_status_and_sets_timestamp() -> None:
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
        TaskCreate(
            title="Validate onboarding flow",
        ),
    )
    created_feedback = create_feedback(
        task.id,
        FeedbackCreate(
            summary="App crashes on launch",
            severity=FeedbackSeverity.HIGH,
            category=FeedbackCategory.BUG,
            actual_result="App exits immediately.",
        ),
    )

    review_requested_feedback = update_feedback(
        created_feedback.id,
        FeedbackUpdate(
            review_status=FeedbackReviewStatus.NEEDS_MORE_INFO,
            developer_note="Please include the exact time between launch and crash.",
        ),
    )

    resubmitted_feedback = update_feedback(
        created_feedback.id,
        FeedbackUpdate(
            actual_result="App exits immediately after three seconds on a cold launch.",
            note="Retested with screen recording enabled.",
        ),
    )

    assert review_requested_feedback.review_status == FeedbackReviewStatus.NEEDS_MORE_INFO
    assert review_requested_feedback.resubmitted_at is None
    assert resubmitted_feedback.review_status == FeedbackReviewStatus.SUBMITTED
    assert resubmitted_feedback.resubmitted_at is not None
    assert (
        resubmitted_feedback.developer_note
        == "Please include the exact time between launch and crash."
    )
    assert (
        resubmitted_feedback.actual_result
        == "App exits immediately after three seconds on a cold launch."
    )


def test_feedback_service_content_update_does_not_set_resubmitted_at_when_not_requested() -> None:
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
        TaskCreate(
            title="Validate onboarding flow",
        ),
    )
    created_feedback = create_feedback(
        task.id,
        FeedbackCreate(
            summary="App crashes on launch",
            severity=FeedbackSeverity.HIGH,
            category=FeedbackCategory.BUG,
        ),
    )

    updated_feedback = update_feedback(
        created_feedback.id,
        FeedbackUpdate(
            note="Retested on a second device.",
        ),
    )

    assert updated_feedback.review_status == FeedbackReviewStatus.SUBMITTED
    assert updated_feedback.resubmitted_at is None


def test_feedback_service_list_queue_supports_mine_filter_for_owned_projects() -> None:
    developer = create_account(
        AccountCreate(
            display_name="Release Owner",
            role="developer",
        )
    )
    other_developer = create_account(
        AccountCreate(
            display_name="Another Dev",
            role="developer",
        )
    )
    tester = create_account(
        AccountCreate(
            display_name="QA Tester",
            role="tester",
        )
    )

    owned_project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    other_project = create_project(
        ProjectCreate(name="FocusFlow"),
        current_actor_id=other_developer.id,
    )

    owned_campaign = create_campaign(
        CampaignCreate(
            project_id=owned_project.id,
            name="Owned Campaign",
            target_platforms=["ios"],
        )
    )
    other_campaign = create_campaign(
        CampaignCreate(
            project_id=other_project.id,
            name="Other Campaign",
            target_platforms=["android"],
        )
    )

    device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA iPhone 15",
            platform=DeviceProfilePlatform.IOS,
            device_model="iPhone 15 Pro",
            os_name="iOS",
        ),
        current_actor_id=tester.id,
    )

    owned_task = create_task(
        owned_campaign.id,
        TaskCreate(
            title="Validate onboarding flow",
            device_profile_id=device_profile.id,
            status=TaskStatus.SUBMITTED,
        ),
    )
    other_task = create_task(
        other_campaign.id,
        TaskCreate(
            title="Validate Android onboarding",
            device_profile_id=device_profile.id,
            status=TaskStatus.SUBMITTED,
        ),
    )

    owned_feedback = create_feedback(
        owned_task.id,
        FeedbackCreate(
            summary="Owned feedback",
            severity=FeedbackSeverity.HIGH,
            category=FeedbackCategory.BUG,
        ),
    )
    create_feedback(
        other_task.id,
        FeedbackCreate(
            summary="Other feedback",
            severity=FeedbackSeverity.MEDIUM,
            category=FeedbackCategory.USABILITY,
        ),
    )

    queue = list_feedback_queue(mine=True, current_actor_id=developer.id)

    assert isinstance(queue, FeedbackQueueResponse)
    assert queue.total == 1
    assert queue.items[0].id == owned_feedback.id
    assert queue.items[0].campaign_id == owned_campaign.id
    assert queue.items[0].review_status == FeedbackReviewStatus.SUBMITTED


def test_feedback_service_list_queue_supports_review_status_filter() -> None:
    developer = create_account(
        AccountCreate(
            display_name="Release Owner",
            role="developer",
        )
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
    task = create_task(
        campaign.id,
        TaskCreate(title="Validate onboarding flow"),
    )
    feedback = create_feedback(
        task.id,
        FeedbackCreate(
            summary="Need more details",
            severity=FeedbackSeverity.HIGH,
            category=FeedbackCategory.BUG,
        ),
    )
    update_feedback(
        feedback.id,
        FeedbackUpdate(
            review_status=FeedbackReviewStatus.NEEDS_MORE_INFO,
        ),
    )

    queue = list_feedback_queue(
        review_status=FeedbackReviewStatus.NEEDS_MORE_INFO,
        current_actor_id=developer.id,
    )

    assert queue.total == 1
    assert queue.items[0].id == feedback.id
    assert queue.items[0].review_status == FeedbackReviewStatus.NEEDS_MORE_INFO


def test_feedback_service_list_queue_requires_current_actor() -> None:
    with pytest.raises(AppError) as exc_info:
        list_feedback_queue()

    error = exc_info.value
    assert error.status_code == status.HTTP_400_BAD_REQUEST
    assert error.code == "missing_actor_context"
    assert error.details == {
        "header": "X-Actor-Id",
    }


def test_feedback_service_list_queue_supports_owned_feedback_for_tester() -> None:
    tester = create_account(
        AccountCreate(
            display_name="QA Tester",
            role="tester",
        )
    )
    other_tester = create_account(
        AccountCreate(
            display_name="Other Tester",
            role="tester",
        )
    )
    developer = create_account(
        AccountCreate(
            display_name="Release Owner",
            role="developer",
        )
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
    owned_device_profile = create_device_profile(
        DeviceProfileCreate(
            name="Owned Device",
            platform=DeviceProfilePlatform.IOS,
            device_model="iPhone 15",
            os_name="iOS",
        ),
        current_actor_id=tester.id,
    )
    other_device_profile = create_device_profile(
        DeviceProfileCreate(
            name="Other Device",
            platform=DeviceProfilePlatform.IOS,
            device_model="iPhone 15",
            os_name="iOS",
        ),
        current_actor_id=other_tester.id,
    )
    owned_task = create_task(
        campaign.id,
        TaskCreate(
            title="Owned Feedback Task",
            device_profile_id=owned_device_profile.id,
            status=TaskStatus.SUBMITTED,
        ),
        current_actor_id=developer.id,
    )
    other_task = create_task(
        campaign.id,
        TaskCreate(
            title="Other Feedback Task",
            device_profile_id=other_device_profile.id,
            status=TaskStatus.SUBMITTED,
        ),
        current_actor_id=developer.id,
    )
    owned_feedback = create_feedback(
        owned_task.id,
        FeedbackCreate(
            summary="Owned feedback",
            severity=FeedbackSeverity.HIGH,
            category=FeedbackCategory.BUG,
        ),
        current_actor_id=tester.id,
    )
    create_feedback(
        other_task.id,
        FeedbackCreate(
            summary="Other feedback",
            severity=FeedbackSeverity.MEDIUM,
            category=FeedbackCategory.USABILITY,
        ),
        current_actor_id=other_tester.id,
    )

    queue = list_feedback_queue(current_actor_id=tester.id)

    assert queue.total == 1
    assert queue.items[0].id == owned_feedback.id


def test_feedback_service_get_detail_requires_matching_actor_scope() -> None:
    developer = create_account(
        AccountCreate(
            display_name="Release Owner",
            role="developer",
        )
    )
    tester = create_account(
        AccountCreate(
            display_name="QA Tester",
            role="tester",
        )
    )
    other_tester = create_account(
        AccountCreate(
            display_name="Other Tester",
            role="tester",
        )
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
            title="Owned Feedback Task",
            device_profile_id=device_profile.id,
            status=TaskStatus.SUBMITTED,
        ),
        current_actor_id=developer.id,
    )
    feedback = create_feedback(
        task.id,
        FeedbackCreate(
            summary="Owned feedback",
            severity=FeedbackSeverity.HIGH,
            category=FeedbackCategory.BUG,
        ),
        current_actor_id=tester.id,
    )

    detail = get_feedback_for_actor(feedback.id, tester.id)

    assert detail.id == feedback.id

    with pytest.raises(AppError) as exc_info:
        get_feedback_for_actor(feedback.id, other_tester.id)

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "ownership_mismatch"
    assert error.details == {
        "actor_id": other_tester.id,
        "resource": "feedback",
        "ownership_anchor": {
            "resource": "device_profile",
            "id": device_profile.id,
            "owner_account_id": tester.id,
        },
    }
