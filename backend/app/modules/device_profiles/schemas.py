from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class DeviceProfilePlatform(str, Enum):
    WEB = "web"
    MOBILE_WEB = "h5"
    PWA = "pwa"
    IOS = "ios"
    ANDROID = "android"


class DeviceProfileCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    platform: DeviceProfilePlatform
    device_model: str = Field(..., min_length=1)
    os_name: str = Field(..., min_length=1)
    os_version: Optional[str] = None
    browser_name: Optional[str] = None
    browser_version: Optional[str] = None
    locale: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("name", "device_model", "os_name")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank.")
        return normalized

    @field_validator("os_version", "browser_name", "browser_version", "locale", "notes")
    @classmethod
    def normalize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class DeviceProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = None
    platform: Optional[DeviceProfilePlatform] = None
    device_model: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    browser_name: Optional[str] = None
    browser_version: Optional[str] = None
    locale: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("name", "device_model", "os_name")
    @classmethod
    def validate_required_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank.")
        return normalized

    @field_validator("os_version", "browser_name", "browser_version", "locale", "notes")
    @classmethod
    def normalize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_not_empty(self) -> "DeviceProfileUpdate":
        if (
            self.name is None
            and self.platform is None
            and self.device_model is None
            and self.os_name is None
            and self.os_version is None
            and self.browser_name is None
            and self.browser_version is None
            and self.locale is None
            and self.notes is None
        ):
            raise ValueError("At least one field must be provided.")
        return self


class DeviceProfileListItem(BaseModel):
    id: str
    name: str
    platform: DeviceProfilePlatform
    device_model: str
    os_name: str
    owner_account_id: Optional[str] = None
    updated_at: str


class DeviceProfileDetail(BaseModel):
    id: str
    name: str
    platform: DeviceProfilePlatform
    device_model: str
    os_name: str
    os_version: Optional[str] = None
    browser_name: Optional[str] = None
    browser_version: Optional[str] = None
    locale: Optional[str] = None
    notes: Optional[str] = None
    owner_account_id: Optional[str] = None
    created_at: str
    updated_at: str


class DeviceProfileListResponse(BaseModel):
    items: list[DeviceProfileListItem]
    total: int
