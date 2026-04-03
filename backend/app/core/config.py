from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "beta-feedback-platform-backend"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        description="Allowed frontend origins for local development.",
    )
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
