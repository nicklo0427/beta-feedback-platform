from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CampaignSafetyRecord:
    id: str
    campaign_id: str
    distribution_channel: str
    source_label: str
    source_url: Optional[str]
    risk_level: str
    review_status: str
    official_channel_only: bool
    risk_note: Optional[str]
    created_at: str
    updated_at: str
