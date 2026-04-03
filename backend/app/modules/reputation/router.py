from __future__ import annotations

from fastapi import APIRouter

from app.modules.reputation.schemas import (
    CampaignReputationSummary,
    DeviceProfileReputationSummary,
)
from app.modules.reputation.service import (
    get_campaign_reputation,
    get_device_profile_reputation,
)

router = APIRouter(tags=["reputation"])


@router.get(
    "/device-profiles/{device_profile_id}/reputation",
    response_model=DeviceProfileReputationSummary,
)
def get_device_profile_reputation_route(
    device_profile_id: str,
) -> DeviceProfileReputationSummary:
    return get_device_profile_reputation(device_profile_id)


@router.get(
    "/campaigns/{campaign_id}/reputation",
    response_model=CampaignReputationSummary,
)
def get_campaign_reputation_route(campaign_id: str) -> CampaignReputationSummary:
    return get_campaign_reputation(campaign_id)
