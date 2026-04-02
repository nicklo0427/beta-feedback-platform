from __future__ import annotations

from fastapi import APIRouter, Response, status

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


@router.get("", response_model=ProjectListResponse)
def list_projects_route() -> ProjectListResponse:
    return list_projects()


@router.post("", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
def create_project_route(payload: ProjectCreate) -> ProjectDetail:
    return create_project(payload)


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project_route(project_id: str) -> ProjectDetail:
    return get_project(project_id)


@router.patch("/{project_id}", response_model=ProjectDetail)
def update_project_route(project_id: str, payload: ProjectUpdate) -> ProjectDetail:
    return update_project(project_id, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_route(project_id: str) -> Response:
    delete_project(project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
