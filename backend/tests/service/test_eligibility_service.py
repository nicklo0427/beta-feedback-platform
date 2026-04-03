from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.campaigns.schemas import CampaignCreate
from app.modules.campaigns.service import create_campaign
from app.modules.eligibility.schemas import (
    EligibilityRuleCreate,
    EligibilityRulePlatform,
    EligibilityRuleUpdate,
)
from app.modules.eligibility.service import (
    create_eligibility_rule,
    ensure_eligibility_rule_exists,
    list_eligibility_rules,
    update_eligibility_rule,
)
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project


def test_eligibility_service_create_and_list_returns_expected_items() -> None:
    project = create_project(ProjectCreate(name="HabitQuest"))
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )

    created_rule = create_eligibility_rule(
        campaign.id,
        EligibilityRuleCreate(
            platform=EligibilityRulePlatform.IOS,
            os_name="iOS",
            install_channel="testflight",
        ),
    )

    listed_rules = list_eligibility_rules(campaign.id)

    assert listed_rules.total == 1
    assert listed_rules.items[0].id == created_rule.id
    assert listed_rules.items[0].campaign_id == campaign.id
    assert listed_rules.items[0].platform == EligibilityRulePlatform.IOS
    assert listed_rules.items[0].install_channel == "testflight"


def test_eligibility_service_create_requires_existing_campaign() -> None:
    with pytest.raises(AppError) as exc_info:
        create_eligibility_rule(
            "camp_missing",
            EligibilityRuleCreate(platform=EligibilityRulePlatform.IOS),
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert error.code == "resource_not_found"
    assert error.details == {
        "resource": "campaign",
        "id": "camp_missing",
    }


def test_eligibility_service_ensure_rule_exists_raises_not_found() -> None:
    with pytest.raises(AppError) as exc_info:
        ensure_eligibility_rule_exists("er_missing")

    error = exc_info.value
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert error.code == "resource_not_found"
    assert error.details == {
        "resource": "eligibility_rule",
        "id": "er_missing",
    }


def test_eligibility_service_update_changes_allowed_fields_only() -> None:
    project = create_project(ProjectCreate(name="HabitQuest"))
    campaign = create_campaign(
        CampaignCreate(
            project_id=project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )
    created_rule = create_eligibility_rule(
        campaign.id,
        EligibilityRuleCreate(
            platform=EligibilityRulePlatform.IOS,
            os_name="iOS",
            install_channel="testflight",
        ),
    )

    updated_rule = update_eligibility_rule(
        created_rule.id,
        EligibilityRuleUpdate(
            install_channel="app-store-connect",
            is_active=False,
        ),
    )

    assert updated_rule.id == created_rule.id
    assert updated_rule.campaign_id == campaign.id
    assert updated_rule.platform == EligibilityRulePlatform.IOS
    assert updated_rule.install_channel == "app-store-connect"
    assert updated_rule.is_active is False
