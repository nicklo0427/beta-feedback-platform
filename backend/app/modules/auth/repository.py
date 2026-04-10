from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, select

from app.db.entities import ActorSessionEntity
from app.db.session import database_persistence_enabled, db_session_scope
from app.modules.auth.models import ActorSessionRecord

_SESSIONS: dict[str, ActorSessionRecord] = {}


def _to_record(entity: ActorSessionEntity) -> ActorSessionRecord:
    return ActorSessionRecord(
        id=entity.id,
        account_id=entity.account_id,
        created_at=entity.created_at,
        expires_at=entity.expires_at,
    )


def _to_entity(record: ActorSessionRecord) -> ActorSessionEntity:
    return ActorSessionEntity(
        id=record.id,
        account_id=record.account_id,
        created_at=record.created_at,
        expires_at=record.expires_at,
    )


def get_session(session_id: str) -> Optional[ActorSessionRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(ActorSessionEntity, session_id)
            return None if entity is None else _to_record(entity)

    return _SESSIONS.get(session_id)


def create_session(record: ActorSessionRecord) -> ActorSessionRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _SESSIONS[record.id] = record
    return record


def delete_session(session_id: str) -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(ActorSessionEntity, session_id)
            if entity is not None:
                session.delete(entity)
        return

    _SESSIONS.pop(session_id, None)


def delete_sessions_for_account(account_id: str) -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.execute(
                delete(ActorSessionEntity).where(ActorSessionEntity.account_id == account_id)
            )
        return

    expired_session_ids = [
        session_id
        for session_id, session in _SESSIONS.items()
        if session.account_id == account_id
    ]
    for session_id in expired_session_ids:
        delete_session(session_id)


def clear_sessions() -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.execute(delete(ActorSessionEntity))
        return

    _SESSIONS.clear()
