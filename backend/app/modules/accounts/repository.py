from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, select

from app.db.entities import AccountEntity
from app.db.session import database_persistence_enabled, db_session_scope
from app.modules.accounts.models import AccountRecord

_ACCOUNTS: dict[str, AccountRecord] = {}


def _normalize_record_roles(role: str, roles: list[str] | None) -> list[str]:
    return list(roles) if roles else [role]


def _to_record(entity: AccountEntity) -> AccountRecord:
    return AccountRecord(
        id=entity.id,
        display_name=entity.display_name,
        role=entity.role,
        roles=_normalize_record_roles(entity.role, entity.roles),
        bio=entity.bio,
        locale=entity.locale,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        email=entity.email,
        password_hash=entity.password_hash,
        is_active=entity.is_active,
    )


def _to_entity(record: AccountRecord) -> AccountEntity:
    return AccountEntity(
        id=record.id,
        display_name=record.display_name,
        role=record.role,
        roles=_normalize_record_roles(record.role, record.roles),
        bio=record.bio,
        locale=record.locale,
        created_at=record.created_at,
        updated_at=record.updated_at,
        email=record.email,
        password_hash=record.password_hash,
        is_active=record.is_active,
    )


def list_accounts() -> list[AccountRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            items = session.scalars(
                select(AccountEntity).order_by(AccountEntity.created_at.asc(), AccountEntity.id.asc())
            ).all()
            return [_to_record(item) for item in items]

    return list(_ACCOUNTS.values())


def get_account(account_id: str) -> Optional[AccountRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(AccountEntity, account_id)
            return None if entity is None else _to_record(entity)

    return _ACCOUNTS.get(account_id)


def get_account_by_email(email: str) -> Optional[AccountRecord]:
    normalized_email = email.strip().lower()
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.scalar(
                select(AccountEntity).where(AccountEntity.email == normalized_email)
            )
            return None if entity is None else _to_record(entity)

    return next(
        (
            record
            for record in _ACCOUNTS.values()
            if record.email is not None and record.email == normalized_email
        ),
        None,
    )


def create_account(record: AccountRecord) -> AccountRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _ACCOUNTS[record.id] = record
    return record


def update_account(record: AccountRecord) -> AccountRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _ACCOUNTS[record.id] = record
    return record


def delete_account(account_id: str) -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(AccountEntity, account_id)
            if entity is not None:
                session.delete(entity)
        return

    _ACCOUNTS.pop(account_id, None)


def clear_accounts() -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.execute(delete(AccountEntity))
        return

    _ACCOUNTS.clear()
