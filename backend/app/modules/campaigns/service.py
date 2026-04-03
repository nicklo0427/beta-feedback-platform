from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import status

from app.common.exceptions import AppError
from app.common.responses import build_list_response
from app.modules.campaigns import repository
from app.modules.campaigns.models import CampaignRecord
from app.modules.campaigns.schemas import (
    CampaignCreate,
    CampaignDetail,
    CampaignListItem,
    CampaignListResponse,
    CampaignStatus,
    CampaignUpdate,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _generate_campaign_id() -> str:
    return f"camp_{uuid4().hex[:12]}"


def _to_campaign_detail(record: CampaignRecord) -> CampaignDetail:
    return CampaignDetail.model_validate(asdict(record))


def _to_campaign_list_item(record: CampaignRecord) -> CampaignListItem:
    return CampaignListItem.model_validate(asdict(record))


def _ensure_campaign_exists(campaign_id: str) -> CampaignRecord:
    record = repository.get_campaign(campaign_id)
    if record is None:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="resource_not_found",
            message="Campaign not found.",
            details={
                "resource": "campaign",
                "id": campaign_id,
            },
        )

    return record


def ensure_campaign_exists(campaign_id: str) -> CampaignRecord:
    return _ensure_campaign_exists(campaign_id)


def has_campaigns_for_project(project_id: str) -> bool:
    return repository.has_campaigns_for_project(project_id)


def list_campaigns(project_id: Optional[str] = None) -> CampaignListResponse:
    items = [
        _to_campaign_list_item(record)
        for record in repository.list_campaigns(project_id=project_id)
    ]
    return CampaignListResponse.model_validate(build_list_response(items))


def get_campaign(campaign_id: str) -> CampaignDetail:
    return _to_campaign_detail(_ensure_campaign_exists(campaign_id))


def create_campaign(payload: CampaignCreate) -> CampaignDetail:
    from app.modules.projects.service import ensure_project_exists

    ensure_project_exists(payload.project_id)

    timestamp = _utc_now_iso()
    record = CampaignRecord(
        id=_generate_campaign_id(),
        project_id=payload.project_id,
        name=payload.name,
        description=payload.description,
        target_platforms=[platform.value for platform in payload.target_platforms],
        version_label=payload.version_label,
        status=CampaignStatus.DRAFT.value,
        created_at=timestamp,
        updated_at=timestamp,
    )
    repository.create_campaign(record)
    return _to_campaign_detail(record)


def update_campaign(campaign_id: str, payload: CampaignUpdate) -> CampaignDetail:
    current = _ensure_campaign_exists(campaign_id)
    updated = replace(
        current,
        name=payload.name if payload.name is not None else current.name,
        description=(
            payload.description if payload.description is not None else current.description
        ),
        target_platforms=(
            [platform.value for platform in payload.target_platforms]
            if payload.target_platforms is not None
            else current.target_platforms
        ),
        version_label=(
            payload.version_label
            if payload.version_label is not None
            else current.version_label
        ),
        status=payload.status.value if payload.status is not None else current.status,
        updated_at=_utc_now_iso(),
    )
    repository.update_campaign(updated)
    return _to_campaign_detail(updated)


def delete_campaign(campaign_id: str) -> None:
    _ensure_campaign_exists(campaign_id)

    from app.modules.eligibility.service import has_eligibility_rules_for_campaign
    from app.modules.safety.service import has_safety_for_campaign
    from app.modules.tasks.service import has_tasks_for_campaign

    if has_eligibility_rules_for_campaign(campaign_id):
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="conflict",
            message="Campaign cannot be deleted while eligibility rules exist.",
            details={
                "resource": "campaign",
                "id": campaign_id,
                "related_resource": "eligibility_rule",
            },
        )

    if has_safety_for_campaign(campaign_id):
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="conflict",
            message="Campaign cannot be deleted while safety exists.",
            details={
                "resource": "campaign",
                "id": campaign_id,
                "related_resource": "campaign_safety",
            },
        )

    if has_tasks_for_campaign(campaign_id):
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="conflict",
            message="Campaign cannot be deleted while tasks exist.",
            details={
                "resource": "campaign",
                "id": campaign_id,
                "related_resource": "task",
            },
        )

    repository.delete_campaign(campaign_id)
