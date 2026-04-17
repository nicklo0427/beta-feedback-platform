from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_settings_dep
from app.core.config import Settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def get_health(settings: Settings = Depends(get_settings_dep)) -> dict[str, object]:
    persistence_mode = "database" if settings.database_url else "memory"
    auth_mode = settings.resolved_auth_mode

    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "database_configured": bool(settings.database_url),
        "persistence_mode": persistence_mode,
        "auth_mode": auth_mode,
    }
