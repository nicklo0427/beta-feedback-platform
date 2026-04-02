from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.projects.schemas import ProjectCreate, ProjectUpdate


def test_project_create_normalizes_name_and_description() -> None:
    payload = ProjectCreate(
        name="  HabitQuest  ",
        description="  Cross-platform habit tracking app beta program.  ",
    )

    assert payload.name == "HabitQuest"
    assert payload.description == "Cross-platform habit tracking app beta program."


def test_project_create_rejects_blank_name() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ProjectCreate(name="   ")

    assert "Project name cannot be blank." in str(exc_info.value)


def test_project_create_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ProjectCreate(name="HabitQuest", unknown_field="x")

    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_project_update_requires_at_least_one_field() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ProjectUpdate()

    assert "At least one field must be provided." in str(exc_info.value)
