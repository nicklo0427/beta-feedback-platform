from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.accounts.schemas import AccountCreate
from app.modules.accounts.service import create_account
from app.modules.campaigns.schemas import CampaignCreate, CampaignStatus, CampaignUpdate
from app.modules.campaigns.service import create_campaign, list_campaigns, update_campaign
from app.modules.eligibility.schemas import EligibilityRuleCreate, EligibilityRulePlatform
from app.modules.eligibility.service import create_eligibility_rule
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project, delete_project
from app.modules.safety.schemas import CampaignSafetyCreate, DistributionChannel, RiskLevel
from app.modules.safety.service import create_campaign_safety
from app.modules.tasks.schemas import TaskCreate
from app.modules.tasks.service import create_task


def _create_developer_account(name: str = "Dev Owner"):
    return create_account(AccountCreate(display_name=name, role="developer"))


def _create_tester_account(name: str = "Tester Owner"):
    return create_account(AccountCreate(display_name=name, role="tester"))


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


def test_campaign_service_list_supports_mine_filter_for_owned_projects() -> None:
    owner = _create_developer_account("Owner Dev")
    other_developer = _create_developer_account("Other Dev")
    owned_project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=owner.id,
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
        ),
        current_actor_id=owner.id,
    )
    create_campaign(
        CampaignCreate(
            project_id=other_project.id,
            name="Other Campaign",
            target_platforms=["android"],
        ),
        current_actor_id=other_developer.id,
    )

    filtered_campaigns = list_campaigns(
        mine=True,
        current_actor_id=owner.id,
    )

    assert filtered_campaigns.total == 1
    assert filtered_campaigns.items[0].id == owned_campaign.id
    assert filtered_campaigns.items[0].project_id == owned_project.id


def test_campaign_service_list_mine_rejects_non_developer_actor() -> None:
    tester = _create_tester_account()

    with pytest.raises(AppError) as exc_info:
        list_campaigns(mine=True, current_actor_id=tester.id)

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "forbidden_actor_role"
    assert error.details == {
        "actor_id": tester.id,
        "actor_role": "tester",
        "required_role": "developer",
    }


def test_campaign_service_update_changes_allowed_fields_only() -> None:
    developer = _create_developer_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    created_campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
            version_label="0.9.0-beta.1",
        ),
        current_actor_id=developer.id,
    )

    updated_campaign = update_campaign(
        created_campaign.id,
        CampaignUpdate(
            status=CampaignStatus.ACTIVE,
            target_platforms=["ios", "android"],
        ),
        current_actor_id=developer.id,
    )

    assert updated_campaign.id == created_campaign.id
    assert updated_campaign.project_id == project.id
    assert updated_campaign.status == CampaignStatus.ACTIVE
    assert updated_campaign.target_platforms == ["ios", "android"]
    assert updated_campaign.version_label == "0.9.0-beta.1"


def test_campaign_service_create_rejects_non_developer_actor() -> None:
    tester = _create_tester_account()
    developer = _create_developer_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )

    with pytest.raises(AppError) as exc_info:
        create_campaign(
            CampaignCreate(
                project_id=project.id,
                name="Closed Beta Round 1",
                target_platforms=["ios"],
            ),
            current_actor_id=tester.id,
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "forbidden_actor_role"
    assert error.details == {
        "actor_id": tester.id,
        "actor_role": "tester",
        "required_role": "developer",
    }


def test_campaign_service_update_rejects_actor_without_project_ownership() -> None:
    owner = _create_developer_account("Owner Dev")
    other_developer = _create_developer_account("Other Dev")
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=owner.id,
    )
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        ),
        current_actor_id=owner.id,
    )

    with pytest.raises(AppError) as exc_info:
        update_campaign(
            campaign.id,
            CampaignUpdate(status=CampaignStatus.ACTIVE),
            current_actor_id=other_developer.id,
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "ownership_mismatch"
    assert error.details == {
        "actor_id": other_developer.id,
        "resource": "campaign",
        "ownership_anchor": {
            "resource": "project",
            "id": project.id,
            "owner_account_id": owner.id,
        },
    }


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


def test_campaign_service_delete_rejects_campaign_with_safety() -> None:
    from app.modules.campaigns.service import delete_campaign

    project = create_project(ProjectCreate(name="HabitQuest"))
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )
    create_campaign_safety(
        campaign.id,
        CampaignSafetyCreate(
            distribution_channel=DistributionChannel.TESTFLIGHT,
            source_label="TestFlight",
            risk_level=RiskLevel.LOW,
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
        "related_resource": "campaign_safety",
    }
