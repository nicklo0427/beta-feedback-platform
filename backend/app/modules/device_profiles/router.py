from __future__ import annotations

from fastapi import APIRouter, Response, status

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


@router.get("", response_model=DeviceProfileListResponse)
def list_device_profiles_route() -> DeviceProfileListResponse:
    return list_device_profiles()


@router.post("", response_model=DeviceProfileDetail, status_code=status.HTTP_201_CREATED)
def create_device_profile_route(payload: DeviceProfileCreate) -> DeviceProfileDetail:
    return create_device_profile(payload)


@router.get("/{device_profile_id}", response_model=DeviceProfileDetail)
def get_device_profile_route(device_profile_id: str) -> DeviceProfileDetail:
    return get_device_profile(device_profile_id)


@router.patch("/{device_profile_id}", response_model=DeviceProfileDetail)
def update_device_profile_route(
    device_profile_id: str,
    payload: DeviceProfileUpdate,
) -> DeviceProfileDetail:
    return update_device_profile(device_profile_id, payload)


@router.delete("/{device_profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device_profile_route(device_profile_id: str) -> Response:
    delete_device_profile(device_profile_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
