from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.accounts.schemas import AccountCreate, AccountRole, AccountUpdate


def test_account_create_normalizes_required_and_optional_strings() -> None:
    payload = AccountCreate(
        display_name="  Alice QA  ",
        role=AccountRole.TESTER,
        bio="  Mobile web tester  ",
        locale="  zh-TW  ",
    )

    assert payload.display_name == "Alice QA"
    assert payload.roles == [AccountRole.TESTER]
    assert payload.bio == "Mobile web tester"
    assert payload.locale == "zh-TW"


def test_account_create_accepts_dual_roles() -> None:
    payload = AccountCreate(
        display_name="Dual Role User",
        role=AccountRole.DEVELOPER,
        roles=[AccountRole.DEVELOPER, AccountRole.TESTER],
    )

    assert payload.role == AccountRole.DEVELOPER
    assert payload.roles == [AccountRole.DEVELOPER, AccountRole.TESTER]


def test_account_create_rejects_blank_display_name() -> None:
    with pytest.raises(ValidationError) as exc_info:
        AccountCreate(display_name="   ", role=AccountRole.DEVELOPER)

    assert "Display name cannot be blank." in str(exc_info.value)


def test_account_create_rejects_unknown_role() -> None:
    with pytest.raises(ValidationError) as exc_info:
        AccountCreate(display_name="Alice QA", role="admin")

    assert "Input should be 'developer' or 'tester'" in str(exc_info.value)


def test_account_create_rejects_unknown_roles_value() -> None:
    with pytest.raises(ValidationError) as exc_info:
        AccountCreate(
            display_name="Alice QA",
            role=AccountRole.TESTER,
            roles=[AccountRole.TESTER, "admin"],
        )

    assert "Input should be 'developer' or 'tester'" in str(exc_info.value)


def test_account_create_rejects_empty_roles() -> None:
    with pytest.raises(ValidationError) as exc_info:
        AccountCreate(
            display_name="Alice QA",
            role=AccountRole.TESTER,
            roles=[],
        )

    assert "At least one role must be selected." in str(exc_info.value)


def test_account_create_rejects_duplicate_roles() -> None:
    with pytest.raises(ValidationError) as exc_info:
        AccountCreate(
            display_name="Alice QA",
            role=AccountRole.TESTER,
            roles=[AccountRole.TESTER, AccountRole.TESTER],
        )

    assert "Roles cannot contain duplicates." in str(exc_info.value)


def test_account_create_rejects_primary_role_outside_roles() -> None:
    with pytest.raises(ValidationError) as exc_info:
        AccountCreate(
            display_name="Alice QA",
            role=AccountRole.DEVELOPER,
            roles=[AccountRole.TESTER],
        )

    assert "Primary role must be included in roles." in str(exc_info.value)


def test_account_update_requires_at_least_one_field() -> None:
    with pytest.raises(ValidationError) as exc_info:
        AccountUpdate()

    assert "At least one field must be provided." in str(exc_info.value)


def test_account_update_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        AccountUpdate(unknown_field="x")

    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_account_update_accepts_roles_only() -> None:
    payload = AccountUpdate(roles=[AccountRole.DEVELOPER, AccountRole.TESTER])

    assert payload.roles == [AccountRole.DEVELOPER, AccountRole.TESTER]
