from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.accounts.schemas import AccountCreate
from app.modules.accounts.service import create_account
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


def _create_developer_account(name: str = "Dev Owner"):
    return create_account(AccountCreate(display_name=name, role="developer"))


def _create_tester_account(name: str = "Tester Owner"):
    return create_account(AccountCreate(display_name=name, role="tester"))


def test_eligibility_service_create_and_list_returns_expected_items() -> None:
    developer = _create_developer_account()
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

    created_rule = create_eligibility_rule(
        campaign.id,
        EligibilityRuleCreate(
            platform=EligibilityRulePlatform.IOS,
            os_name="iOS",
            install_channel="testflight",
        ),
        current_actor_id=developer.id,
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
    developer = _create_developer_account()
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
    created_rule = create_eligibility_rule(
        campaign.id,
        EligibilityRuleCreate(
            platform=EligibilityRulePlatform.IOS,
            os_name="iOS",
            install_channel="testflight",
        ),
        current_actor_id=developer.id,
    )

    updated_rule = update_eligibility_rule(
        created_rule.id,
        EligibilityRuleUpdate(
            install_channel="app-store-connect",
            is_active=False,
        ),
        current_actor_id=developer.id,
    )

    assert updated_rule.id == created_rule.id
    assert updated_rule.campaign_id == campaign.id
    assert updated_rule.platform == EligibilityRulePlatform.IOS
    assert updated_rule.install_channel == "app-store-connect"
    assert updated_rule.is_active is False


def test_eligibility_service_create_rejects_non_developer_actor() -> None:
    developer = _create_developer_account()
    tester = _create_tester_account()
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

    with pytest.raises(AppError) as exc_info:
        create_eligibility_rule(
            campaign.id,
            EligibilityRuleCreate(platform=EligibilityRulePlatform.IOS),
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


def test_eligibility_service_update_rejects_actor_without_campaign_ownership() -> None:
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
    rule = create_eligibility_rule(
        campaign.id,
        EligibilityRuleCreate(platform=EligibilityRulePlatform.IOS),
        current_actor_id=owner.id,
    )

    with pytest.raises(AppError) as exc_info:
        update_eligibility_rule(
            rule.id,
            EligibilityRuleUpdate(is_active=False),
            current_actor_id=other_developer.id,
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "ownership_mismatch"
    assert error.details == {
        "actor_id": other_developer.id,
        "resource": "eligibility_rule",
        "ownership_anchor": {
            "resource": "project",
            "id": project.id,
            "owner_account_id": owner.id,
        },
    }
