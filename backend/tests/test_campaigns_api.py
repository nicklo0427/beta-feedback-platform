from __future__ import annotations

from fastapi.testclient import TestClient

from app.modules.accounts.schemas import AccountCreate
from app.modules.accounts.service import create_account
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project


def _create_developer_account(name: str = "Dev Owner"):
    return create_account(AccountCreate(display_name=name, role="developer"))


def _create_tester_account(name: str = "Tester Owner"):
    return create_account(AccountCreate(display_name=name, role="tester"))


def _actor_headers(actor_id: str) -> dict[str, str]:
    return {"X-Actor-Id": actor_id}


def test_campaigns_crud_flow_supports_project_filter(client: TestClient) -> None:
    developer = _create_developer_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    project_id = project.id

    create_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project_id,
            "name": "Closed Beta Round 1",
            "description": "Collect onboarding feedback.",
            "target_platforms": ["ios", "android"],
            "version_label": "0.9.0-beta.1",
        },
        headers=_actor_headers(developer.id),
    )

    assert create_response.status_code == 201
    created_campaign = create_response.json()
    campaign_id = created_campaign["id"]
    assert created_campaign["status"] == "draft"

    list_response = client.get("/api/v1/campaigns")
    assert list_response.status_code == 200
    assert list_response.json() == {
        "items": [
            {
                "id": campaign_id,
                "project_id": project_id,
                "name": "Closed Beta Round 1",
                "target_platforms": ["ios", "android"],
                "version_label": "0.9.0-beta.1",
                "status": "draft",
                "updated_at": created_campaign["updated_at"],
            }
        ],
        "total": 1,
    }

    filtered_response = client.get(f"/api/v1/campaigns?project_id={project_id}")
    assert filtered_response.status_code == 200
    assert filtered_response.json()["total"] == 1
    assert filtered_response.json()["items"][0]["id"] == campaign_id

    detail_response = client.get(f"/api/v1/campaigns/{campaign_id}")
    assert detail_response.status_code == 200
    assert detail_response.json() == created_campaign

    patch_response = client.patch(
        f"/api/v1/campaigns/{campaign_id}",
        json={"status": "active"},
        headers=_actor_headers(developer.id),
    )
    assert patch_response.status_code == 200
    patched_campaign = patch_response.json()
    assert patched_campaign["status"] == "active"
    assert patched_campaign["project_id"] == project_id

    delete_response = client.delete(f"/api/v1/campaigns/{campaign_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    empty_list_response = client.get(f"/api/v1/campaigns?project_id={project_id}")
    assert empty_list_response.status_code == 200
    assert empty_list_response.json() == {"items": [], "total": 0}


def test_campaign_create_requires_current_actor(client: TestClient) -> None:
    response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": "proj_missing",
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "missing_actor_context",
        "message": "Current actor is required.",
        "details": {
            "header": "X-Actor-Id",
        },
    }


def test_campaigns_list_supports_mine_filter_for_owned_projects(client: TestClient) -> None:
    first_account_response = client.post(
        "/api/v1/accounts",
        json={"display_name": "Dev A", "role": "developer"},
    )
    second_account_response = client.post(
        "/api/v1/accounts",
        json={"display_name": "Dev B", "role": "developer"},
    )
    first_account_id = first_account_response.json()["id"]
    second_account_id = second_account_response.json()["id"]

    first_project_response = client.post(
        "/api/v1/projects",
        headers={"X-Actor-Id": first_account_id},
        json={"name": "HabitQuest"},
    )
    second_project_response = client.post(
        "/api/v1/projects",
        headers={"X-Actor-Id": second_account_id},
        json={"name": "FocusFlow"},
    )

    client.post(
        "/api/v1/campaigns",
        headers={"X-Actor-Id": first_account_id},
        json={
            "project_id": first_project_response.json()["id"],
            "name": "Owned Campaign",
            "target_platforms": ["ios"],
        },
    )
    client.post(
        "/api/v1/campaigns",
        headers={"X-Actor-Id": second_account_id},
        json={
            "project_id": second_project_response.json()["id"],
            "name": "Other Campaign",
            "target_platforms": ["android"],
        },
    )

    response = client.get(
        "/api/v1/campaigns?mine=true",
        headers={"X-Actor-Id": first_account_id},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["project_id"] == first_project_response.json()["id"]


def test_campaigns_mine_filter_requires_current_actor_header(client: TestClient) -> None:
    response = client.get("/api/v1/campaigns?mine=true")

    assert response.status_code == 400
    assert response.json() == {
        "code": "missing_actor_context",
        "message": "Current actor is required.",
        "details": {
            "header": "X-Actor-Id",
        },
    }


def test_campaigns_mine_filter_rejects_tester_actor(client: TestClient) -> None:
    tester_response = client.post(
        "/api/v1/accounts",
        json={"display_name": "QA Tester", "role": "tester"},
    )
    tester_id = tester_response.json()["id"]

    response = client.get(
        "/api/v1/campaigns?mine=true",
        headers={"X-Actor-Id": tester_id},
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "forbidden_actor_role",
        "message": "Developer role is required to access owned campaigns.",
        "details": {
            "actor_id": tester_id,
            "actor_role": "tester",
            "required_role": "developer",
        },
    }


def test_campaign_create_requires_existing_project(client: TestClient) -> None:
    developer = _create_developer_account()
    response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": "proj_missing",
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "resource_not_found",
        "message": "Project not found.",
        "details": {
            "resource": "project",
            "id": "proj_missing",
        },
    }


