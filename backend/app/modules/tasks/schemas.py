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


class TaskListItem(BaseModel):
    id: str
    campaign_id: str
    device_profile_id: Optional[str] = None
    title: str
    status: TaskStatus
    updated_at: str
    qualification_context: Optional[TaskQualificationContext] = None


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


class TaskListResponse(BaseModel):
    items: list[TaskListItem]
    total: int
