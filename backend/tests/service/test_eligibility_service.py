from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.accounts.schemas import AccountCreate
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
from app.modules.eligibility.service import (
    create_eligibility_rule,
    ensure_eligibility_rule_exists,
    get_campaign_qualification_check,
    list_campaign_qualification_results,
    list_eligibility_rules,
    update_eligibility_rule,
)
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project


def _create_developer_account(name: str = "Dev Owner"):
    return create_account(AccountCreate(display_name=name, role="developer"))


def _create_tester_account(name: str = "Tester Owner"):
    return create_account(AccountCreate(display_name=name, role="tester"))


def _create_device_profile_for_tester(
    tester_id: str,
    *,
    name: str = "iPhone 15",
    platform: DeviceProfilePlatform = DeviceProfilePlatform.IOS,
    os_name: str = "iOS",
    os_version: str | None = "17.4",
    install_channel: str | None = None,
):
    return create_device_profile(
        DeviceProfileCreate(
            name=name,
            platform=platform,
            device_model="Device Model",
            os_name=os_name,
            os_version=os_version,
            install_channel=install_channel,
        ),
        current_actor_id=tester_id,
    )


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


def test_campaign_qualification_results_return_qualified_when_no_active_rules() -> None:
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
    device_profile = _create_device_profile_for_tester(tester.id)

    results = list_campaign_qualification_results(campaign.id, tester.id)

    assert results.total == 1
    assert results.items[0].device_profile_id == device_profile.id
    assert results.items[0].device_profile_name == device_profile.name
    assert results.items[0].qualification_status == "qualified"
    assert results.items[0].matched_rule_id is None
    assert results.items[0].reason_codes == []
    assert results.items[0].reason_summary == "目前沒有啟用中的資格限制。"


def test_campaign_qualification_results_return_match_for_active_rule() -> None:
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
    _create_device_profile_for_tester(
        tester.id,
        name="iPhone 15 Pro",
        platform=DeviceProfilePlatform.IOS,
        os_name="iOS",
        os_version="17.4",
        install_channel="testflight",
    )
    rule = create_eligibility_rule(
        campaign.id,
        EligibilityRuleCreate(
            platform=EligibilityRulePlatform.IOS,
            os_name="iOS",
            os_version_min="17.0",
            install_channel="testflight",
        ),
        current_actor_id=developer.id,
    )

    results = list_campaign_qualification_results(campaign.id, tester.id)

    assert results.total == 1
    assert results.items[0].qualification_status == "qualified"
    assert results.items[0].matched_rule_id == rule.id
    assert results.items[0].reason_codes == []
    assert results.items[0].reason_summary == "符合目前活動的資格條件。"


def test_campaign_qualification_results_return_fail_reasons() -> None:
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
    _create_device_profile_for_tester(
        tester.id,
        name="iPhone 15 Pro",
        platform=DeviceProfilePlatform.IOS,
        os_name="iOS",
        os_version="17.4",
        install_channel="app-store-connect",
    )
    create_eligibility_rule(
        campaign.id,
        EligibilityRuleCreate(
            platform=EligibilityRulePlatform.IOS,
            os_name="iOS",
            os_version_min="17.0",
            install_channel="testflight",
        ),
        current_actor_id=developer.id,
    )

    results = list_campaign_qualification_results(campaign.id, tester.id)

    assert results.total == 1
    assert results.items[0].qualification_status == "not_qualified"
    assert results.items[0].matched_rule_id is None
    assert results.items[0].reason_codes == ["install_channel_mismatch"]
    assert results.items[0].reason_summary == "主要未符合條件：安裝渠道不符合目前活動條件。"


def test_campaign_qualification_results_require_tester_actor() -> None:
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

    with pytest.raises(AppError) as exc_info:
        list_campaign_qualification_results(campaign.id, developer.id)

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "forbidden_actor_role"
    assert error.details == {
        "actor_id": developer.id,
        "actor_role": "developer",
        "required_role": "tester",
    }


def test_campaign_qualification_check_returns_match_for_campaign_owner() -> None:
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
    device_profile = _create_device_profile_for_tester(
        tester.id,
        name="iPhone 15 Pro",
        platform=DeviceProfilePlatform.IOS,
        os_name="iOS",
        os_version="17.4",
        install_channel="testflight",
    )
    rule = create_eligibility_rule(
        campaign.id,
        EligibilityRuleCreate(
            platform=EligibilityRulePlatform.IOS,
            os_name="iOS",
            os_version_min="17.0",
            install_channel="testflight",
        ),
        current_actor_id=developer.id,
    )

    result = get_campaign_qualification_check(
        campaign.id,
        device_profile.id,
        developer.id,
    )

    assert result.device_profile_id == device_profile.id
    assert result.device_profile_name == device_profile.name
    assert result.qualification_status == "qualified"
    assert result.matched_rule_id == rule.id
    assert result.reason_codes == []
    assert result.reason_summary == "符合目前活動的資格條件。"


def test_campaign_qualification_check_returns_fail_reason_summary() -> None:
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
    device_profile = _create_device_profile_for_tester(
        tester.id,
        name="iPhone 15 Pro",
        platform=DeviceProfilePlatform.IOS,
        os_name="iOS",
        os_version="17.4",
        install_channel="app-store-connect",
    )
    create_eligibility_rule(
        campaign.id,
        EligibilityRuleCreate(
            platform=EligibilityRulePlatform.IOS,
            os_name="iOS",
            os_version_min="17.0",
            install_channel="testflight",
        ),
        current_actor_id=developer.id,
    )

    result = get_campaign_qualification_check(
        campaign.id,
        device_profile.id,
        developer.id,
    )

    assert result.device_profile_id == device_profile.id
    assert result.qualification_status == "not_qualified"
    assert result.matched_rule_id is None
    assert result.reason_codes == [
        "install_channel_mismatch",
    ]
    assert result.reason_summary == (
        "主要未符合條件：安裝渠道不符合目前活動條件。"
    )
