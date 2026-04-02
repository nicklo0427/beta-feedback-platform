from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CampaignRecord:
    id: str
    project_id: str
    name: str
    description: Optional[str]
    target_platforms: list[str]
    version_label: Optional[str]
    status: str
    created_at: str
    updated_at: str
