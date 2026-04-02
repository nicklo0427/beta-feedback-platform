from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "beta-feedback-platform-backend"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: Optional[str] = Field(
        default=None,
        description="Reserved PostgreSQL connection URL for future integration.",
    )

    model_config = SettingsConfigDict(
        env_prefix="BFP_",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
