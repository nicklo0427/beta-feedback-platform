from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.accounts.schemas import AccountRole


def _normalize_email(value: str) -> str:
    normalized = value.strip().lower()
    if not normalized or "@" not in normalized:
        raise ValueError("Email must be a valid address.")
    return normalized


class AuthRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str = Field(..., min_length=1)
    role: AccountRole
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
    bio: Optional[str] = None
    locale: Optional[str] = None

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Display name cannot be blank.")
        return normalized

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return _normalize_email(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return normalized

    @field_validator("bio", "locale")
    @classmethod
    def normalize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class AuthLoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return _normalize_email(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return normalized


class AuthenticatedActor(BaseModel):
    id: str
    display_name: str
    role: AccountRole
    email: str
    is_active: bool


class AuthSessionResponse(BaseModel):
    account: AuthenticatedActor
    expires_at: str
