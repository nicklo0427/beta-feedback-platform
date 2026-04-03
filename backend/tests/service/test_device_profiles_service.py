from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.device_profiles.schemas import (
    DeviceProfileCreate,
    DeviceProfilePlatform,
    DeviceProfileUpdate,
)
from app.modules.device_profiles.service import (
    create_device_profile,
    delete_device_profile,
    ensure_device_profile_exists,
    list_device_profiles,
    update_device_profile,
)
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project
from app.modules.campaigns.schemas import CampaignCreate
from app.modules.campaigns.service import create_campaign
from app.modules.tasks.schemas import TaskCreate, TaskStatus
from app.modules.tasks.service import create_task


def test_device_profile_service_create_and_list_returns_expected_items() -> None:
    created_device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA iPhone 15",
            platform=DeviceProfilePlatform.IOS,
            device_model="iPhone 15 Pro",
            os_name="iOS",
            os_version="18.1",
        )
    )

    listed_device_profiles = list_device_profiles()

    assert listed_device_profiles.total == 1
    assert listed_device_profiles.items[0].id == created_device_profile.id
    assert listed_device_profiles.items[0].name == "QA iPhone 15"
    assert listed_device_profiles.items[0].platform == DeviceProfilePlatform.IOS
    assert listed_device_profiles.items[0].device_model == "iPhone 15 Pro"


def test_device_profile_service_ensure_exists_raises_not_found() -> None:
    with pytest.raises(AppError) as exc_info:
        ensure_device_profile_exists("dp_missing")

    error = exc_info.value
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert error.code == "resource_not_found"
    assert error.details == {
        "resource": "device_profile",
        "id": "dp_missing",
    }


def test_device_profile_service_update_changes_only_provided_fields() -> None:
    created_device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA Pixel 9",
            platform=DeviceProfilePlatform.ANDROID,
            device_model="Pixel 9",
            os_name="Android",
            os_version="15",
            browser_name="Chrome",
        )
    )

    updated_device_profile = update_device_profile(
        created_device_profile.id,
        DeviceProfileUpdate(
            browser_name="Chrome Beta",
            notes="Reserved for shell testing.",
        ),
    )

    assert updated_device_profile.id == created_device_profile.id
    assert updated_device_profile.platform == DeviceProfilePlatform.ANDROID
    assert updated_device_profile.device_model == "Pixel 9"
    assert updated_device_profile.browser_name == "Chrome Beta"
    assert updated_device_profile.notes == "Reserved for shell testing."


def test_device_profile_service_delete_removes_the_resource() -> None:
    created_device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA PWA Tablet",
            platform=DeviceProfilePlatform.PWA,
            device_model="iPad Air",
            os_name="iPadOS",
        )
    )

    delete_device_profile(created_device_profile.id)

    with pytest.raises(AppError) as exc_info:
        ensure_device_profile_exists(created_device_profile.id)

    assert exc_info.value.code == "resource_not_found"


def test_device_profile_service_delete_rejects_device_profile_with_tasks() -> None:
    project = create_project(ProjectCreate(name="HabitQuest"))
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )
    created_device_profile = create_device_profile(
        DeviceProfileCreate(
            name="QA PWA Tablet",
            platform=DeviceProfilePlatform.PWA,
            device_model="iPad Air",
            os_name="iPadOS",
        )
    )
    create_task(
        campaign.id,
        TaskCreate(
            title="Validate onboarding flow",
            device_profile_id=created_device_profile.id,
            status=TaskStatus.ASSIGNED,
        ),
    )

    with pytest.raises(AppError) as exc_info:
        delete_device_profile(created_device_profile.id)

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "conflict"
    assert error.details == {
        "resource": "device_profile",
        "id": created_device_profile.id,
        "related_resource": "task",
    }
