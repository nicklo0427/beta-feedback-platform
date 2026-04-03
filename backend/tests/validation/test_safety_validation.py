from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.safety.schemas import (
    CampaignSafetyCreate,
    CampaignSafetyUpdate,
    DistributionChannel,
    ReviewStatus,
    RiskLevel,
)


def test_campaign_safety_create_normalizes_optional_strings() -> None:
    payload = CampaignSafetyCreate(
        distribution_channel=DistributionChannel.TESTFLIGHT,
        source_label="  TestFlight  ",
        source_url="  https://testflight.apple.com/join/example  ",
        risk_level=RiskLevel.LOW,
        review_status=ReviewStatus.APPROVED,
        official_channel_only=True,
        risk_note="  Install only from the official invite flow.  ",
    )

    assert payload.source_label == "TestFlight"
    assert payload.source_url == "https://testflight.apple.com/join/example"
    assert payload.risk_note == "Install only from the official invite flow."


def test_campaign_safety_create_rejects_blank_source_label() -> None:
    with pytest.raises(ValidationError) as exc_info:
        CampaignSafetyCreate(
            distribution_channel=DistributionChannel.WEB_URL,
            source_label="   ",
            risk_level=RiskLevel.MEDIUM,
        )

    assert "Source label cannot be blank." in str(exc_info.value)


def test_campaign_safety_create_rejects_unknown_distribution_channel() -> None:
    with pytest.raises(ValidationError) as exc_info:
        CampaignSafetyCreate(
            distribution_channel="steam_key",
            source_label="Steam key",
            risk_level=RiskLevel.HIGH,
        )

    assert (
        "Input should be 'web_url', 'pwa_url', 'testflight', 'google_play_testing', 'manual_invite' or 'other'"
        in str(exc_info.value)
    )


def test_campaign_safety_update_requires_at_least_one_field() -> None:
    with pytest.raises(ValidationError) as exc_info:
        CampaignSafetyUpdate()

    assert "At least one field must be provided." in str(exc_info.value)


def test_campaign_safety_update_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        CampaignSafetyUpdate(campaign_id="camp_123")

    assert "Extra inputs are not permitted" in str(exc_info.value)
