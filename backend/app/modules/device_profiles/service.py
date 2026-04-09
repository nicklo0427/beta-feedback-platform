from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import status

from app.common.exceptions import AppError
from app.common.responses import build_list_response
from app.modules.accounts.schemas import AccountRole
from app.modules.accounts.service import ensure_account_exists
from app.modules.device_profiles import repository
from app.modules.device_profiles.models import DeviceProfileRecord
from app.modules.device_profiles.schemas import (
    DeviceProfileCreate,
    DeviceProfileDetail,
    DeviceProfileListItem,
    DeviceProfileListResponse,
    DeviceProfileUpdate,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _generate_device_profile_id() -> str:
    return f"dp_{uuid4().hex[:12]}"


def _to_device_profile_detail(record: DeviceProfileRecord) -> DeviceProfileDetail:
    return DeviceProfileDetail.model_validate(asdict(record))


def _to_device_profile_list_item(record: DeviceProfileRecord) -> DeviceProfileListItem:
    return DeviceProfileListItem.model_validate(asdict(record))


def ensure_device_profile_exists(device_profile_id: str) -> DeviceProfileRecord:
    record = repository.get_device_profile(device_profile_id)
    if record is None:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="resource_not_found",
            message="Device profile not found.",
            details={
                "resource": "device_profile",
                "id": device_profile_id,
            },
        )

    return record


def _resolve_device_profile_owner_account_id(current_actor_id: str | None) -> str | None:
    if current_actor_id is None:
        return None

    actor = ensure_account_exists(current_actor_id)
    if actor.role != AccountRole.TESTER.value:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="conflict",
            message="Tester account is required to own a device profile.",
            details={
                "resource": "device_profile",
                "account_id": actor.id,
                "expected_role": AccountRole.TESTER.value,
                "actual_role": actor.role,
            },
        )

    return actor.id


def list_device_profiles(
    owner_account_id: str | None = None,
) -> DeviceProfileListResponse:
    items = [
        _to_device_profile_list_item(record)
        for record in repository.list_device_profiles()
        if owner_account_id is None or record.owner_account_id == owner_account_id
    ]
    return DeviceProfileListResponse.model_validate(build_list_response(items))


def get_device_profile(device_profile_id: str) -> DeviceProfileDetail:
    return _to_device_profile_detail(ensure_device_profile_exists(device_profile_id))


def create_device_profile(
    payload: DeviceProfileCreate,
    current_actor_id: str | None = None,
) -> DeviceProfileDetail:
    timestamp = _utc_now_iso()
    record = DeviceProfileRecord(
        id=_generate_device_profile_id(),
        name=payload.name,
        platform=payload.platform.value,
        device_model=payload.device_model,
        os_name=payload.os_name,
        install_channel=payload.install_channel,
        os_version=payload.os_version,
        browser_name=payload.browser_name,
        browser_version=payload.browser_version,
        locale=payload.locale,
        notes=payload.notes,
        owner_account_id=_resolve_device_profile_owner_account_id(current_actor_id),
        created_at=timestamp,
        updated_at=timestamp,
    )
    repository.create_device_profile(record)
    return _to_device_profile_detail(record)


def update_device_profile(
    device_profile_id: str,
    payload: DeviceProfileUpdate,
) -> DeviceProfileDetail:
    current = ensure_device_profile_exists(device_profile_id)
    updated = replace(
        current,
        name=payload.name if payload.name is not None else current.name,
        platform=payload.platform.value if payload.platform is not None else current.platform,
        device_model=(
            payload.device_model
            if payload.device_model is not None
            else current.device_model
        ),
        os_name=payload.os_name if payload.os_name is not None else current.os_name,
        install_channel=(
            payload.install_channel
            if payload.install_channel is not None
            else current.install_channel
        ),
        os_version=payload.os_version if payload.os_version is not None else current.os_version,
        browser_name=(
            payload.browser_name
            if payload.browser_name is not None
            else current.browser_name
        ),
        browser_version=(
            payload.browser_version
            if payload.browser_version is not None
            else current.browser_version
        ),
        locale=payload.locale if payload.locale is not None else current.locale,
        notes=payload.notes if payload.notes is not None else current.notes,
        updated_at=_utc_now_iso(),
    )
    repository.update_device_profile(updated)
    return _to_device_profile_detail(updated)


def delete_device_profile(device_profile_id: str) -> None:
    ensure_device_profile_exists(device_profile_id)

    from app.modules.tasks.service import has_tasks_for_device_profile

    if has_tasks_for_device_profile(device_profile_id):
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="conflict",
            message="Device profile cannot be deleted while tasks exist.",
            details={
                "resource": "device_profile",
                "id": device_profile_id,
                "related_resource": "task",
            },
        )

    repository.delete_device_profile(device_profile_id)
