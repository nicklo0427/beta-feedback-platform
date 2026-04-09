from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TargetPlatform(str, Enum):
    WEB = "web"
    MOBILE_WEB = "h5"
    PWA = "pwa"
    IOS = "ios"
    ANDROID = "android"


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class CampaignQualifyingDeviceProfileRef(BaseModel):
    id: str
    name: str


class CampaignCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    target_platforms: list[TargetPlatform] = Field(..., min_length=1)
    version_label: Optional[str] = None

    @field_validator("project_id", "name")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank.")
        return normalized

    @field_validator("description", "version_label")
    @classmethod
    def normalize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    @field_validator("target_platforms")
    @classmethod
    def deduplicate_platforms(
        cls,
        value: list[TargetPlatform],
    ) -> list[TargetPlatform]:
        unique_platforms: list[TargetPlatform] = []
        seen: set[TargetPlatform] = set()

        for platform in value:
            if platform not in seen:
                unique_platforms.append(platform)
                seen.add(platform)

        return unique_platforms


class CampaignUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = None
    description: Optional[str] = None
    target_platforms: Optional[list[TargetPlatform]] = Field(default=None, min_length=1)
    version_label: Optional[str] = None
    status: Optional[CampaignStatus] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        if not normalized:
            raise ValueError("Campaign name cannot be blank.")
        return normalized

    @field_validator("description", "version_label")
    @classmethod
    def normalize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    @field_validator("target_platforms")
    @classmethod
    def deduplicate_platforms(
        cls,
        value: Optional[list[TargetPlatform]],
    ) -> Optional[list[TargetPlatform]]:
        if value is None:
            return None

        unique_platforms: list[TargetPlatform] = []
        seen: set[TargetPlatform] = set()

        for platform in value:
            if platform not in seen:
                unique_platforms.append(platform)
                seen.add(platform)

        return unique_platforms

    @model_validator(mode="after")
    def validate_not_empty(self) -> "CampaignUpdate":
        if (
            self.name is None
            and self.description is None
            and self.target_platforms is None
            and self.version_label is None
            and self.status is None
        ):
            raise ValueError("At least one field must be provided.")
        return self


class CampaignListItem(BaseModel):
    id: str
    project_id: str
    name: str
    target_platforms: list[TargetPlatform]
    version_label: Optional[str] = None
    status: CampaignStatus
    updated_at: str
    qualifying_device_profiles: Optional[list[CampaignQualifyingDeviceProfileRef]] = None
    qualification_summary: Optional[str] = None


class CampaignDetail(BaseModel):
    id: str
    project_id: str
    name: str
    description: Optional[str] = None
    target_platforms: list[TargetPlatform]
    version_label: Optional[str] = None
    status: CampaignStatus
    created_at: str
    updated_at: str


class CampaignListResponse(BaseModel):
    items: list[CampaignListItem]
    total: int
