from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import get_current_actor_id_dep, require_current_actor_id
from app.modules.campaigns.schemas import (
    CampaignCreate,
    CampaignDetail,
    CampaignListResponse,
    CampaignUpdate,
)
from app.modules.campaigns.service import (
    create_campaign,
    delete_campaign,
    get_campaign,
    list_campaigns,
    update_campaign,
)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=CampaignListResponse, response_model_exclude_unset=True)
def list_campaigns_route(
    project_id: Optional[str] = Query(default=None),
    mine: bool = False,
    qualified_for_me: bool = False,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> CampaignListResponse:
    actor_id = (
        require_current_actor_id(current_actor_id)
        if mine or qualified_for_me
        else current_actor_id
    )
    return list_campaigns(
        project_id=project_id,
        mine=mine,
        qualified_for_me=qualified_for_me,
        current_actor_id=actor_id,
    )


@router.post("", response_model=CampaignDetail, status_code=status.HTTP_201_CREATED)
def create_campaign_route(
    payload: CampaignCreate,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> CampaignDetail:
    actor_id = require_current_actor_id(current_actor_id)
    return create_campaign(payload, actor_id)


@router.get("/{campaign_id}", response_model=CampaignDetail)
def get_campaign_route(campaign_id: str) -> CampaignDetail:
    return get_campaign(campaign_id)


@router.patch("/{campaign_id}", response_model=CampaignDetail)
def update_campaign_route(
    campaign_id: str,
    payload: CampaignUpdate,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> CampaignDetail:
    actor_id = require_current_actor_id(current_actor_id)
    return update_campaign(campaign_id, payload, actor_id)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign_route(campaign_id: str) -> Response:
    delete_campaign(campaign_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
