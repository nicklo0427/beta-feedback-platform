from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActivityEventRecord:
    id: str
    entity_type: str
    entity_id: str
    event_type: str
    actor_account_id: str
    summary: str
    created_at: str
