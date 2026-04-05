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
    assert payload.bio == "Mobile web tester"
    assert payload.locale == "zh-TW"


def test_account_create_rejects_blank_display_name() -> None:
    with pytest.raises(ValidationError) as exc_info:
        AccountCreate(display_name="   ", role=AccountRole.DEVELOPER)

    assert "Display name cannot be blank." in str(exc_info.value)


def test_account_create_rejects_unknown_role() -> None:
    with pytest.raises(ValidationError) as exc_info:
        AccountCreate(display_name="Alice QA", role="admin")

    assert "Input should be 'developer' or 'tester'" in str(exc_info.value)


def test_account_update_requires_at_least_one_field() -> None:
    with pytest.raises(ValidationError) as exc_info:
        AccountUpdate()

    assert "At least one field must be provided." in str(exc_info.value)


def test_account_update_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        AccountUpdate(unknown_field="x")

    assert "Extra inputs are not permitted" in str(exc_info.value)
