from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.auth.schemas import AuthLoginRequest, AuthRegisterRequest


def test_auth_register_validation_rejects_short_password() -> None:
    with pytest.raises(ValidationError):
        AuthRegisterRequest(
            display_name="Alice",
            role="tester",
            email="alice@example.com",
            password="short",
        )


def test_auth_register_validation_backfills_legacy_role() -> None:
    payload = AuthRegisterRequest(
        display_name="Alice",
        role="tester",
        email="alice@example.com",
        password="long-enough-password",
    )

    assert payload.roles == ["tester"]


def test_auth_register_validation_accepts_dual_roles() -> None:
    payload = AuthRegisterRequest(
        display_name="Alice",
        roles=["developer", "tester"],
        email="alice@example.com",
        password="long-enough-password",
    )

    assert payload.role == "developer"
    assert payload.roles == ["developer", "tester"]


def test_auth_register_validation_rejects_primary_role_outside_roles() -> None:
    with pytest.raises(ValidationError):
        AuthRegisterRequest(
            display_name="Alice",
            role="developer",
            roles=["tester"],
            email="alice@example.com",
            password="long-enough-password",
        )


def test_auth_login_validation_normalizes_email() -> None:
    payload = AuthLoginRequest(
        email="  Alice@example.com ",
        password="long-enough-password",
    )

    assert payload.email == "alice@example.com"
