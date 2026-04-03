from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.campaigns.schemas import CampaignCreate, CampaignStatus, CampaignUpdate
from app.modules.campaigns.service import create_campaign, list_campaigns, update_campaign
from app.modules.eligibility.schemas import EligibilityRuleCreate, EligibilityRulePlatform
from app.modules.eligibility.service import create_eligibility_rule
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project, delete_project
from app.modules.tasks.schemas import TaskCreate
from app.modules.tasks.service import create_task


def test_campaign_service_create_requires_existing_project() -> None:
    with pytest.raises(AppError) as exc_info:
        create_campaign(
            CampaignCreate(
                project_id="proj_missing",
                name="Closed Beta Round 1",
                target_platforms=["ios"],
            )
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert error.code == "resource_not_found"
    assert error.details == {
        "resource": "project",
        "id": "proj_missing",
    }


def test_campaign_service_list_filters_by_project_id() -> None:
    first_project = create_project(ProjectCreate(name="HabitQuest"))
    second_project = create_project(ProjectCreate(name="FocusFlow"))

    first_campaign = create_campaign(
        CampaignCreate(
            project_id=first_project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )
    create_campaign(
        CampaignCreate(
            project_id=second_project.id,
            name="Closed Beta Round 2",
            target_platforms=["android"],
        )
    )

    filtered_campaigns = list_campaigns(project_id=first_project.id)

    assert filtered_campaigns.total == 1
    assert filtered_campaigns.items[0].id == first_campaign.id
    assert filtered_campaigns.items[0].project_id == first_project.id


def test_campaign_service_update_changes_allowed_fields_only() -> None:
    project = create_project(ProjectCreate(name="HabitQuest"))
    created_campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
            version_label="0.9.0-beta.1",
        )
    )

    updated_campaign = update_campaign(
        created_campaign.id,
        CampaignUpdate(
            status=CampaignStatus.ACTIVE,
            target_platforms=["ios", "android"],
        ),
    )

    assert updated_campaign.id == created_campaign.id
    assert updated_campaign.project_id == project.id
    assert updated_campaign.status == CampaignStatus.ACTIVE
    assert updated_campaign.target_platforms == ["ios", "android"]
    assert updated_campaign.version_label == "0.9.0-beta.1"


def test_campaign_service_delete_rejects_campaign_with_eligibility_rules() -> None:
    from app.modules.campaigns.service import delete_campaign

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
        ),
    )

    with pytest.raises(AppError) as exc_info:
        delete_campaign(campaign.id)

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "conflict"
    assert error.details == {
        "resource": "campaign",
        "id": campaign.id,
        "related_resource": "eligibility_rule",
    }


def test_campaign_service_delete_rejects_campaign_with_tasks() -> None:
    from app.modules.campaigns.service import delete_campaign

    project = create_project(ProjectCreate(name="HabitQuest"))
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )
    create_task(
        campaign.id,
        TaskCreate(title="Validate onboarding flow"),
    )

    with pytest.raises(AppError) as exc_info:
        delete_campaign(campaign.id)

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "conflict"
    assert error.details == {
        "resource": "campaign",
        "id": campaign.id,
        "related_resource": "task",
    }
