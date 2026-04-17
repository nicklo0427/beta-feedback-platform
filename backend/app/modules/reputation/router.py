from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends

from app.api.deps import get_current_actor_id_dep, require_current_actor_id

from app.modules.reputation.schemas import (
    CampaignReputationSummary,
    DeviceProfileReputationSummary,
)
from app.modules.reputation.service import (
    get_campaign_reputation,
    get_campaign_reputation_for_actor,
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
def get_campaign_reputation_route(
    campaign_id: str,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> CampaignReputationSummary:
    return get_campaign_reputation_for_actor(
        campaign_id,
        require_current_actor_id(current_actor_id),
    )
