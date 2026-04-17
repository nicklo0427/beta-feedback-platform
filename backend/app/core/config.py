from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


AuthMode = Literal["auto", "session_only", "session_with_header_fallback"]


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
    auth_mode: AuthMode = Field(
        default="auto",
        description=(
            "Auth mode baseline. Use session_only for beta/staging/production and "
            "session_with_header_fallback only for local QA / seed workflows."
        ),
    )
    auth_dev_actor_header_fallback_enabled: Optional[bool] = Field(
        default=None,
        description=(
            "Legacy compatibility override for X-Actor-Id fallback. Prefer BFP_AUTH_MODE."
        ),
    )

    model_config = SettingsConfigDict(
        env_prefix="BFP_",
        case_sensitive=False,
    )

    @property
    def resolved_auth_mode(
        self,
    ) -> Literal["session_only", "session_with_header_fallback"]:
        if self.auth_mode == "session_only":
            return "session_only"

        if self.auth_mode == "session_with_header_fallback":
            return "session_with_header_fallback"

        if self.auth_dev_actor_header_fallback_enabled is not None:
            return (
                "session_with_header_fallback"
                if self.auth_dev_actor_header_fallback_enabled
                else "session_only"
            )

        app_env = self.app_env.strip().lower()
        if app_env in {"beta", "staging", "production", "prod", "qa"}:
            return "session_only"

        return "session_with_header_fallback"

    @property
    def auth_header_fallback_enabled(self) -> bool:
        return self.resolved_auth_mode == "session_with_header_fallback"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
