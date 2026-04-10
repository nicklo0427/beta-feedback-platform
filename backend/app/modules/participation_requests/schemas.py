from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.accounts.schemas import AccountCollaborationSummary, AccountDetail
from app.modules.campaigns.schemas import CampaignDetail
from app.modules.device_profiles.schemas import DeviceProfileDetail
from app.modules.eligibility.schemas import CampaignQualificationResultItem
from app.modules.reputation.schemas import (
    CampaignReputationSummary,
    DeviceProfileReputationSummary,
)
from app.modules.tasks.schemas import TaskStatus


class ParticipationRequestStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    WITHDRAWN = "withdrawn"


class ParticipationAssignmentStatus(str, Enum):
    NOT_ASSIGNED = "not_assigned"
    TASK_CREATED = "task_created"


class ParticipationRequestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    device_profile_id: str = Field(..., min_length=1)
    note: Optional[str] = None

    @field_validator("device_profile_id")
    @classmethod
    def validate_device_profile_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Device profile ID cannot be blank.")
        return normalized

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class ParticipationRequestUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["withdrawn", "accepted", "declined"]
    decision_note: Optional[str] = None

    @field_validator("decision_note")
    @classmethod
    def normalize_decision_note(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class ParticipationRequestTaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1)
    instruction_summary: Optional[str] = None
    status: TaskStatus = TaskStatus.ASSIGNED

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


class ParticipationRequestListItem(BaseModel):
    id: str
    campaign_id: str
    campaign_name: str
    tester_account_id: str
    device_profile_id: str
    device_profile_name: str
    status: ParticipationRequestStatus
    note: Optional[str] = None
    decision_note: Optional[str] = None
    created_at: str
    updated_at: str
    decided_at: Optional[str] = None
    linked_task_id: Optional[str] = None
    assignment_created_at: Optional[str] = None
    assignment_status: ParticipationAssignmentStatus


class ParticipationRequestDetail(BaseModel):
    id: str
    campaign_id: str
    campaign_name: str
    tester_account_id: str
    device_profile_id: str
    device_profile_name: str
    status: ParticipationRequestStatus
    note: Optional[str] = None
    decision_note: Optional[str] = None
    created_at: str
    updated_at: str
    decided_at: Optional[str] = None
    linked_task_id: Optional[str] = None
    assignment_created_at: Optional[str] = None
    assignment_status: ParticipationAssignmentStatus


class ParticipationRequestEnrichedDetail(ParticipationRequestDetail):
    tester_account: AccountDetail
    tester_account_summary: AccountCollaborationSummary
    device_profile: DeviceProfileDetail
    device_profile_reputation: DeviceProfileReputationSummary
    qualification_snapshot: CampaignQualificationResultItem
    campaign: CampaignDetail
    campaign_reputation: CampaignReputationSummary


class ParticipationRequestListResponse(BaseModel):
    items: list[ParticipationRequestListItem]
    total: int
