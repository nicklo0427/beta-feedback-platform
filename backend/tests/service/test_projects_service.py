from __future__ import annotations

import pytest
from fastapi import status

from app.common.exceptions import AppError
from app.modules.accounts.schemas import AccountCreate, AccountRole
from app.modules.accounts.service import create_account
from app.modules.campaigns.schemas import CampaignCreate
from app.modules.campaigns.service import create_campaign
from app.modules.projects.schemas import ProjectCreate, ProjectUpdate
from app.modules.projects.service import (
    create_project,
    delete_project,
    ensure_project_exists,
    list_projects,
    update_project,
)


def test_project_service_create_and_list_returns_expected_items() -> None:
    created_project = create_project(
        ProjectCreate(
            name="HabitQuest",
            description="Cross-platform habit tracking app beta program.",
        )
    )

    listed_projects = list_projects()

    assert listed_projects.total == 1
    assert listed_projects.items[0].id == created_project.id
    assert listed_projects.items[0].name == "HabitQuest"
    assert listed_projects.items[0].description == (
        "Cross-platform habit tracking app beta program."
    )


def test_project_service_create_assigns_owner_when_actor_is_developer() -> None:
    developer = create_account(
        AccountCreate(display_name="Dev Lead", role=AccountRole.DEVELOPER)
    )

    created_project = create_project(
        ProjectCreate(name="HabitQuest"),
        developer.id,
    )

    assert created_project.owner_account_id == developer.id


def test_project_service_create_rejects_non_developer_actor() -> None:
    tester = create_account(
        AccountCreate(display_name="QA Tester", role=AccountRole.TESTER)
    )

    with pytest.raises(AppError) as exc_info:
        create_project(ProjectCreate(name="HabitQuest"), tester.id)

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "forbidden_actor_role"
    assert error.details == {
        "actor_id": tester.id,
        "actor_role": "tester",
        "actor_roles": ["tester"],
        "required_role": "developer",
    }


def test_project_service_list_filters_by_owner_account_id() -> None:
    first_developer = create_account(
        AccountCreate(display_name="Dev A", role=AccountRole.DEVELOPER)
    )
    second_developer = create_account(
        AccountCreate(display_name="Dev B", role=AccountRole.DEVELOPER)
    )
    owned_project = create_project(ProjectCreate(name="HabitQuest"), first_developer.id)
    create_project(ProjectCreate(name="FocusFlow"), second_developer.id)

    listed_projects = list_projects(owner_account_id=first_developer.id)

    assert listed_projects.total == 1
    assert listed_projects.items[0].id == owned_project.id
    assert listed_projects.items[0].owner_account_id == first_developer.id


def test_project_service_ensure_project_exists_raises_not_found() -> None:
    with pytest.raises(AppError) as exc_info:
        ensure_project_exists("proj_missing")

    error = exc_info.value
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert error.code == "resource_not_found"
    assert error.details == {
        "resource": "project",
        "id": "proj_missing",
    }


def test_project_service_delete_rejects_project_with_campaigns() -> None:
    created_project = create_project(ProjectCreate(name="HabitQuest"))
    create_campaign(
        CampaignCreate(
            project_id=created_project.id,
            name="Closed Beta Round 1",
            target_platforms=["ios"],
        )
    )

    with pytest.raises(AppError) as exc_info:
        delete_project(created_project.id)

    error = exc_info.value
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.code == "conflict"
    assert error.details == {
        "resource": "project",
        "id": created_project.id,
        "related_resource": "campaign",
    }


def test_project_service_update_changes_only_provided_fields() -> None:
    created_project = create_project(
        ProjectCreate(
            name="HabitQuest",
            description="Original description.",
        )
    )

    updated_project = update_project(
        created_project.id,
        ProjectUpdate(description="Updated project summary."),
    )

    assert updated_project.id == created_project.id
    assert updated_project.name == "HabitQuest"
    assert updated_project.description == "Updated project summary."
