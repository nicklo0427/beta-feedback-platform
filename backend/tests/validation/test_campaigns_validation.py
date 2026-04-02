from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.campaigns.schemas import CampaignCreate, CampaignStatus, CampaignUpdate


def test_campaign_create_deduplicates_platforms_and_normalizes_strings() -> None:
    payload = CampaignCreate(
        project_id="  proj_123  ",
        name="  Closed Beta Round 1  ",
        description="  Collect onboarding feedback.  ",
        target_platforms=["ios", "ios", "android"],
        version_label="  0.9.0-beta.1  ",
    )

    assert payload.project_id == "proj_123"
    assert payload.name == "Closed Beta Round 1"
    assert payload.description == "Collect onboarding feedback."
    assert payload.target_platforms == ["ios", "android"]
    assert payload.version_label == "0.9.0-beta.1"


def test_campaign_create_rejects_unknown_platform() -> None:
    with pytest.raises(ValidationError) as exc_info:
        CampaignCreate(
            project_id="proj_123",
            name="Closed Beta Round 1",
            target_platforms=["desktop"],
        )

    assert "Input should be 'web', 'h5', 'pwa', 'ios' or 'android'" in str(
        exc_info.value
    )


def test_campaign_update_requires_at_least_one_field() -> None:
    with pytest.raises(ValidationError) as exc_info:
        CampaignUpdate()

    assert "At least one field must be provided." in str(exc_info.value)


def test_campaign_update_accepts_valid_status_enum() -> None:
    payload = CampaignUpdate(status=CampaignStatus.ACTIVE)

    assert payload.status == CampaignStatus.ACTIVE
