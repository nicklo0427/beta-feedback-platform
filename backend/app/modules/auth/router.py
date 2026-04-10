from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status

from app.api.deps import get_settings_dep
from app.core.config import Settings
from app.modules.auth.schemas import AuthLoginRequest, AuthRegisterRequest, AuthSessionResponse
from app.modules.auth.service import get_current_session, login, logout, register

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(
    response: Response,
    *,
    session_id: str,
    settings: Settings,
) -> None:
    response.set_cookie(
        key=settings.auth_session_cookie_name,
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=settings.auth_session_cookie_secure,
        max_age=settings.auth_session_duration_hours * 3600,
        path="/",
    )


def _clear_session_cookie(response: Response, *, settings: Settings) -> None:
    response.delete_cookie(
        key=settings.auth_session_cookie_name,
        path="/",
    )


@router.post("/register", response_model=AuthSessionResponse, status_code=status.HTTP_201_CREATED)
def register_route(
    payload: AuthRegisterRequest,
    response: Response,
    settings: Settings = Depends(get_settings_dep),
) -> AuthSessionResponse:
    session_id, session_response = register(payload)
    _set_session_cookie(response, session_id=session_id, settings=settings)
    return session_response


@router.post("/login", response_model=AuthSessionResponse)
def login_route(
    payload: AuthLoginRequest,
    response: Response,
    settings: Settings = Depends(get_settings_dep),
) -> AuthSessionResponse:
    session_id, session_response = login(payload)
    _set_session_cookie(response, session_id=session_id, settings=settings)
    return session_response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_route(
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings_dep),
) -> Response:
    session_id = request.cookies.get(settings.auth_session_cookie_name)
    logout(session_id)
    _clear_session_cookie(response, settings=settings)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=AuthSessionResponse)
def me_route(
    request: Request,
    settings: Settings = Depends(get_settings_dep),
) -> AuthSessionResponse:
    session_id = request.cookies.get(settings.auth_session_cookie_name)
    return get_current_session(session_id)
