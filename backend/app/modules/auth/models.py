from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActorSessionRecord:
    id: str
    account_id: str
    created_at: str
    expires_at: str
