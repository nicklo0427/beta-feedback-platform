from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import status

from app.common.exceptions import AppError
from app.common.responses import build_list_response
from app.modules.accounts.schemas import AccountRole
from app.modules.accounts.service import ensure_account_exists
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


def _ensure_developer_actor(current_actor_id: str | None):
    if current_actor_id is None:
        return None

    actor = ensure_account_exists(current_actor_id)
    if actor.role != AccountRole.DEVELOPER.value:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="forbidden_actor_role",
            message="Developer role is required for this operation.",
            details={
                "actor_id": actor.id,
                "actor_role": actor.role,
                "required_role": AccountRole.DEVELOPER.value,
            },
        )

    return actor


def _raise_ownership_mismatch(
    actor_id: str,
    resource: str,
    ownership_anchor: dict[str, str | None],
) -> None:
    raise AppError(
        status_code=status.HTTP_409_CONFLICT,
        code="ownership_mismatch",
        message="Current actor does not own the target resource.",
        details={
            "actor_id": actor_id,
            "resource": resource,
            "ownership_anchor": ownership_anchor,
        },
    )


def ensure_project_owned_by_actor(project_id: str, current_actor_id: str | None, resource: str):
    from app.modules.projects.service import ensure_project_exists

    actor = _ensure_developer_actor(current_actor_id)
    project = ensure_project_exists(project_id)

    if actor is not None and project.owner_account_id != actor.id:
        _raise_ownership_mismatch(
            actor.id,
            resource,
            {
                "resource": "project",
                "id": project.id,
                "owner_account_id": project.owner_account_id,
            },
        )

    return project


def ensure_campaign_owned_by_actor(
    campaign_id: str,
    current_actor_id: str | None,
    resource: str = "campaign",
) -> CampaignRecord:
    from app.modules.projects.service import ensure_project_exists

    actor = _ensure_developer_actor(current_actor_id)
    campaign = _ensure_campaign_exists(campaign_id)

    if actor is None:
        return campaign

    project = ensure_project_exists(campaign.project_id)
    if project.owner_account_id != actor.id:
        _raise_ownership_mismatch(
            actor.id,
            resource,
            {
                "resource": "project",
                "id": project.id,
                "owner_account_id": project.owner_account_id,
            },
        )

    return campaign


def ensure_campaign_exists(campaign_id: str) -> CampaignRecord:
    return _ensure_campaign_exists(campaign_id)


def has_campaigns_for_project(project_id: str) -> bool:
    return repository.has_campaigns_for_project(project_id)


def _resolve_owned_project_ids_for_actor(current_actor_id: str) -> set[str]:
    from app.modules.projects import repository as projects_repository

    actor = ensure_account_exists(current_actor_id)
    if actor.role != AccountRole.DEVELOPER.value:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="forbidden_actor_role",
            message="Developer role is required to access owned campaigns.",
            details={
                "actor_id": actor.id,
                "actor_role": actor.role,
                "required_role": AccountRole.DEVELOPER.value,
            },
        )

    return {
        record.id
        for record in projects_repository.list_projects()
        if record.owner_account_id == current_actor_id
    }


def list_campaigns(
    project_id: Optional[str] = None,
    *,
    mine: bool = False,
    current_actor_id: str | None = None,
) -> CampaignListResponse:
    records = repository.list_campaigns(project_id=project_id)

    if mine:
        if current_actor_id is None:
            raise AppError(
                status_code=status.HTTP_400_BAD_REQUEST,
                code="missing_actor_context",
                message="Current actor is required.",
                details={
                    "header": "X-Actor-Id",
                },
            )

        owned_project_ids = _resolve_owned_project_ids_for_actor(current_actor_id)
        records = [
            record for record in records if record.project_id in owned_project_ids
        ]

    items = [
        _to_campaign_list_item(record)
        for record in records
    ]
    return CampaignListResponse.model_validate(build_list_response(items))


def get_campaign(campaign_id: str) -> CampaignDetail:
    return _to_campaign_detail(_ensure_campaign_exists(campaign_id))


def create_campaign(
    payload: CampaignCreate,
    current_actor_id: str | None = None,
) -> CampaignDetail:
    ensure_project_owned_by_actor(
        payload.project_id,
        current_actor_id,
        resource="campaign",
    )

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


def update_campaign(
    campaign_id: str,
    payload: CampaignUpdate,
    current_actor_id: str | None = None,
) -> CampaignDetail:
    current = ensure_campaign_owned_by_actor(
        campaign_id,
        current_actor_id,
        resource="campaign",
    )
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
