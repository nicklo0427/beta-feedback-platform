from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.accounts.schemas import AccountCreate
from app.modules.accounts.service import create_account
from app.modules.campaigns.schemas import CampaignCreate
from app.modules.campaigns.service import create_campaign
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project
from app.modules.safety.schemas import (
    CampaignSafetyCreate,
    CampaignSafetyUpdate,
    DistributionChannel,
    ReviewStatus,
    RiskLevel,
)
from app.modules.safety.service import (
    create_campaign_safety,
    delete_campaign_safety,
    ensure_campaign_safety_exists,
    get_campaign_safety,
    update_campaign_safety,
)


def _create_developer_account(name: str = "Dev Owner"):
    return create_account(AccountCreate(display_name=name, role="developer"))


def _create_tester_account(name: str = "Tester Owner"):
    return create_account(AccountCreate(display_name=name, role="tester"))


def test_campaign_safety_service_create_and_get_returns_expected_resource() -> None:
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

    created_safety = create_campaign_safety(
        campaign.id,
        CampaignSafetyCreate(
            distribution_channel=DistributionChannel.TESTFLIGHT,
            source_label="TestFlight",
            risk_level=RiskLevel.LOW,
            review_status=ReviewStatus.APPROVED,
            official_channel_only=True,
        ),
        current_actor_id=developer.id,
    )

    retrieved_safety = get_campaign_safety(campaign.id)

    assert retrieved_safety.id == created_safety.id
    assert retrieved_safety.campaign_id == campaign.id
    assert retrieved_safety.distribution_channel == DistributionChannel.TESTFLIGHT
    assert retrieved_safety.source_label == "TestFlight"
    assert retrieved_safety.risk_level == RiskLevel.LOW
    assert retrieved_safety.review_status == ReviewStatus.APPROVED
    assert retrieved_safety.official_channel_only is True


def test_campaign_safety_service_create_requires_existing_campaign() -> None:
    with pytest.raises(AppError) as exc_info:
        create_campaign_safety(
            "camp_missing",
            CampaignSafetyCreate(
                distribution_channel=DistributionChannel.WEB_URL,
                source_label="Official testing site",
                risk_level=RiskLevel.MEDIUM,
            ),
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert error.code == "resource_not_found"
    assert error.details == {
        "resource": "campaign",
        "id": "camp_missing",
    }


def test_campaign_safety_service_create_rejects_duplicate_safety() -> None:
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
        create_campaign_safety(
            campaign.id,
            CampaignSafetyCreate(
                distribution_channel=DistributionChannel.MANUAL_INVITE,
                source_label="Manual invite link",
                risk_level=RiskLevel.HIGH,
            ),
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "conflict"
    assert error.details == {
        "resource": "campaign_safety",
        "campaign_id": campaign.id,
    }


def test_campaign_safety_service_update_changes_only_provided_fields() -> None:
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
    create_campaign_safety(
        campaign.id,
        CampaignSafetyCreate(
            distribution_channel=DistributionChannel.TESTFLIGHT,
            source_label="TestFlight",
            risk_level=RiskLevel.LOW,
        ),
        current_actor_id=developer.id,
    )

    updated_safety = update_campaign_safety(
        campaign.id,
        CampaignSafetyUpdate(
            risk_level=RiskLevel.MEDIUM,
            risk_note="Manual review required before sharing to broader testers.",
        ),
        current_actor_id=developer.id,
    )

    assert updated_safety.campaign_id == campaign.id
    assert updated_safety.distribution_channel == DistributionChannel.TESTFLIGHT
    assert updated_safety.risk_level == RiskLevel.MEDIUM
    assert (
        updated_safety.risk_note
        == "Manual review required before sharing to broader testers."
    )


def test_campaign_safety_service_create_rejects_non_developer_actor() -> None:
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
        create_campaign_safety(
            campaign.id,
            CampaignSafetyCreate(
                distribution_channel=DistributionChannel.TESTFLIGHT,
                source_label="TestFlight",
                risk_level=RiskLevel.LOW,
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


def test_campaign_safety_service_update_rejects_actor_without_campaign_ownership() -> None:
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
    create_campaign_safety(
        campaign.id,
        CampaignSafetyCreate(
            distribution_channel=DistributionChannel.TESTFLIGHT,
            source_label="TestFlight",
            risk_level=RiskLevel.LOW,
        ),
        current_actor_id=owner.id,
    )

    with pytest.raises(AppError) as exc_info:
        update_campaign_safety(
            campaign.id,
            CampaignSafetyUpdate(risk_level=RiskLevel.MEDIUM),
            current_actor_id=other_developer.id,
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "ownership_mismatch"
    assert error.details == {
        "actor_id": other_developer.id,
        "resource": "campaign_safety",
        "ownership_anchor": {
            "resource": "project",
            "id": project.id,
            "owner_account_id": owner.id,
        },
    }


def test_campaign_safety_service_delete_removes_resource() -> None:
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

    delete_campaign_safety(campaign.id)

    with pytest.raises(AppError) as exc_info:
        ensure_campaign_safety_exists(campaign.id)

    assert exc_info.value.code == "resource_not_found"
