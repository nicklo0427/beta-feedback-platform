from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ProjectRecord:
    id: str
    name: str
    description: Optional[str]
    created_at: str
    updated_at: str
