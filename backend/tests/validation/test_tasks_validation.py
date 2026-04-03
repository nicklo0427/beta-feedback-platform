from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.tasks.schemas import TaskCreate, TaskStatus, TaskUpdate


def test_task_create_normalizes_title_and_instruction_summary() -> None:
    payload = TaskCreate(
        title="  Validate onboarding task  ",
        instruction_summary="  Verify the first-run welcome experience.  ",
    )

    assert payload.title == "Validate onboarding task"
    assert payload.instruction_summary == "Verify the first-run welcome experience."
    assert payload.status is None


def test_task_create_rejects_blank_title() -> None:
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title="   ")

    assert "Task title cannot be blank." in str(exc_info.value)


def test_task_create_rejects_blank_device_profile_id() -> None:
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(
            title="Validate onboarding task",
            device_profile_id="   ",
        )

    assert "Device profile ID cannot be blank." in str(exc_info.value)


def test_task_create_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(
            title="Validate onboarding task",
            status="queued",
        )

    assert "Input should be 'draft', 'open', 'assigned', 'in_progress', 'submitted' or 'closed'" in str(
        exc_info.value
    )


def test_task_update_requires_at_least_one_field() -> None:
    with pytest.raises(ValidationError) as exc_info:
        TaskUpdate()

    assert "At least one field must be provided." in str(exc_info.value)


def test_task_update_accepts_null_device_profile_id_and_valid_status() -> None:
    payload = TaskUpdate(
        device_profile_id=None,
        status=TaskStatus.OPEN,
    )

    assert payload.device_profile_id is None
    assert payload.status == TaskStatus.OPEN
