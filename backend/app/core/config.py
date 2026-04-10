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
        description="Database connection URL for persistence mode.",
    )
    auth_session_cookie_name: str = Field(
        default="bfp_session",
        description="Cookie name for the MVP auth session.",
    )
    auth_session_duration_hours: int = Field(
        default=24,
        description="Session lifetime in hours for the MVP auth flow.",
    )
    auth_session_cookie_secure: bool = Field(
        default=False,
        description="Whether the auth session cookie should require HTTPS.",
    )
    auth_dev_actor_header_fallback_enabled: bool = Field(
        default=True,
        description="Allows X-Actor-Id fallback for local dev and seed workflows.",
    )

    model_config = SettingsConfigDict(
        env_prefix="BFP_",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
