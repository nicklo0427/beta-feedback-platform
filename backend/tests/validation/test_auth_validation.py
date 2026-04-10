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


def test_auth_login_validation_normalizes_email() -> None:
    payload = AuthLoginRequest(
        email="  Alice@example.com ",
        password="long-enough-password",
    )

    assert payload.email == "alice@example.com"
