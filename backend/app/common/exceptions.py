from __future__ import annotations

from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.common.responses import build_error_response


class AppError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def _format_validation_details(exc: RequestValidationError) -> dict[str, Any]:
    fields: list[dict[str, str]] = []

    for error in exc.errors():
        location = [str(item) for item in error.get("loc", ())]
        if location and location[0] in {"body", "query", "path"}:
            location = location[1:]

        fields.append(
            {
                "field": ".".join(location) or "request",
                "message": error["msg"],
            }
        )

    return {"fields": fields}


async def app_error_exception_handler(
    request: Request,
    exc: AppError,
) -> JSONResponse:
    del request
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details,
        ),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    del request
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=build_error_response(
            code="validation_error",
            message="Request validation failed.",
            details=_format_validation_details(exc),
        ),
    )
