from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AccountRole(str, Enum):
    DEVELOPER = "developer"
    TESTER = "tester"


class AccountCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str = Field(..., min_length=1)
    role: AccountRole
    bio: Optional[str] = None
    locale: Optional[str] = None

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Display name cannot be blank.")
        return normalized

    @field_validator("bio", "locale")
    @classmethod
    def normalize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class AccountUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: Optional[str] = None
    role: Optional[AccountRole] = None
    bio: Optional[str] = None
    locale: Optional[str] = None

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        if not normalized:
            raise ValueError("Display name cannot be blank.")
        return normalized

    @field_validator("bio", "locale")
    @classmethod
    def normalize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_not_empty(self) -> "AccountUpdate":
        if (
            self.display_name is None
            and self.role is None
            and self.bio is None
            and self.locale is None
        ):
            raise ValueError("At least one field must be provided.")
        return self


class AccountListItem(BaseModel):
    id: str
    display_name: str
    role: AccountRole
    updated_at: str


class AccountDetail(BaseModel):
    id: str
    display_name: str
    role: AccountRole
    bio: Optional[str] = None
    locale: Optional[str] = None
    created_at: str
    updated_at: str


class AccountListResponse(BaseModel):
    items: list[AccountListItem]
    total: int


class AccountRecentProject(BaseModel):
    id: str
    name: str
    updated_at: str


class AccountRecentCampaign(BaseModel):
    id: str
    project_id: str
    name: str
    status: str
    updated_at: str


class AccountRecentDeviceProfile(BaseModel):
    id: str
    name: str
    platform: str
    updated_at: str


class AccountRecentTask(BaseModel):
    id: str
    campaign_id: str
    title: str
    status: str
    updated_at: str


class AccountRecentFeedback(BaseModel):
    id: str
    task_id: str
    summary: str
    review_status: str
    submitted_at: str


class DeveloperAccountSummary(BaseModel):
    owned_projects_count: int
    owned_campaigns_count: int
    feedback_to_review_count: int
    recent_projects: list[AccountRecentProject]
    recent_campaigns: list[AccountRecentCampaign]


class TesterAccountSummary(BaseModel):
    owned_device_profiles_count: int
    assigned_tasks_count: int
    submitted_feedback_count: int
    recent_device_profiles: list[AccountRecentDeviceProfile]
    recent_tasks: list[AccountRecentTask]
    recent_feedback: list[AccountRecentFeedback]


class AccountCollaborationSummary(BaseModel):
    account_id: str
    role: AccountRole
    developer_summary: Optional[DeveloperAccountSummary] = None
    tester_summary: Optional[TesterAccountSummary] = None
    updated_at: str
