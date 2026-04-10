from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, select

from app.db.entities import ProjectEntity
from app.db.session import database_persistence_enabled, db_session_scope
from app.modules.projects.models import ProjectRecord

_PROJECTS: dict[str, ProjectRecord] = {}


def _to_record(entity: ProjectEntity) -> ProjectRecord:
    return ProjectRecord(
        id=entity.id,
        name=entity.name,
        description=entity.description,
        owner_account_id=entity.owner_account_id,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def _to_entity(record: ProjectRecord) -> ProjectEntity:
    return ProjectEntity(
        id=record.id,
        name=record.name,
        description=record.description,
        owner_account_id=record.owner_account_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def list_projects() -> list[ProjectRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            items = session.scalars(
                select(ProjectEntity).order_by(ProjectEntity.created_at.asc(), ProjectEntity.id.asc())
            ).all()
            return [_to_record(item) for item in items]

    return list(_PROJECTS.values())


def get_project(project_id: str) -> Optional[ProjectRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(ProjectEntity, project_id)
            return None if entity is None else _to_record(entity)

    return _PROJECTS.get(project_id)


def exists_project(project_id: str) -> bool:
    if database_persistence_enabled():
        with db_session_scope() as session:
            return session.get(ProjectEntity, project_id) is not None

    return project_id in _PROJECTS


def create_project(record: ProjectRecord) -> ProjectRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _PROJECTS[record.id] = record
    return record


def update_project(record: ProjectRecord) -> ProjectRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _PROJECTS[record.id] = record
    return record


def delete_project(project_id: str) -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(ProjectEntity, project_id)
            if entity is not None:
                session.delete(entity)
        return

    _PROJECTS.pop(project_id, None)


def clear_projects() -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.execute(delete(ProjectEntity))
        return

    _PROJECTS.clear()
