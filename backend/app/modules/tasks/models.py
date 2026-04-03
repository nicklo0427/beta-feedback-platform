from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TaskRecord:
    id: str
    campaign_id: str
    device_profile_id: Optional[str]
    title: str
    instruction_summary: Optional[str]
    status: str
    submitted_at: Optional[str]
    created_at: str
    updated_at: str
