from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class FeedbackRecord:
    id: str
    task_id: str
    campaign_id: str
    device_profile_id: Optional[str]
    summary: str
    rating: Optional[int]
    severity: str
    category: str
    reproduction_steps: Optional[str]
    expected_result: Optional[str]
    actual_result: Optional[str]
    note: Optional[str]
    review_status: str
    developer_note: Optional[str]
    submitted_at: str
    resubmitted_at: Optional[str]
    updated_at: str
