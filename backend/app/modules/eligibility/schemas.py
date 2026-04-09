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


class QualificationStatus(str, Enum):
    QUALIFIED = "qualified"
    NOT_QUALIFIED = "not_qualified"


class QualificationReasonCode(str, Enum):
    PLATFORM_MISMATCH = "platform_mismatch"
    OS_NAME_MISMATCH = "os_name_mismatch"
    OS_VERSION_BELOW_MIN = "os_version_below_min"
    OS_VERSION_ABOVE_MAX = "os_version_above_max"
    OS_VERSION_UNCOMPARABLE = "os_version_uncomparable"
    INSTALL_CHANNEL_MISMATCH = "install_channel_mismatch"


class CampaignQualificationResultItem(BaseModel):
    device_profile_id: str
    device_profile_name: str
    qualification_status: QualificationStatus
    matched_rule_id: Optional[str] = None
    reason_codes: list[QualificationReasonCode]
    reason_summary: Optional[str] = None


class CampaignQualificationResultListResponse(BaseModel):
    items: list[CampaignQualificationResultItem]
    total: int
