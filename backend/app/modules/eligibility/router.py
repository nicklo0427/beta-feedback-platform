from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Response, status
from fastapi import Query

from app.api.deps import get_current_actor_id_dep, require_current_actor_id
from app.modules.eligibility.schemas import (
    CampaignQualificationResultItem,
    CampaignQualificationResultListResponse,
    EligibilityRuleCreate,
    EligibilityRuleDetail,
    EligibilityRuleListResponse,
    EligibilityRuleUpdate,
)
from app.modules.eligibility.service import (
    create_eligibility_rule,
    delete_eligibility_rule,
    get_eligibility_rule,
    get_campaign_qualification_check,
    list_campaign_qualification_results,
    list_eligibility_rules,
    update_eligibility_rule,
)

router = APIRouter(tags=["eligibility"])


@router.get(
    "/campaigns/{campaign_id}/eligibility-rules",
    response_model=EligibilityRuleListResponse,
)
def list_eligibility_rules_route(campaign_id: str) -> EligibilityRuleListResponse:
    return list_eligibility_rules(campaign_id)


@router.get(
    "/campaigns/{campaign_id}/qualification-results",
    response_model=CampaignQualificationResultListResponse,
)
def list_campaign_qualification_results_route(
    campaign_id: str,
    mine: bool = True,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> CampaignQualificationResultListResponse:
    _ = mine
    actor_id = require_current_actor_id(current_actor_id)
    return list_campaign_qualification_results(campaign_id, actor_id)


@router.get(
    "/campaigns/{campaign_id}/qualification-check",
    response_model=CampaignQualificationResultItem,
)
def get_campaign_qualification_check_route(
    campaign_id: str,
    device_profile_id: str = Query(...),
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> CampaignQualificationResultItem:
    actor_id = require_current_actor_id(current_actor_id)
    return get_campaign_qualification_check(
        campaign_id,
        device_profile_id,
        actor_id,
    )


@router.post(
    "/campaigns/{campaign_id}/eligibility-rules",
    response_model=EligibilityRuleDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_eligibility_rule_route(
    campaign_id: str,
    payload: EligibilityRuleCreate,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> EligibilityRuleDetail:
    actor_id = require_current_actor_id(current_actor_id)
    return create_eligibility_rule(campaign_id, payload, actor_id)


@router.get("/eligibility-rules/{eligibility_rule_id}", response_model=EligibilityRuleDetail)
def get_eligibility_rule_route(eligibility_rule_id: str) -> EligibilityRuleDetail:
    return get_eligibility_rule(eligibility_rule_id)


@router.patch(
    "/eligibility-rules/{eligibility_rule_id}",
    response_model=EligibilityRuleDetail,
)
def update_eligibility_rule_route(
    eligibility_rule_id: str,
    payload: EligibilityRuleUpdate,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> EligibilityRuleDetail:
    actor_id = require_current_actor_id(current_actor_id)
    return update_eligibility_rule(eligibility_rule_id, payload, actor_id)


@router.delete("/eligibility-rules/{eligibility_rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_eligibility_rule_route(eligibility_rule_id: str) -> Response:
    delete_eligibility_rule(eligibility_rule_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