def test_campaign_create_rejects_non_developer_actor(client: TestClient) -> None:
    developer = _create_developer_account()
    tester = _create_tester_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )

    response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project.id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
        headers=_actor_headers(tester.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "forbidden_actor_role",
        "message": "Developer role is required for this operation.",
        "details": {
            "actor_id": tester.id,
            "actor_role": "tester",
            "required_role": "developer",
        },
    }


def test_campaign_patch_rejects_project_id_updates(client: TestClient) -> None:
    developer = _create_developer_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    project_id = project.id

    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project_id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
        headers=_actor_headers(developer.id),
    )
    campaign_id = campaign_response.json()["id"]

    response = client.patch(
        f"/api/v1/campaigns/{campaign_id}",
        json={"project_id": "proj_other"},
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "validation_error",
        "message": "Request validation failed.",
        "details": {
            "fields": [
                {
                    "field": "project_id",
                    "message": "Extra inputs are not permitted",
                }
            ]
        },
    }


def test_campaign_patch_rejects_actor_without_project_ownership(client: TestClient) -> None:
    owner = _create_developer_account("Owner Dev")
    other_developer = _create_developer_account("Other Dev")
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=owner.id,
    )

    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project.id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
        headers=_actor_headers(owner.id),
    )
    campaign_id = campaign_response.json()["id"]

    response = client.patch(
        f"/api/v1/campaigns/{campaign_id}",
        json={"status": "active"},
        headers=_actor_headers(other_developer.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "ownership_mismatch",
        "message": "Current actor does not own the target resource.",
        "details": {
            "actor_id": other_developer.id,
            "resource": "campaign",
            "ownership_anchor": {
                "resource": "project",
                "id": project.id,
                "owner_account_id": owner.id,
            },
        },
    }


def test_project_delete_conflicts_when_campaigns_exist(client: TestClient) -> None:
    developer = _create_developer_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    project_id = project.id

    client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project_id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
        headers=_actor_headers(developer.id),
    )

    response = client.delete(f"/api/v1/projects/{project_id}")

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Project cannot be deleted while campaigns exist.",
        "details": {
            "resource": "project",
            "id": project_id,
            "related_resource": "campaign",
        },
    }


def test_campaign_delete_conflicts_when_tasks_exist(client: TestClient) -> None:
    developer = _create_developer_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    project_id = project.id

    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project_id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
        headers=_actor_headers(developer.id),
    )
    campaign_id = campaign_response.json()["id"]

    client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={"title": "Validate onboarding flow"},
        headers=_actor_headers(developer.id),
    )

    response = client.delete(f"/api/v1/campaigns/{campaign_id}")

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Campaign cannot be deleted while tasks exist.",
        "details": {
            "resource": "campaign",
            "id": campaign_id,
            "related_resource": "task",
        },
    }


def test_campaign_delete_conflicts_when_eligibility_rules_exist(client: TestClient) -> None:
    developer = _create_developer_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    project_id = project.id

    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project_id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
        headers=_actor_headers(developer.id),
    )
    campaign_id = campaign_response.json()["id"]

    client.post(
        f"/api/v1/campaigns/{campaign_id}/eligibility-rules",
        json={
            "platform": "ios",
            "os_name": "iOS",
        },
        headers=_actor_headers(developer.id),
    )

    response = client.delete(f"/api/v1/campaigns/{campaign_id}")

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Campaign cannot be deleted while eligibility rules exist.",
        "details": {
            "resource": "campaign",
            "id": campaign_id,
            "related_resource": "eligibility_rule",
        },
    }


def test_campaign_delete_conflicts_when_safety_exists(client: TestClient) -> None:
    developer = _create_developer_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    project_id = project.id

    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project_id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
        headers=_actor_headers(developer.id),
    )
    campaign_id = campaign_response.json()["id"]

    client.post(
        f"/api/v1/campaigns/{campaign_id}/safety",
        json={
            "distribution_channel": "testflight",
            "source_label": "TestFlight",
            "risk_level": "low",
        },
        headers=_actor_headers(developer.id),
    )

    response = client.delete(f"/api/v1/campaigns/{campaign_id}")

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Campaign cannot be deleted while safety exists.",
        "details": {
            "resource": "campaign",
            "id": campaign_id,
            "related_resource": "campaign_safety",
        },
    }
