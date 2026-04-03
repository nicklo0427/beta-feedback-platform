from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.feedback.schemas import (
    FeedbackCategory,
    FeedbackCreate,
    FeedbackSeverity,
    FeedbackUpdate,
)


def test_feedback_create_normalizes_optional_fields() -> None:
    payload = FeedbackCreate(
        summary="  App crashes on launch  ",
        rating=4,
        severity=FeedbackSeverity.HIGH,
        category=FeedbackCategory.BUG,
        reproduction_steps="  Open the app and wait  ",
        expected_result="  App should stay responsive  ",
        actual_result="  App exits immediately  ",
        note="  Happens only on cellular  ",
    )

    assert payload.summary == "App crashes on launch"
    assert payload.reproduction_steps == "Open the app and wait"
    assert payload.expected_result == "App should stay responsive"
    assert payload.actual_result == "App exits immediately"
    assert payload.note == "Happens only on cellular"


def test_feedback_create_rejects_blank_summary() -> None:
    with pytest.raises(ValidationError) as exc_info:
        FeedbackCreate(
            summary="   ",
            severity=FeedbackSeverity.HIGH,
            category=FeedbackCategory.BUG,
        )

    assert "Feedback summary cannot be blank." in str(exc_info.value)


def test_feedback_create_rejects_out_of_range_rating() -> None:
    with pytest.raises(ValidationError) as exc_info:
        FeedbackCreate(
            summary="App crashes on launch",
            rating=6,
            severity=FeedbackSeverity.HIGH,
            category=FeedbackCategory.BUG,
        )

    assert "Input should be less than or equal to 5" in str(exc_info.value)


def test_feedback_update_requires_at_least_one_field() -> None:
    with pytest.raises(ValidationError) as exc_info:
        FeedbackUpdate()

    assert "At least one field must be provided." in str(exc_info.value)


def test_feedback_update_accepts_valid_enums_and_null_optional_fields() -> None:
    payload = FeedbackUpdate(
        severity=FeedbackSeverity.CRITICAL,
        category=FeedbackCategory.COMPATIBILITY,
        note=None,
    )

    assert payload.severity == FeedbackSeverity.CRITICAL
    assert payload.category == FeedbackCategory.COMPATIBILITY
    assert payload.note is None
