from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.campaigns.schemas import CampaignCreate
from app.modules.campaigns.service import create_campaign
from app.modules.device_profiles.schemas import DeviceProfileCreate, DeviceProfilePlatform
from app.modules.device_profiles.service import create_device_profile
from app.modules.feedback.schemas import (
    FeedbackCategory,
    FeedbackCreate,
    FeedbackReviewStatus,
    FeedbackSeverity,
    FeedbackUpdate,
)
from app.modules.feedback.service import (
    create_feedback,
    ensure_feedback_exists,
    list_feedback,
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
