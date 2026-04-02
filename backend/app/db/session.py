from __future__ import annotations

from functools import lru_cache
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine() -> Optional[Engine]:
    settings = get_settings()
    if not settings.database_url:
        return None

    return create_engine(settings.database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> Optional[sessionmaker]:
    engine = get_engine()
    if engine is None:
        return None

    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )


def get_db_session() -> Generator[Session, None, None]:
    session_factory = get_session_factory()
    if session_factory is None:
        raise RuntimeError(
            "Database session requested before BFP_DATABASE_URL was configured."
        )

    db_session = session_factory()
    try:
        yield db_session
    finally:
        db_session.close()
