from __future__ import annotations

from fastapi import APIRouter, Response, status

from app.modules.eligibility.schemas import (
    EligibilityRuleCreate,
    EligibilityRuleDetail,
    EligibilityRuleListResponse,
    EligibilityRuleUpdate,
)
from app.modules.eligibility.service import (
    create_eligibility_rule,
    delete_eligibility_rule,
    get_eligibility_rule,
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


@router.post(
    "/campaigns/{campaign_id}/eligibility-rules",
    response_model=EligibilityRuleDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_eligibility_rule_route(
    campaign_id: str,
    payload: EligibilityRuleCreate,
) -> EligibilityRuleDetail:
    return create_eligibility_rule(campaign_id, payload)


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
) -> EligibilityRuleDetail:
    return update_eligibility_rule(eligibility_rule_id, payload)


@router.delete("/eligibility-rules/{eligibility_rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_eligibility_rule_route(eligibility_rule_id: str) -> Response:
    delete_eligibility_rule(eligibility_rule_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
