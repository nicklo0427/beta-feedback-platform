from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AccountRecord:
    id: str
    display_name: str
    role: str
    bio: Optional[str]
    locale: Optional[str]
    created_at: str
    updated_at: str
