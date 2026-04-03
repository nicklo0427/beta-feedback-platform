from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class EligibilityRulePlatform(str, Enum):
    WEB = "web"
    MOBILE_WEB = "h5"
    PWA = "pwa"
    IOS = "ios"
    ANDROID = "android"


class EligibilityRuleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: EligibilityRulePlatform
    os_name: Optional[str] = None
    os_version_min: Optional[str] = None
    os_version_max: Optional[str] = None
    install_channel: Optional[str] = None
    is_active: bool = True

    @field_validator("os_name", "os_version_min", "os_version_max", "install_channel")
    @classmethod
    def normalize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class EligibilityRuleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: Optional[EligibilityRulePlatform] = None
    os_name: Optional[str] = None
    os_version_min: Optional[str] = None
    os_version_max: Optional[str] = None
    install_channel: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("os_name", "os_version_min", "os_version_max", "install_channel")
    @classmethod
    def normalize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_not_empty(self) -> "EligibilityRuleUpdate":
        if (
            self.platform is None
            and self.os_name is None
            and self.os_version_min is None
            and self.os_version_max is None
            and self.install_channel is None
            and self.is_active is None
        ):
            raise ValueError("At least one field must be provided.")
        return self


class EligibilityRuleListItem(BaseModel):
    id: str
    campaign_id: str
    platform: EligibilityRulePlatform
    os_name: Optional[str] = None
    install_channel: Optional[str] = None
    is_active: bool
    updated_at: str


class EligibilityRuleDetail(BaseModel):
    id: str
    campaign_id: str
    platform: EligibilityRulePlatform
    os_name: Optional[str] = None
    os_version_min: Optional[str] = None
    os_version_max: Optional[str] = None
    install_channel: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str


class EligibilityRuleListResponse(BaseModel):
    items: list[EligibilityRuleListItem]
    total: int
