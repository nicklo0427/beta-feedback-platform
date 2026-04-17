from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.migrations import upgrade_database_schema


@lru_cache
def get_engine() -> Optional[Engine]:
    settings = get_settings()
    if not settings.database_url:
        return None

    database_url = settings.database_url
    connect_args: dict[str, object] = {}

    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if ":///" in database_url and ":memory:" not in database_url:
            database_path = database_url.split(":///", 1)[1]
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    return create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


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


def database_persistence_enabled() -> bool:
    return get_session_factory() is not None


@lru_cache
def ensure_database_ready() -> bool:
    engine = get_engine()
    if engine is None:
        return False

    upgrade_database_schema("head")
    return True


@contextmanager
def db_session_scope() -> Generator[Session, None, None]:
    ensure_database_ready()
    session_factory = get_session_factory()
    if session_factory is None:
        raise RuntimeError(
            "Database session requested before BFP_DATABASE_URL was configured."
        )

    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_database_runtime() -> None:
    engine = get_engine()
    if engine is not None:
        engine.dispose()

    ensure_database_ready.cache_clear()
    get_session_factory.cache_clear()
    get_engine.cache_clear()
