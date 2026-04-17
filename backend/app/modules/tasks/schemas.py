from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TaskStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    CLOSED = "closed"


class TaskResolutionOutcome(str, Enum):
    CONFIRMED_ISSUE = "confirmed_issue"
    NEEDS_FOLLOW_UP = "needs_follow_up"
    NOT_REPRODUCIBLE = "not_reproducible"
    CANCELLED = "cancelled"


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1)
    instruction_summary: Optional[str] = None
    device_profile_id: Optional[str] = None
    status: Optional[TaskStatus] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Task title cannot be blank.")
        return normalized

    @field_validator("instruction_summary")
    @classmethod
    def normalize_instruction_summary(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    @field_validator("device_profile_id")
    @classmethod
    def validate_device_profile_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        if not normalized:
            raise ValueError("Device profile ID cannot be blank.")
        return normalized


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    instruction_summary: Optional[str] = None
    device_profile_id: Optional[str] = None
    status: Optional[TaskStatus] = None
    resolution_outcome: Optional[TaskResolutionOutcome] = None
    resolution_note: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        if not normalized:
            raise ValueError("Task title cannot be blank.")
        return normalized

    @field_validator("instruction_summary")
    @classmethod
    def normalize_instruction_summary(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    @field_validator("device_profile_id")
    @classmethod
    def validate_device_profile_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        if not normalized:
            raise ValueError("Device profile ID cannot be blank.")
        return normalized

    @field_validator("resolution_note")
    @classmethod
    def normalize_resolution_note(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_not_empty(self) -> "TaskUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class TaskQualificationContext(BaseModel):
    device_profile_id: str
    device_profile_name: str
    qualification_status: Literal["qualified", "not_qualified"]
    matched_rule_id: Optional[str] = None
    reason_summary: Optional[str] = None
    qualification_drift: bool


class TaskParticipationRequestContext(BaseModel):
    request_id: str
    request_status: Literal["pending", "accepted", "declined", "withdrawn"]
    tester_account_id: str
    tester_account_display_name: str
    assignment_created_at: Optional[str] = None


class TaskResolutionContext(BaseModel):
    resolution_outcome: TaskResolutionOutcome
    resolution_note: Optional[str] = None
    resolved_at: str
    resolved_by_account_id: str
    resolved_by_account_display_name: str


class TaskListItem(BaseModel):
    id: str
    campaign_id: str
    device_profile_id: Optional[str] = None
    title: str
    status: TaskStatus
    updated_at: str
    qualification_context: Optional[TaskQualificationContext] = None
    resolution_context: Optional[TaskResolutionContext] = None


class TaskDetail(BaseModel):
    id: str
    campaign_id: str
    device_profile_id: Optional[str] = None
    title: str
    instruction_summary: Optional[str] = None
    status: TaskStatus
    submitted_at: Optional[str] = None
    created_at: str
    updated_at: str
    qualification_context: Optional[TaskQualificationContext] = None
    participation_request_context: Optional[TaskParticipationRequestContext] = None
    resolution_context: Optional[TaskResolutionContext] = None


class TaskListResponse(BaseModel):
    items: list[TaskListItem]
    total: int
