from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

from app.core.config import get_settings


def backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def alembic_ini_path() -> Path:
    return backend_root() / "alembic.ini"


def alembic_script_location() -> Path:
    return backend_root() / "alembic"


def build_alembic_config(database_url: str | None = None) -> Config:
    config = Config(str(alembic_ini_path()))
    config.set_main_option("script_location", str(alembic_script_location()))

    effective_database_url = database_url or get_settings().database_url
    if effective_database_url:
        config.set_main_option("sqlalchemy.url", effective_database_url)

    return config


def upgrade_database_schema(revision: str = "head") -> bool:
    settings = get_settings()
    if not settings.database_url:
        return False

    command.upgrade(build_alembic_config(settings.database_url), revision)
    return True
