from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.device_profiles.schemas import (
    DeviceProfileCreate,
    DeviceProfilePlatform,
    DeviceProfileUpdate,
)


def test_device_profile_create_normalizes_required_and_optional_strings() -> None:
    payload = DeviceProfileCreate(
        name="  QA iPhone 15  ",
        platform=DeviceProfilePlatform.IOS,
        device_model="  iPhone 15 Pro  ",
        os_name="  iOS  ",
        os_version="  18.1  ",
        browser_name="  Safari  ",
        browser_version="  18.0  ",
        locale="  zh-TW  ",
        notes="  Internal test device  ",
    )

    assert payload.name == "QA iPhone 15"
    assert payload.device_model == "iPhone 15 Pro"
    assert payload.os_name == "iOS"
    assert payload.os_version == "18.1"
    assert payload.browser_name == "Safari"
    assert payload.browser_version == "18.0"
    assert payload.locale == "zh-TW"
    assert payload.notes == "Internal test device"


def test_device_profile_create_rejects_blank_required_field() -> None:
    with pytest.raises(ValidationError) as exc_info:
        DeviceProfileCreate(
            name="   ",
            platform=DeviceProfilePlatform.WEB,
            device_model="MacBook Pro",
            os_name="macOS",
        )

    assert "This field cannot be blank." in str(exc_info.value)


def test_device_profile_create_rejects_unknown_platform() -> None:
    with pytest.raises(ValidationError) as exc_info:
        DeviceProfileCreate(
            name="QA Desktop Browser",
            platform="desktop",
            device_model="MacBook Pro",
            os_name="macOS",
        )

    assert "Input should be 'web', 'h5', 'pwa', 'ios' or 'android'" in str(
        exc_info.value
    )


def test_device_profile_create_normalizes_empty_optional_strings_to_none() -> None:
    payload = DeviceProfileCreate(
        name="QA Android",
        platform=DeviceProfilePlatform.ANDROID,
        device_model="Pixel 9",
        os_name="Android",
        os_version="   ",
        browser_name="   ",
        browser_version="   ",
        locale="   ",
        notes="   ",
    )

    assert payload.os_version is None
    assert payload.browser_name is None
    assert payload.browser_version is None
    assert payload.locale is None
    assert payload.notes is None


def test_device_profile_update_requires_at_least_one_field() -> None:
    with pytest.raises(ValidationError) as exc_info:
        DeviceProfileUpdate()

    assert "At least one field must be provided." in str(exc_info.value)


def test_device_profile_update_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        DeviceProfileUpdate(unknown_field="x")

    assert "Extra inputs are not permitted" in str(exc_info.value)
