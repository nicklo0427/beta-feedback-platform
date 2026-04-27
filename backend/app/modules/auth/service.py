from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import status

from app.common.exceptions import AppError
from app.core.config import get_settings
from app.modules.accounts import repository as accounts_repository
from app.modules.accounts.schemas import AccountCreate
from app.modules.accounts.service import create_account_with_auth, ensure_account_exists
from app.modules.auth import repository
from app.modules.auth.models import ActorSessionRecord
from app.modules.auth.schemas import (
    AuthLoginRequest,
    AuthRegisterRequest,
    AuthSessionResponse,
    AuthenticatedActor,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _utc_now_iso() -> str:
    return _utc_now().isoformat().replace("+00:00", "Z")


def _to_iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _generate_session_id() -> str:
    return f"sess_{secrets.token_hex(16)}"


def _hash_password(password: str, *, salt: str | None = None) -> str:
    normalized_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        normalized_salt.encode("utf-8"),
        100_000,
    ).hex()
    return f"pbkdf2_sha256${normalized_salt}${digest}"


def _verify_password(password: str, password_hash: str | None) -> bool:
    if password_hash is None:
        return False

    try:
        _, salt, stored_digest = password_hash.split("$", 2)
    except ValueError:
        return False

    recalculated = _hash_password(password, salt=salt)
    return hmac.compare_digest(recalculated, password_hash)


def _raise_invalid_credentials() -> None:
    raise AppError(
        status_code=status.HTTP_401_UNAUTHORIZED,
        code="invalid_credentials",
        message="Email or password is incorrect.",
        details=None,
    )


def _raise_unauthenticated() -> None:
    raise AppError(
        status_code=status.HTTP_401_UNAUTHORIZED,
        code="unauthenticated",
        message="Authentication is required.",
        details=None,
    )


def _raise_session_expired() -> None:
    raise AppError(
        status_code=status.HTTP_401_UNAUTHORIZED,
        code="session_expired",
        message="Your session has expired. Please sign in again.",
        details=None,
    )


def _to_authenticated_actor(account_id: str) -> AuthenticatedActor:
    account = ensure_account_exists(account_id)
    if account.email is None:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="account_auth_not_configured",
            message="Account does not have sign-in credentials configured.",
            details={
                "account_id": account.id,
            },
        )

    return AuthenticatedActor(
        id=account.id,
        display_name=account.display_name,
        role=account.role,
        roles=account.roles,
        email=account.email,
        is_active=account.is_active,
    )


def _build_session_response(session_record: ActorSessionRecord) -> AuthSessionResponse:
    return AuthSessionResponse(
        account=_to_authenticated_actor(session_record.account_id),
        expires_at=session_record.expires_at,
    )


def _create_actor_session(account_id: str) -> tuple[ActorSessionRecord, AuthSessionResponse]:
    settings = get_settings()
    created_at = _utc_now()
    expires_at = created_at + timedelta(hours=settings.auth_session_duration_hours)
    session_record = ActorSessionRecord(
        id=_generate_session_id(),
        account_id=account_id,
        created_at=_to_iso(created_at),
        expires_at=_to_iso(expires_at),
    )
    repository.create_session(session_record)
    return session_record, _build_session_response(session_record)


def register(payload: AuthRegisterRequest) -> tuple[str, AuthSessionResponse]:
    existing_account = accounts_repository.get_account_by_email(payload.email)
    if existing_account is not None:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="duplicate_email",
            message="This email is already registered.",
            details={
                "email": payload.email,
            },
        )

    account = create_account_with_auth(
        AccountCreate(
            display_name=payload.display_name,
            role=payload.role,
            roles=payload.roles,
            bio=payload.bio,
            locale=payload.locale,
        ),
        email=payload.email,
        password_hash=_hash_password(payload.password),
        is_active=True,
    )
    session_record, session_response = _create_actor_session(account.id)
    return session_record.id, session_response


def login(payload: AuthLoginRequest) -> tuple[str, AuthSessionResponse]:
    account = accounts_repository.get_account_by_email(payload.email)
    if account is None or not _verify_password(payload.password, account.password_hash):
        _raise_invalid_credentials()

    if not account.is_active:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="account_inactive",
            message="This account is inactive.",
            details={
                "account_id": account.id,
            },
        )

    repository.delete_sessions_for_account(account.id)
    session_record, session_response = _create_actor_session(account.id)
    return session_record.id, session_response


def logout(session_id: str | None) -> None:
    if session_id is None:
        return

    repository.delete_session(session_id)


def get_current_session(session_id: str | None) -> AuthSessionResponse:
    if session_id is None:
        _raise_unauthenticated()

    session_record = repository.get_session(session_id)
    if session_record is None:
        _raise_unauthenticated()

    expires_at = datetime.fromisoformat(session_record.expires_at.replace("Z", "+00:00"))
    if expires_at <= _utc_now():
        repository.delete_session(session_record.id)
        _raise_session_expired()

    return _build_session_response(session_record)


def resolve_session_actor_id(session_id: str | None) -> str | None:
    if session_id is None:
        return None

    session_record = repository.get_session(session_id)
    if session_record is None:
        _raise_unauthenticated()

    expires_at = datetime.fromisoformat(session_record.expires_at.replace("Z", "+00:00"))
    if expires_at <= _utc_now():
        repository.delete_session(session_record.id)
        _raise_session_expired()

    return session_record.account_id
