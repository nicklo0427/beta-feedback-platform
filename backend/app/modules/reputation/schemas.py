from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class DeviceProfileReputationSummary(BaseModel):
    device_profile_id: str
    tasks_assigned_count: int
    tasks_submitted_count: int
    feedback_submitted_count: int
    submission_rate: float
    last_feedback_at: Optional[str] = None
    updated_at: str


class CampaignReputationSummary(BaseModel):
    campaign_id: str
    tasks_total_count: int
    tasks_closed_count: int
    feedback_received_count: int
    closure_rate: float
    last_feedback_at: Optional[str] = None
    updated_at: str
