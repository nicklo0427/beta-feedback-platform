from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def build_list_response(items: Sequence[Any]) -> dict[str, Any]:
    serialized_items = list(items)
    return {
        "items": serialized_items,
        "total": len(serialized_items),
    }


def build_error_response(
    *,
    code: str,
    message: str,
    details: Any = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "details": details,
    }
