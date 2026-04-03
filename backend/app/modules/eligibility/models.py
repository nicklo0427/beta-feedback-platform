from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EligibilityRuleRecord:
    id: str
    campaign_id: str
    platform: str
    os_name: Optional[str]
    os_version_min: Optional[str]
    os_version_max: Optional[str]
    install_channel: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str
