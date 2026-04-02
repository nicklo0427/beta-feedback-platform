from __future__ import annotations

from typing import Optional

from app.modules.projects.models import ProjectRecord

_PROJECTS: dict[str, ProjectRecord] = {}


def list_projects() -> list[ProjectRecord]:
    return list(_PROJECTS.values())


def get_project(project_id: str) -> Optional[ProjectRecord]:
    return _PROJECTS.get(project_id)


def exists_project(project_id: str) -> bool:
    return project_id in _PROJECTS


def create_project(record: ProjectRecord) -> ProjectRecord:
    _PROJECTS[record.id] = record
    return record


def update_project(record: ProjectRecord) -> ProjectRecord:
    _PROJECTS[record.id] = record
    return record


def delete_project(project_id: str) -> None:
    _PROJECTS.pop(project_id, None)


def clear_projects() -> None:
    _PROJECTS.clear()
