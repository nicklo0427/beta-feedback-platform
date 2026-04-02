from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query, Response, status

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


@router.get("", response_model=CampaignListResponse)
def list_campaigns_route(
    project_id: Optional[str] = Query(default=None),
) -> CampaignListResponse:
    return list_campaigns(project_id=project_id)


@router.post("", response_model=CampaignDetail, status_code=status.HTTP_201_CREATED)
def create_campaign_route(payload: CampaignCreate) -> CampaignDetail:
    return create_campaign(payload)


@router.get("/{campaign_id}", response_model=CampaignDetail)
def get_campaign_route(campaign_id: str) -> CampaignDetail:
    return get_campaign(campaign_id)


@router.patch("/{campaign_id}", response_model=CampaignDetail)
def update_campaign_route(
    campaign_id: str,
    payload: CampaignUpdate,
) -> CampaignDetail:
    return update_campaign(campaign_id, payload)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign_route(campaign_id: str) -> Response:
    delete_campaign(campaign_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
