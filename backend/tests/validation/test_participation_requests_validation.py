from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.participation_requests.schemas import (
    ParticipationRequestCreate,
    ParticipationRequestUpdate,
)


def test_participation_request_create_normalizes_note() -> None:
    payload = ParticipationRequestCreate(
        device_profile_id="  dp_123  ",
        note="  Please consider me for the iOS beta.  ",
    )

    assert payload.device_profile_id == "dp_123"
    assert payload.note == "Please consider me for the iOS beta."


def test_participation_request_create_rejects_blank_device_profile_id() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ParticipationRequestCreate(
            device_profile_id="   ",
        )

    assert "Device profile ID cannot be blank." in str(exc_info.value)


def test_participation_request_update_accepts_decision_status_and_normalizes_note() -> None:
    payload = ParticipationRequestUpdate(
        status="accepted",
        decision_note="  Looks like a good fit for this beta.  ",
    )

    assert payload.status == "accepted"
    assert payload.decision_note == "Looks like a good fit for this beta."


def test_participation_request_update_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ParticipationRequestUpdate(status="reviewing")

    assert "withdrawn" in str(exc_info.value)
