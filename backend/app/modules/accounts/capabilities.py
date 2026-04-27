from __future__ import annotations

from fastapi import status

from app.common.exceptions import AppError
from app.modules.accounts.models import AccountRecord
from app.modules.accounts.schemas import AccountRole


def account_role_values(account: AccountRecord) -> list[str]:
    roles = account.roles or [account.role]
    deduped_roles: list[str] = []
    for role in roles:
        if role not in deduped_roles:
            deduped_roles.append(role)
    return deduped_roles


def account_has_role(account: AccountRecord, role: AccountRole) -> bool:
    return role.value in account_role_values(account)


def forbidden_actor_role_details(
    actor: AccountRecord,
    required_role: AccountRole,
) -> dict[str, object]:
    return {
        "actor_id": actor.id,
        "actor_role": actor.role,
        "actor_roles": account_role_values(actor),
        "required_role": required_role.value,
    }


def raise_forbidden_actor_role(
    actor: AccountRecord,
    required_role: AccountRole,
    message: str,
) -> None:
    raise AppError(
        status_code=status.HTTP_409_CONFLICT,
        code="forbidden_actor_role",
        message=message,
        details=forbidden_actor_role_details(actor, required_role),
    )
