from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class FeedbackSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackCategory(str, Enum):
    BUG = "bug"
    USABILITY = "usability"
    PERFORMANCE = "performance"
    COMPATIBILITY = "compatibility"
    OTHER = "other"


class FeedbackCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(..., min_length=1)
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    severity: FeedbackSeverity
    category: FeedbackCategory
    reproduction_steps: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    note: Optional[str] = None

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Feedback summary cannot be blank.")
        return normalized

    @field_validator("reproduction_steps", "expected_result", "actual_result", "note")
    @classmethod
    def normalize_optional_fields(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class FeedbackUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: Optional[str] = None
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    severity: Optional[FeedbackSeverity] = None
    category: Optional[FeedbackCategory] = None
    reproduction_steps: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    note: Optional[str] = None

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        if not normalized:
            raise ValueError("Feedback summary cannot be blank.")
        return normalized

    @field_validator("reproduction_steps", "expected_result", "actual_result", "note")
    @classmethod
    def normalize_optional_fields(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_not_empty(self) -> "FeedbackUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class FeedbackListItem(BaseModel):
    id: str
    task_id: str
    summary: str
    severity: FeedbackSeverity
    category: FeedbackCategory
    submitted_at: str


class FeedbackDetail(BaseModel):
    id: str
    task_id: str
    campaign_id: str
    device_profile_id: Optional[str] = None
    summary: str
    rating: Optional[int] = None
    severity: FeedbackSeverity
    category: FeedbackCategory
    reproduction_steps: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    note: Optional[str] = None
    submitted_at: str
    updated_at: str


class FeedbackListResponse(BaseModel):
    items: list[FeedbackListItem]
    total: int
