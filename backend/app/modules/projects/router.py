from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_current_actor_id_dep, require_current_actor_id
from app.modules.accounts.service import ensure_account_exists
from app.modules.projects.schemas import (
    ProjectCreate,
    ProjectDetail,
    ProjectListResponse,
    ProjectUpdate,
)
from app.modules.projects.service import (
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse, response_model_exclude_none=True)
def list_projects_route(
    mine: bool = False,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> ProjectListResponse:
    if not mine:
        return list_projects()

    actor_id = require_current_actor_id(current_actor_id)
    ensure_account_exists(actor_id)
    return list_projects(owner_account_id=actor_id)


@router.post(
    "",
    response_model=ProjectDetail,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
def create_project_route(
    payload: ProjectCreate,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> ProjectDetail:
    return create_project(payload, current_actor_id)


@router.get(
    "/{project_id}",
    response_model=ProjectDetail,
    response_model_exclude_none=True,
)
def get_project_route(project_id: str) -> ProjectDetail:
    return get_project(project_id)


@router.patch(
    "/{project_id}",
    response_model=ProjectDetail,
    response_model_exclude_none=True,
)
def update_project_route(project_id: str, payload: ProjectUpdate) -> ProjectDetail:
    return update_project(project_id, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_route(project_id: str) -> Response:
    delete_project(project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
