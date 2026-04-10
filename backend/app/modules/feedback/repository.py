from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, select

from app.db.entities import FeedbackEntity
from app.db.session import database_persistence_enabled, db_session_scope
from app.modules.feedback.models import FeedbackRecord

_FEEDBACK: dict[str, FeedbackRecord] = {}


def _to_record(entity: FeedbackEntity) -> FeedbackRecord:
    return FeedbackRecord(
        id=entity.id,
        task_id=entity.task_id,
        campaign_id=entity.campaign_id,
        device_profile_id=entity.device_profile_id,
        summary=entity.summary,
        rating=entity.rating,
        severity=entity.severity,
        category=entity.category,
        reproduction_steps=entity.reproduction_steps,
        expected_result=entity.expected_result,
        actual_result=entity.actual_result,
        note=entity.note,
        review_status=entity.review_status,
        developer_note=entity.developer_note,
        submitted_at=entity.submitted_at,
        resubmitted_at=entity.resubmitted_at,
        updated_at=entity.updated_at,
    )


def _to_entity(record: FeedbackRecord) -> FeedbackEntity:
    return FeedbackEntity(
        id=record.id,
        task_id=record.task_id,
        campaign_id=record.campaign_id,
        device_profile_id=record.device_profile_id,
        summary=record.summary,
        rating=record.rating,
        severity=record.severity,
        category=record.category,
        reproduction_steps=record.reproduction_steps,
        expected_result=record.expected_result,
        actual_result=record.actual_result,
        note=record.note,
        review_status=record.review_status,
        developer_note=record.developer_note,
        submitted_at=record.submitted_at,
        resubmitted_at=record.resubmitted_at,
        updated_at=record.updated_at,
    )


def list_feedback(*, task_id: Optional[str] = None) -> list[FeedbackRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            statement = select(FeedbackEntity)
            if task_id is not None:
                statement = statement.where(FeedbackEntity.task_id == task_id)
            items = session.scalars(
                statement.order_by(FeedbackEntity.submitted_at.asc(), FeedbackEntity.id.asc())
            ).all()
            return [_to_record(item) for item in items]

    items = list(_FEEDBACK.values())
    if task_id is not None:
        items = [item for item in items if item.task_id == task_id]
    return items


def get_feedback(feedback_id: str) -> Optional[FeedbackRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(FeedbackEntity, feedback_id)
            return None if entity is None else _to_record(entity)

    return _FEEDBACK.get(feedback_id)


def create_feedback(record: FeedbackRecord) -> FeedbackRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _FEEDBACK[record.id] = record
    return record


def update_feedback(record: FeedbackRecord) -> FeedbackRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _FEEDBACK[record.id] = record
    return record


def delete_feedback(feedback_id: str) -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(FeedbackEntity, feedback_id)
            if entity is not None:
                session.delete(entity)
        return

    _FEEDBACK.pop(feedback_id, None)


def has_feedback_for_task(task_id: str) -> bool:
    if database_persistence_enabled():
        with db_session_scope() as session:
            return (
                session.scalar(
                    select(FeedbackEntity.id).where(FeedbackEntity.task_id == task_id).limit(1)
                )
                is not None
            )

    return any(record.task_id == task_id for record in _FEEDBACK.values())


def clear_feedback() -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.execute(delete(FeedbackEntity))
        return

    _FEEDBACK.clear()
