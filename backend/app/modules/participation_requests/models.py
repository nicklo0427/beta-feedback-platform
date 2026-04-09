from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ParticipationRequestRecord:
    id: str
    campaign_id: str
    tester_account_id: str
    device_profile_id: str
    status: str
    note: Optional[str]
    decision_note: Optional[str]
    created_at: str
    updated_at: str
    decided_at: Optional[str]

