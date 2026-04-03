from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class DistributionChannel(str, Enum):
    WEB_URL = "web_url"
    PWA_URL = "pwa_url"
    TESTFLIGHT = "testflight"
    GOOGLE_PLAY_TESTING = "google_play_testing"
    MANUAL_INVITE = "manual_invite"
    OTHER = "other"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CampaignSafetyCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    distribution_channel: DistributionChannel
    source_label: str
    source_url: Optional[str] = None
    risk_level: RiskLevel
    review_status: ReviewStatus = ReviewStatus.PENDING
    official_channel_only: bool = False
    risk_note: Optional[str] = None

    @field_validator("source_label")
    @classmethod
    def validate_source_label(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Source label cannot be blank.")
        return normalized

    @field_validator("source_url", "risk_note")
    @classmethod
    def normalize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class CampaignSafetyUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    distribution_channel: Optional[DistributionChannel] = None
    source_label: Optional[str] = None
    source_url: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    review_status: Optional[ReviewStatus] = None
    official_channel_only: Optional[bool] = None
    risk_note: Optional[str] = None

    @field_validator("source_label")
    @classmethod
    def validate_source_label(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        if not normalized:
            raise ValueError("Source label cannot be blank.")
        return normalized

    @field_validator("source_url", "risk_note")
    @classmethod
    def normalize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_not_empty(self) -> "CampaignSafetyUpdate":
        if (
            self.distribution_channel is None
            and self.source_label is None
            and self.source_url is None
            and self.risk_level is None
            and self.review_status is None
            and self.official_channel_only is None
            and self.risk_note is None
        ):
            raise ValueError("At least one field must be provided.")
        return self


class CampaignSafetyDetail(BaseModel):
    id: str
    campaign_id: str
    distribution_channel: DistributionChannel
    source_label: str
    source_url: Optional[str] = None
    risk_level: RiskLevel
    review_status: ReviewStatus
    official_channel_only: bool
    risk_note: Optional[str] = None
    created_at: str
    updated_at: str
