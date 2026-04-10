from __future__ import annotations

from typing import Annotated, Generator, Optional

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from app.common.exceptions import AppError
from app.core.config import Settings, get_settings
from app.db.session import get_db_session


def get_settings_dep() -> Settings:
    return get_settings()


def get_db_session_dep() -> Generator[Session, None, None]:
    yield from get_db_session()


def get_current_actor_id_dep(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings_dep)],
    x_actor_id: Annotated[Optional[str], Header(alias="X-Actor-Id")] = None,
) -> Optional[str]:
    from app.modules.auth.service import resolve_session_actor_id

    session_id = request.cookies.get(settings.auth_session_cookie_name)
    if session_id is not None:
        session_actor_id = resolve_session_actor_id(session_id)
        if session_actor_id is not None:
            return session_actor_id

    if not settings.auth_dev_actor_header_fallback_enabled:
        return None

    if x_actor_id is None:
        return None

    normalized = x_actor_id.strip()
    return normalized or None


def require_current_actor_id(actor_id: Optional[str]) -> str:
    if actor_id is None:
        raise AppError(
            status_code=400,
            code="missing_actor_context",
            message="Current actor is required.",
            details={
                "header": "X-Actor-Id",
            },
        )

    return actor_id
