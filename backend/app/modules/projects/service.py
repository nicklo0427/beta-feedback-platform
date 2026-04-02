from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import status

from app.common.exceptions import AppError
from app.common.responses import build_list_response
from app.modules.projects import repository
from app.modules.projects.models import ProjectRecord
from app.modules.projects.schemas import (
    ProjectCreate,
    ProjectDetail,
    ProjectListItem,
    ProjectListResponse,
    ProjectUpdate,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _generate_project_id() -> str:
    return f"proj_{uuid4().hex[:12]}"


def _to_project_detail(record: ProjectRecord) -> ProjectDetail:
    return ProjectDetail.model_validate(asdict(record))


def _to_project_list_item(record: ProjectRecord) -> ProjectListItem:
    return ProjectListItem.model_validate(asdict(record))


def ensure_project_exists(project_id: str) -> ProjectRecord:
    record = repository.get_project(project_id)
    if record is None:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="resource_not_found",
            message="Project not found.",
            details={
                "resource": "project",
                "id": project_id,
            },
        )

    return record


def list_projects() -> ProjectListResponse:
    items = [_to_project_list_item(record) for record in repository.list_projects()]
    return ProjectListResponse.model_validate(build_list_response(items))


def get_project(project_id: str) -> ProjectDetail:
    return _to_project_detail(ensure_project_exists(project_id))


def create_project(payload: ProjectCreate) -> ProjectDetail:
    timestamp = _utc_now_iso()
    record = ProjectRecord(
        id=_generate_project_id(),
        name=payload.name,
        description=payload.description,
        created_at=timestamp,
        updated_at=timestamp,
    )
    repository.create_project(record)
    return _to_project_detail(record)


def update_project(project_id: str, payload: ProjectUpdate) -> ProjectDetail:
    current = ensure_project_exists(project_id)
    updated = replace(
        current,
        name=payload.name if payload.name is not None else current.name,
        description=(
            payload.description if payload.description is not None else current.description
        ),
        updated_at=_utc_now_iso(),
    )
    repository.update_project(updated)
    return _to_project_detail(updated)


def delete_project(project_id: str) -> None:
    ensure_project_exists(project_id)

    from app.modules.campaigns.service import has_campaigns_for_project

    if has_campaigns_for_project(project_id):
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="conflict",
            message="Project cannot be deleted while campaigns exist.",
            details={
                "resource": "project",
                "id": project_id,
                "related_resource": "campaign",
            },
        )

    repository.delete_project(project_id)
