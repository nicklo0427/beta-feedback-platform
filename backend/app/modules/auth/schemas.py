from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.accounts.schemas import AccountRole


def _validate_roles(value: Optional[list[AccountRole]]) -> Optional[list[AccountRole]]:
    if value is None:
        return None
    if not value:
        raise ValueError("At least one role must be selected.")

    seen: set[AccountRole] = set()
    normalized_roles: list[AccountRole] = []
    for role in value:
        if role in seen:
            raise ValueError("Roles cannot contain duplicates.")
        seen.add(role)
        normalized_roles.append(role)

    return normalized_roles


def _normalize_email(value: str) -> str:
    normalized = value.strip().lower()
    if not normalized or "@" not in normalized:
        raise ValueError("Email must be a valid address.")
    return normalized


class AuthRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str = Field(..., min_length=1)
    role: Optional[AccountRole] = None
    roles: Optional[list[AccountRole]] = None
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

    @field_validator("roles")
    @classmethod
    def validate_roles(
        cls,
        value: Optional[list[AccountRole]],
    ) -> Optional[list[AccountRole]]:
        return _validate_roles(value)

    @model_validator(mode="after")
    def normalize_roles(self) -> "AuthRegisterRequest":
        if self.roles is None:
            if self.role is None:
                raise ValueError("At least one role must be selected.")
            self.roles = [self.role]
            return self

        if self.role is None:
            self.role = self.roles[0]
            return self

        if self.role not in self.roles:
            raise ValueError("Primary role must be included in roles.")
        return self


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
    roles: list[AccountRole]
    email: str
    is_active: bool


class AuthSessionResponse(BaseModel):
    account: AuthenticatedActor
    expires_at: str
