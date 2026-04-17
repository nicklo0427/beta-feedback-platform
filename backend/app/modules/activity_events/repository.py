from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, select

from app.db.entities import ActivityEventEntity
from app.db.session import database_persistence_enabled, db_session_scope
from app.modules.activity_events.models import ActivityEventRecord

_ACTIVITY_EVENTS: dict[str, ActivityEventRecord] = {}


def _to_record(entity: ActivityEventEntity) -> ActivityEventRecord:
    return ActivityEventRecord(
        id=entity.id,
        entity_type=entity.entity_type,
        entity_id=entity.entity_id,
        event_type=entity.event_type,
        actor_account_id=entity.actor_account_id,
        summary=entity.summary,
        created_at=entity.created_at,
    )


def _to_entity(record: ActivityEventRecord) -> ActivityEventEntity:
    return ActivityEventEntity(
        id=record.id,
        entity_type=record.entity_type,
        entity_id=record.entity_id,
        event_type=record.event_type,
        actor_account_id=record.actor_account_id,
        summary=record.summary,
        created_at=record.created_at,
    )


def list_activity_events(
    *,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
) -> list[ActivityEventRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            statement = select(ActivityEventEntity)
            if entity_type is not None:
                statement = statement.where(ActivityEventEntity.entity_type == entity_type)
            if entity_id is not None:
                statement = statement.where(ActivityEventEntity.entity_id == entity_id)
            items = session.scalars(
                statement.order_by(
                    ActivityEventEntity.created_at.desc(),
                    ActivityEventEntity.id.desc(),
                )
            ).all()
            return [_to_record(item) for item in items]

    items = list(_ACTIVITY_EVENTS.values())
    if entity_type is not None:
        items = [item for item in items if item.entity_type == entity_type]
    if entity_id is not None:
        items = [item for item in items if item.entity_id == entity_id]
    return sorted(
        items,
        key=lambda item: (item.created_at, item.id),
        reverse=True,
    )


def create_activity_event(record: ActivityEventRecord) -> ActivityEventRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _ACTIVITY_EVENTS[record.id] = record
    return record


def clear_activity_events() -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.execute(delete(ActivityEventEntity))
        return

    _ACTIVITY_EVENTS.clear()
