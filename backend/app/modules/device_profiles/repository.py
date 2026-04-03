from __future__ import annotations

from typing import Optional

from app.modules.device_profiles.models import DeviceProfileRecord

_DEVICE_PROFILES: dict[str, DeviceProfileRecord] = {}


def list_device_profiles() -> list[DeviceProfileRecord]:
    return list(_DEVICE_PROFILES.values())


def get_device_profile(device_profile_id: str) -> Optional[DeviceProfileRecord]:
    return _DEVICE_PROFILES.get(device_profile_id)


def create_device_profile(record: DeviceProfileRecord) -> DeviceProfileRecord:
    _DEVICE_PROFILES[record.id] = record
    return record


def update_device_profile(record: DeviceProfileRecord) -> DeviceProfileRecord:
    _DEVICE_PROFILES[record.id] = record
    return record


def delete_device_profile(device_profile_id: str) -> None:
    _DEVICE_PROFILES.pop(device_profile_id, None)


def clear_device_profiles() -> None:
    _DEVICE_PROFILES.clear()
