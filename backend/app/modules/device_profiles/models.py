from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DeviceProfileRecord:
    id: str
    name: str
    platform: str
    device_model: str
    os_name: str
    os_version: Optional[str]
    browser_name: Optional[str]
    browser_version: Optional[str]
    locale: Optional[str]
    notes: Optional[str]
    owner_account_id: Optional[str]
    created_at: str
    updated_at: str
