from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_current_actor_id_dep, require_current_actor_id
from app.modules.safety.schemas import (
    CampaignSafetyCreate,
    CampaignSafetyDetail,
    CampaignSafetyUpdate,
)
from app.modules.safety.service import (
    create_campaign_safety,
    delete_campaign_safety,
    get_campaign_safety,
    update_campaign_safety,
)

router = APIRouter(tags=["safety"])


@router.get("/campaigns/{campaign_id}/safety", response_model=CampaignSafetyDetail)
def get_campaign_safety_route(campaign_id: str) -> CampaignSafetyDetail:
    return get_campaign_safety(campaign_id)


@router.post(
    "/campaigns/{campaign_id}/safety",
    response_model=CampaignSafetyDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_campaign_safety_route(
    campaign_id: str,
    payload: CampaignSafetyCreate,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> CampaignSafetyDetail:
    actor_id = require_current_actor_id(current_actor_id)
    return create_campaign_safety(campaign_id, payload, actor_id)


@router.patch("/campaigns/{campaign_id}/safety", response_model=CampaignSafetyDetail)
def update_campaign_safety_route(
    campaign_id: str,
    payload: CampaignSafetyUpdate,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> CampaignSafetyDetail:
    actor_id = require_current_actor_id(current_actor_id)
    return update_campaign_safety(campaign_id, payload, actor_id)


@router.delete("/campaigns/{campaign_id}/safety", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign_safety_route(campaign_id: str) -> Response:
    delete_campaign_safety(campaign_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
