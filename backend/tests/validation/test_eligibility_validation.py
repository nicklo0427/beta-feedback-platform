from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.eligibility.schemas import (
    EligibilityRuleCreate,
    EligibilityRulePlatform,
    EligibilityRuleUpdate,
)


def test_eligibility_create_normalizes_optional_strings() -> None:
    payload = EligibilityRuleCreate(
        platform=EligibilityRulePlatform.IOS,
        os_name="  iOS  ",
        os_version_min="  17.0  ",
        os_version_max="  18.2  ",
        install_channel="  testflight  ",
    )

    assert payload.os_name == "iOS"
    assert payload.os_version_min == "17.0"
    assert payload.os_version_max == "18.2"
    assert payload.install_channel == "testflight"
    assert payload.is_active is True


def test_eligibility_create_rejects_unknown_platform() -> None:
    with pytest.raises(ValidationError) as exc_info:
        EligibilityRuleCreate(platform="desktop")

    assert "Input should be 'web', 'h5', 'pwa', 'ios' or 'android'" in str(
        exc_info.value
    )


def test_eligibility_create_normalizes_blank_optional_strings_to_none() -> None:
    payload = EligibilityRuleCreate(
        platform=EligibilityRulePlatform.WEB,
        os_name="   ",
        os_version_min="   ",
        os_version_max="   ",
        install_channel="   ",
    )

    assert payload.os_name is None
    assert payload.os_version_min is None
    assert payload.os_version_max is None
    assert payload.install_channel is None


def test_eligibility_update_requires_at_least_one_field() -> None:
    with pytest.raises(ValidationError) as exc_info:
        EligibilityRuleUpdate()

    assert "At least one field must be provided." in str(exc_info.value)


def test_eligibility_update_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        EligibilityRuleUpdate(campaign_id="camp_123")

    assert "Extra inputs are not permitted" in str(exc_info.value)
