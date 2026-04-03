from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.campaigns.schemas import CampaignCreate
from app.modules.campaigns.service import create_campaign
from app.modules.device_profiles.schemas import DeviceProfileCreate, DeviceProfilePlatform
from app.modules.device_profiles.service import create_device_profile
from app.modules.feedback.schemas import FeedbackCategory, FeedbackCreate, FeedbackSeverity
from app.modules.feedback.service import create_feedback
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project
from app.modules.reputation.service import (
    get_campaign_reputation,
    get_device_profile_reputation,
)
from app.modules.tasks.schemas import TaskCreate, TaskStatus, TaskUpdate
from app.modules.tasks.service import create_task, update_task


def test_device_profile_reputation_service_derives_summary_metrics() -> None:
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

    create_task(
        campaign.id,
        TaskCreate(
            title="Assigned task",
            device_profile_id=device_profile.id,
            status=TaskStatus.ASSIGNED,
        ),
    )
    submitted_task = create_task(
        campaign.id,
        TaskCreate(
            title="Submitted task",
            device_profile_id=device_profile.id,
            status=TaskStatus.SUBMITTED,
        ),
    )
    create_task(
        campaign.id,
        TaskCreate(
            title="Open task",
            status=TaskStatus.OPEN,
        ),
    )
    create_feedback(
        submitted_task.id,
        FeedbackCreate(
            summary="App crashes on launch",
            severity=FeedbackSeverity.HIGH,
            category=FeedbackCategory.BUG,
            note="Observed on the same device twice.",
        ),
    )

    summary = get_device_profile_reputation(device_profile.id)

    assert summary.device_profile_id == device_profile.id
    assert summary.tasks_assigned_count == 2
    assert summary.tasks_submitted_count == 1
    assert summary.feedback_submitted_count == 1
    assert summary.submission_rate == 0.5
    assert summary.last_feedback_at is not None
    assert summary.updated_at >= summary.last_feedback_at


def test_device_profile_reputation_service_returns_zero_state_without_activity() -> None:
    device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA Pixel 9",
            platform=DeviceProfilePlatform.ANDROID,
            device_model="Pixel 9",
            os_name="Android",
        )
    )

    summary = get_device_profile_reputation(device_profile.id)

    assert summary.device_profile_id == device_profile.id
    assert summary.tasks_assigned_count == 0
    assert summary.tasks_submitted_count == 0
    assert summary.feedback_submitted_count == 0
    assert summary.submission_rate == 0.0
    assert summary.last_feedback_at is None
    assert summary.updated_at == device_profile.updated_at


def test_campaign_reputation_service_derives_summary_metrics() -> None:
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

    closed_task = create_task(
        campaign.id,
        TaskCreate(
            title="Closed task",
            device_profile_id=device_profile.id,
            status=TaskStatus.SUBMITTED,
        ),
    )
    update_task(closed_task.id, TaskUpdate(status=TaskStatus.CLOSED))

    in_progress_task = create_task(
        campaign.id,
        TaskCreate(
            title="In progress task",
            device_profile_id=device_profile.id,
            status=TaskStatus.IN_PROGRESS,
        ),
    )
    create_feedback(
        in_progress_task.id,
        FeedbackCreate(
            summary="Layout overlaps on small screens",
            severity=FeedbackSeverity.MEDIUM,
            category=FeedbackCategory.USABILITY,
        ),
    )

    summary = get_campaign_reputation(campaign.id)

    assert summary.campaign_id == campaign.id
    assert summary.tasks_total_count == 2
    assert summary.tasks_closed_count == 1
    assert summary.feedback_received_count == 1
    assert summary.closure_rate == 0.5
    assert summary.last_feedback_at is not None
    assert summary.updated_at >= summary.last_feedback_at


def test_reputation_service_requires_existing_anchor() -> None:
    with pytest.raises(AppError) as device_profile_exc:
        get_device_profile_reputation("dp_missing")

    assert device_profile_exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert device_profile_exc.value.code == "resource_not_found"

    with pytest.raises(AppError) as campaign_exc:
        get_campaign_reputation("camp_missing")

    assert campaign_exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert campaign_exc.value.code == "resource_not_found"
