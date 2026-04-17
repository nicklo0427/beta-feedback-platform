from __future__ import annotations

from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from app.db.base import Base
from app.db import entities  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _database_url() -> str:
    return os.getenv("BFP_DATABASE_URL") or config.get_main_option("sqlalchemy.url")


def _connect_args(url: str) -> dict[str, object]:
    if url.startswith("sqlite"):
        return {
            "check_same_thread": False,
        }

    return {}


def run_migrations_offline() -> None:
    url = _database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = _database_url()
    connectable = create_engine(
        url,
        poolclass=NullPool,
        connect_args=_connect_args(url),
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
