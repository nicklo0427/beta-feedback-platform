from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, select

from app.db.entities import DeviceProfileEntity
from app.db.session import database_persistence_enabled, db_session_scope
from app.modules.device_profiles.models import DeviceProfileRecord

_DEVICE_PROFILES: dict[str, DeviceProfileRecord] = {}


def _to_record(entity: DeviceProfileEntity) -> DeviceProfileRecord:
    return DeviceProfileRecord(
        id=entity.id,
        name=entity.name,
        platform=entity.platform,
        device_model=entity.device_model,
        os_name=entity.os_name,
        install_channel=entity.install_channel,
        os_version=entity.os_version,
        browser_name=entity.browser_name,
        browser_version=entity.browser_version,
        locale=entity.locale,
        notes=entity.notes,
        owner_account_id=entity.owner_account_id,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def _to_entity(record: DeviceProfileRecord) -> DeviceProfileEntity:
    return DeviceProfileEntity(
        id=record.id,
        name=record.name,
        platform=record.platform,
        device_model=record.device_model,
        os_name=record.os_name,
        install_channel=record.install_channel,
        os_version=record.os_version,
        browser_name=record.browser_name,
        browser_version=record.browser_version,
        locale=record.locale,
        notes=record.notes,
        owner_account_id=record.owner_account_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def list_device_profiles() -> list[DeviceProfileRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            items = session.scalars(
                select(DeviceProfileEntity).order_by(
                    DeviceProfileEntity.created_at.asc(),
                    DeviceProfileEntity.id.asc(),
                )
            ).all()
            return [_to_record(item) for item in items]

    return list(_DEVICE_PROFILES.values())


def get_device_profile(device_profile_id: str) -> Optional[DeviceProfileRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(DeviceProfileEntity, device_profile_id)
            return None if entity is None else _to_record(entity)

    return _DEVICE_PROFILES.get(device_profile_id)


def create_device_profile(record: DeviceProfileRecord) -> DeviceProfileRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _DEVICE_PROFILES[record.id] = record
    return record


def update_device_profile(record: DeviceProfileRecord) -> DeviceProfileRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _DEVICE_PROFILES[record.id] = record
    return record


def delete_device_profile(device_profile_id: str) -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(DeviceProfileEntity, device_profile_id)
            if entity is not None:
                session.delete(entity)
        return

    _DEVICE_PROFILES.pop(device_profile_id, None)


def clear_device_profiles() -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.execute(delete(DeviceProfileEntity))
        return

    _DEVICE_PROFILES.clear()
