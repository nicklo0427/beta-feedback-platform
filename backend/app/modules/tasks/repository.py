from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, select

from app.db.entities import TaskEntity
from app.db.session import database_persistence_enabled, db_session_scope
from app.modules.tasks.models import TaskRecord

_TASKS: dict[str, TaskRecord] = {}


def _to_record(entity: TaskEntity) -> TaskRecord:
    return TaskRecord(
        id=entity.id,
        campaign_id=entity.campaign_id,
        device_profile_id=entity.device_profile_id,
        title=entity.title,
        instruction_summary=entity.instruction_summary,
        status=entity.status,
        submitted_at=entity.submitted_at,
        resolution_outcome=entity.resolution_outcome,
        resolution_note=entity.resolution_note,
        resolved_at=entity.resolved_at,
        resolved_by_account_id=entity.resolved_by_account_id,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def _to_entity(record: TaskRecord) -> TaskEntity:
    return TaskEntity(
        id=record.id,
        campaign_id=record.campaign_id,
        device_profile_id=record.device_profile_id,
        title=record.title,
        instruction_summary=record.instruction_summary,
        status=record.status,
        submitted_at=record.submitted_at,
        resolution_outcome=record.resolution_outcome,
        resolution_note=record.resolution_note,
        resolved_at=record.resolved_at,
        resolved_by_account_id=record.resolved_by_account_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def list_tasks(
    *,
    campaign_id: Optional[str] = None,
    device_profile_id: Optional[str] = None,
    status: Optional[str] = None,
) -> list[TaskRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            statement = select(TaskEntity)
            if campaign_id is not None:
                statement = statement.where(TaskEntity.campaign_id == campaign_id)
            if device_profile_id is not None:
                statement = statement.where(TaskEntity.device_profile_id == device_profile_id)
            if status is not None:
                statement = statement.where(TaskEntity.status == status)
            items = session.scalars(
                statement.order_by(TaskEntity.created_at.asc(), TaskEntity.id.asc())
            ).all()
            return [_to_record(item) for item in items]

    items = list(_TASKS.values())

    if campaign_id is not None:
        items = [item for item in items if item.campaign_id == campaign_id]

    if device_profile_id is not None:
        items = [item for item in items if item.device_profile_id == device_profile_id]

    if status is not None:
        items = [item for item in items if item.status == status]

    return items


def get_task(task_id: str) -> Optional[TaskRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(TaskEntity, task_id)
            return None if entity is None else _to_record(entity)

    return _TASKS.get(task_id)


def create_task(record: TaskRecord) -> TaskRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _TASKS[record.id] = record
    return record


def update_task(record: TaskRecord) -> TaskRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _TASKS[record.id] = record
    return record


def delete_task(task_id: str) -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(TaskEntity, task_id)
            if entity is not None:
                session.delete(entity)
        return

    _TASKS.pop(task_id, None)


def has_tasks_for_campaign(campaign_id: str) -> bool:
    if database_persistence_enabled():
        with db_session_scope() as session:
            return (
                session.scalar(
                    select(TaskEntity.id).where(TaskEntity.campaign_id == campaign_id).limit(1)
                )
                is not None
            )

    return any(record.campaign_id == campaign_id for record in _TASKS.values())


def has_tasks_for_device_profile(device_profile_id: str) -> bool:
    if database_persistence_enabled():
        with db_session_scope() as session:
            return (
                session.scalar(
                    select(TaskEntity.id)
                    .where(TaskEntity.device_profile_id == device_profile_id)
                    .limit(1)
                )
                is not None
            )

    return any(record.device_profile_id == device_profile_id for record in _TASKS.values())


def clear_tasks() -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.execute(delete(TaskEntity))
        return

    _TASKS.clear()
