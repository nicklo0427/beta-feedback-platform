from __future__ import annotations

from typing import Annotated, Generator, Optional

from fastapi import Header
from sqlalchemy.orm import Session

from app.common.exceptions import AppError
from app.core.config import Settings, get_settings
from app.db.session import get_db_session


def get_settings_dep() -> Settings:
    return get_settings()


def get_db_session_dep() -> Generator[Session, None, None]:
    yield from get_db_session()


def get_current_actor_id_dep(
    x_actor_id: Annotated[Optional[str], Header(alias="X-Actor-Id")] = None,
) -> Optional[str]:
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
