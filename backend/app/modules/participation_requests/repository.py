from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, select

from app.db.entities import ParticipationRequestEntity
from app.db.session import database_persistence_enabled, db_session_scope
from app.modules.participation_requests.models import ParticipationRequestRecord

_PARTICIPATION_REQUESTS: dict[str, ParticipationRequestRecord] = {}


def _to_record(entity: ParticipationRequestEntity) -> ParticipationRequestRecord:
    return ParticipationRequestRecord(
        id=entity.id,
        campaign_id=entity.campaign_id,
        tester_account_id=entity.tester_account_id,
        device_profile_id=entity.device_profile_id,
        status=entity.status,
        note=entity.note,
        decision_note=entity.decision_note,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        decided_at=entity.decided_at,
        linked_task_id=entity.linked_task_id,
        assignment_created_at=entity.assignment_created_at,
    )


def _to_entity(record: ParticipationRequestRecord) -> ParticipationRequestEntity:
    return ParticipationRequestEntity(
        id=record.id,
        campaign_id=record.campaign_id,
        tester_account_id=record.tester_account_id,
        device_profile_id=record.device_profile_id,
        status=record.status,
        note=record.note,
        decision_note=record.decision_note,
        created_at=record.created_at,
        updated_at=record.updated_at,
        decided_at=record.decided_at,
        linked_task_id=record.linked_task_id,
        assignment_created_at=record.assignment_created_at,
    )


def list_participation_requests() -> list[ParticipationRequestRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            items = session.scalars(
                select(ParticipationRequestEntity).order_by(
                    ParticipationRequestEntity.created_at.asc(),
                    ParticipationRequestEntity.id.asc(),
                )
            ).all()
            return [_to_record(item) for item in items]

    return list(_PARTICIPATION_REQUESTS.values())


def get_participation_request(
    request_id: str,
) -> Optional[ParticipationRequestRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(ParticipationRequestEntity, request_id)
            return None if entity is None else _to_record(entity)

    return _PARTICIPATION_REQUESTS.get(request_id)


def create_participation_request(
    record: ParticipationRequestRecord,
) -> ParticipationRequestRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _PARTICIPATION_REQUESTS[record.id] = record
    return record


def update_participation_request(
    record: ParticipationRequestRecord,
) -> ParticipationRequestRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _PARTICIPATION_REQUESTS[record.id] = record
    return record


def clear_participation_requests() -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.execute(delete(ParticipationRequestEntity))
        return

    _PARTICIPATION_REQUESTS.clear()
