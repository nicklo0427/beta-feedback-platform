from __future__ import annotations

from typing import Optional

from app.modules.accounts.models import AccountRecord

_ACCOUNTS: dict[str, AccountRecord] = {}


def list_accounts() -> list[AccountRecord]:
    return list(_ACCOUNTS.values())


def get_account(account_id: str) -> Optional[AccountRecord]:
    return _ACCOUNTS.get(account_id)


def create_account(record: AccountRecord) -> AccountRecord:
    _ACCOUNTS[record.id] = record
    return record


def update_account(record: AccountRecord) -> AccountRecord:
    _ACCOUNTS[record.id] = record
    return record


def delete_account(account_id: str) -> None:
    _ACCOUNTS.pop(account_id, None)


def clear_accounts() -> None:
    _ACCOUNTS.clear()
