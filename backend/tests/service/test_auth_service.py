from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.auth.schemas import AuthLoginRequest, AuthRegisterRequest
from app.modules.auth.service import get_current_session, login, logout, register


def test_auth_service_register_creates_session_and_current_actor() -> None:
    session_id, session = register(
        AuthRegisterRequest(
            display_name="Release Owner",
            role="developer",
            email="owner@example.com",
            password="supersecret",
        )
    )

    assert session_id.startswith("sess_")
    assert session.account.display_name == "Release Owner"
    assert session.account.email == "owner@example.com"
    assert session.account.roles == ["developer"]
    assert session.expires_at

    current_session = get_current_session(session_id)
    assert current_session.account.id == session.account.id


def test_auth_service_register_accepts_dual_roles() -> None:
    _, session = register(
        AuthRegisterRequest(
            display_name="Dual Mode Builder",
            roles=["developer", "tester"],
            email="dual@example.com",
            password="supersecret",
        )
    )

    assert session.account.role == "developer"
    assert session.account.roles == ["developer", "tester"]


def test_auth_service_login_rejects_invalid_credentials() -> None:
    register(
        AuthRegisterRequest(
            display_name="QA Tester",
            role="tester",
            email="tester@example.com",
            password="supersecret",
        )
    )

    with pytest.raises(AppError) as exc_info:
        login(
            AuthLoginRequest(
                email="tester@example.com",
                password="wrong-pass",
            )
        )

    error = exc_info.value
    assert error.status_code == status.HTTP_401_UNAUTHORIZED
    assert error.code == "invalid_credentials"


def test_auth_service_logout_invalidates_session() -> None:
    session_id, _ = register(
        AuthRegisterRequest(
            display_name="QA Tester",
            role="tester",
            email="tester@example.com",
            password="supersecret",
        )
    )

    logout(session_id)

    with pytest.raises(AppError) as exc_info:
        get_current_session(session_id)

    error = exc_info.value
    assert error.status_code == status.HTTP_401_UNAUTHORIZED
    assert error.code == "unauthenticated"
