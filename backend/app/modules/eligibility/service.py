from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import status

from app.common.exceptions import AppError
from app.common.responses import build_list_response
from app.modules.eligibility import repository
from app.modules.eligibility.models import EligibilityRuleRecord
from app.modules.eligibility.schemas import (
    EligibilityRuleCreate,
    EligibilityRuleDetail,
    EligibilityRuleListItem,
    EligibilityRuleListResponse,
    EligibilityRuleUpdate,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _generate_eligibility_rule_id() -> str:
    return f"er_{uuid4().hex[:12]}"


def _to_eligibility_rule_detail(record: EligibilityRuleRecord) -> EligibilityRuleDetail:
    return EligibilityRuleDetail.model_validate(asdict(record))


def _to_eligibility_rule_list_item(record: EligibilityRuleRecord) -> EligibilityRuleListItem:
    return EligibilityRuleListItem.model_validate(asdict(record))


def ensure_eligibility_rule_exists(eligibility_rule_id: str) -> EligibilityRuleRecord:
    record = repository.get_eligibility_rule(eligibility_rule_id)
    if record is None:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="resource_not_found",
            message="Eligibility rule not found.",
            details={
                "resource": "eligibility_rule",
                "id": eligibility_rule_id,
            },
        )

    return record


def has_eligibility_rules_for_campaign(campaign_id: str) -> bool:
    return repository.has_eligibility_rules_for_campaign(campaign_id)


def list_eligibility_rules(campaign_id: str) -> EligibilityRuleListResponse:
    from app.modules.campaigns.service import ensure_campaign_exists

    ensure_campaign_exists(campaign_id)

    items = [
        _to_eligibility_rule_list_item(record)
        for record in repository.list_eligibility_rules(campaign_id=campaign_id)
    ]
    return EligibilityRuleListResponse.model_validate(build_list_response(items))


def get_eligibility_rule(eligibility_rule_id: str) -> EligibilityRuleDetail:
    return _to_eligibility_rule_detail(ensure_eligibility_rule_exists(eligibility_rule_id))


def create_eligibility_rule(
    campaign_id: str,
    payload: EligibilityRuleCreate,
    current_actor_id: str | None = None,
) -> EligibilityRuleDetail:
    from app.modules.campaigns.service import ensure_campaign_owned_by_actor

    ensure_campaign_owned_by_actor(
        campaign_id,
        current_actor_id,
        resource="eligibility_rule",
    )

    timestamp = _utc_now_iso()
    record = EligibilityRuleRecord(
        id=_generate_eligibility_rule_id(),
        campaign_id=campaign_id,
        platform=payload.platform.value,
        os_name=payload.os_name,
        os_version_min=payload.os_version_min,
        os_version_max=payload.os_version_max,
        install_channel=payload.install_channel,
        is_active=payload.is_active,
        created_at=timestamp,
        updated_at=timestamp,
    )
    repository.create_eligibility_rule(record)
    return _to_eligibility_rule_detail(record)


def update_eligibility_rule(
    eligibility_rule_id: str,
    payload: EligibilityRuleUpdate,
    current_actor_id: str | None = None,
) -> EligibilityRuleDetail:
    current = ensure_eligibility_rule_exists(eligibility_rule_id)
    from app.modules.campaigns.service import ensure_campaign_owned_by_actor

    ensure_campaign_owned_by_actor(
        current.campaign_id,
        current_actor_id,
        resource="eligibility_rule",
    )

    updated = replace(
        current,
        platform=payload.platform.value if payload.platform is not None else current.platform,
        os_name=payload.os_name if payload.os_name is not None else current.os_name,
        os_version_min=(
            payload.os_version_min
            if payload.os_version_min is not None
            else current.os_version_min
        ),
        os_version_max=(
            payload.os_version_max
            if payload.os_version_max is not None
            else current.os_version_max
        ),
        install_channel=(
            payload.install_channel
            if payload.install_channel is not None
            else current.install_channel
        ),
        is_active=payload.is_active if payload.is_active is not None else current.is_active,
        updated_at=_utc_now_iso(),
    )
    repository.update_eligibility_rule(updated)
    return _to_eligibility_rule_detail(updated)


def delete_eligibility_rule(eligibility_rule_id: str) -> None:
    ensure_eligibility_rule_exists(eligibility_rule_id)
    repository.delete_eligibility_rule(eligibility_rule_id)
