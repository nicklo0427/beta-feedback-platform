from __future__ import annotations

from typing import Generator

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db_session


def get_settings_dep() -> Settings:
    return get_settings()


def get_db_session_dep() -> Generator[Session, None, None]:
    yield from get_db_session()
