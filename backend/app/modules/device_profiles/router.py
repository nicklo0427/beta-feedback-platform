from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_current_actor_id_dep, require_current_actor_id
from app.modules.accounts.service import ensure_account_exists
from app.modules.device_profiles.schemas import (
    DeviceProfileCreate,
    DeviceProfileDetail,
    DeviceProfileListResponse,
    DeviceProfileUpdate,
)
from app.modules.device_profiles.service import (
    create_device_profile,
    delete_device_profile,
    get_device_profile,
    list_device_profiles,
    update_device_profile,
)

router = APIRouter(prefix="/device-profiles", tags=["device_profiles"])


@router.get(
    "",
    response_model=DeviceProfileListResponse,
    response_model_exclude_none=True,
)
def list_device_profiles_route(
    mine: bool = False,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> DeviceProfileListResponse:
    if not mine:
        return list_device_profiles()

    actor_id = require_current_actor_id(current_actor_id)
    ensure_account_exists(actor_id)
    return list_device_profiles(owner_account_id=actor_id)


@router.post(
    "",
    response_model=DeviceProfileDetail,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
def create_device_profile_route(
    payload: DeviceProfileCreate,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> DeviceProfileDetail:
    return create_device_profile(payload, current_actor_id)


@router.get(
    "/{device_profile_id}",
    response_model=DeviceProfileDetail,
    response_model_exclude_none=True,
)
def get_device_profile_route(device_profile_id: str) -> DeviceProfileDetail:
    return get_device_profile(device_profile_id)


@router.patch(
    "/{device_profile_id}",
    response_model=DeviceProfileDetail,
    response_model_exclude_none=True,
)
def update_device_profile_route(
    device_profile_id: str,
    payload: DeviceProfileUpdate,
) -> DeviceProfileDetail:
    return update_device_profile(device_profile_id, payload)


@router.delete("/{device_profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device_profile_route(device_profile_id: str) -> Response:
    delete_device_profile(device_profile_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
