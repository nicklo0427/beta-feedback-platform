from __future__ import annotations

from fastapi.testclient import TestClient

from app.modules.accounts.schemas import AccountCreate
from app.modules.accounts.service import create_account
from app.modules.projects.schemas import ProjectCreate
from app.modules.projects.service import create_project


def _create_developer_account(name: str = "Dev Owner"):
    return create_account(AccountCreate(display_name=name, role="developer"))


def _create_tester_account(name: str = "QA Tester"):
    return create_account(AccountCreate(display_name=name, role="tester"))


def _actor_headers(actor_id: str) -> dict[str, str]:
    return {"X-Actor-Id": actor_id}


def test_tasks_crud_flow_supports_filters_and_submitted_at(client: TestClient) -> None:
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

    device_profile_response = client.post(
        "/api/v1/device-profiles",
        json={
            "name": "QA iPhone 15",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
        },
    )
    device_profile_id = device_profile_response.json()["id"]

    create_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Validate onboarding flow",
            "instruction_summary": "Verify the welcome experience.",
            "device_profile_id": device_profile_id,
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )

    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task["id"]

    assert created_task["campaign_id"] == campaign_id
    assert created_task["device_profile_id"] == device_profile_id
    assert created_task["title"] == "Validate onboarding flow"
    assert created_task["status"] == "assigned"
    assert created_task["submitted_at"] is None
    assert created_task["qualification_context"] == {
        "device_profile_id": device_profile_id,
        "device_profile_name": "QA iPhone 15",
        "qualification_status": "qualified",
        "matched_rule_id": None,
        "reason_summary": "目前沒有啟用中的資格限制。",
        "qualification_drift": False,
    }

    list_response = client.get(
        f"/api/v1/tasks?campaign_id={campaign_id}&device_profile_id={device_profile_id}&status=assigned"
    )

    assert list_response.status_code == 200
    assert list_response.json() == {
        "items": [
            {
                "id": task_id,
                "campaign_id": campaign_id,
                "device_profile_id": device_profile_id,
                "title": "Validate onboarding flow",
                "status": "assigned",
                "updated_at": created_task["updated_at"],
                "qualification_context": {
                    "device_profile_id": device_profile_id,
                    "device_profile_name": "QA iPhone 15",
                    "qualification_status": "qualified",
                    "matched_rule_id": None,
                    "reason_summary": "目前沒有啟用中的資格限制。",
                    "qualification_drift": False,
                },
            }
        ],
        "total": 1,
    }

    detail_response = client.get(f"/api/v1/tasks/{task_id}")
    assert detail_response.status_code == 200
    assert detail_response.json() == created_task

    patch_in_progress_response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "in_progress"},
        headers=_actor_headers(developer.id),
    )
    assert patch_in_progress_response.status_code == 200
    in_progress_task = patch_in_progress_response.json()
    assert in_progress_task["status"] == "in_progress"
    assert in_progress_task["submitted_at"] is None

    patch_submitted_response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "submitted"},
        headers=_actor_headers(developer.id),
    )
    assert patch_submitted_response.status_code == 200
    submitted_task = patch_submitted_response.json()
    assert submitted_task["status"] == "submitted"
    assert submitted_task["submitted_at"] is not None

    delete_response = client.delete(f"/api/v1/tasks/{task_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""


def test_task_create_requires_existing_campaign(client: TestClient) -> None:
    developer = _create_developer_account()
    response = client.post(
        "/api/v1/campaigns/camp_missing/tasks",
        json={
            "title": "Validate onboarding flow",
        },
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "resource_not_found",
        "message": "Campaign not found.",
        "details": {
            "resource": "campaign",
            "id": "camp_missing",
        },
    }


def test_task_patch_rejects_campaign_id_updates(client: TestClient) -> None:
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
    task_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={"title": "Validate onboarding flow"},
        headers=_actor_headers(developer.id),
    )
    task_id = task_response.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"campaign_id": "camp_other"},
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "validation_error",
        "message": "Request validation failed.",
        "details": {
            "fields": [
                {
                    "field": "campaign_id",
                    "message": "Extra inputs are not permitted",
                }
            ]
        },
    }


def test_task_patch_rejects_illegal_status_transition(client: TestClient) -> None:
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
    device_profile_response = client.post(
        "/api/v1/device-profiles",
        json={
            "name": "QA iPhone 15",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
        },
    )
    device_profile_id = device_profile_response.json()["id"]
    task_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": device_profile_id,
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )
    task_id = task_response.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "submitted"},
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Task status transition is not allowed.",
        "details": {
            "resource": "task",
            "current_status": "assigned",
            "next_status": "submitted",
        },
    }


def test_task_create_rejects_ineligible_assignment(client: TestClient) -> None:
    developer = _create_developer_account()
    tester = _create_tester_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project.id,
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
            "os_version_min": "17.0",
            "install_channel": "testflight",
        },
        headers=_actor_headers(developer.id),
    )
    device_profile_response = client.post(
        "/api/v1/device-profiles",
        headers=_actor_headers(tester.id),
        json={
            "name": "QA iPhone 15 (Alt Channel)",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
            "os_version": "17.4",
            "install_channel": "app-store-connect",
        },
    )
    device_profile_id = device_profile_response.json()["id"]

    response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": device_profile_id,
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "assignment_not_eligible",
        "message": "Selected device profile does not meet campaign eligibility requirements.",
        "details": {
            "campaign_id": campaign_id,
            "device_profile_id": device_profile_id,
            "qualification_status": "not_qualified",
            "matched_rule_id": None,
            "reason_codes": ["install_channel_mismatch"],
            "reason_summary": "主要未符合條件：安裝渠道不符合目前活動條件。",
        },
    }


def test_task_patch_rejects_ineligible_assignment(client: TestClient) -> None:
    developer = _create_developer_account()
    tester = _create_tester_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project.id,
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
            "os_version_min": "17.0",
            "install_channel": "testflight",
        },
        headers=_actor_headers(developer.id),
    )

    eligible_device_profile_response = client.post(
        "/api/v1/device-profiles",
        headers=_actor_headers(tester.id),
        json={
            "name": "QA iPhone 15",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
            "os_version": "17.4",
            "install_channel": "testflight",
        },
    )
    ineligible_device_profile_response = client.post(
        "/api/v1/device-profiles",
        headers=_actor_headers(tester.id),
        json={
            "name": "QA iPhone 15 (Alt Channel)",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
            "os_version": "17.4",
            "install_channel": "app-store-connect",
        },
    )
    task_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": eligible_device_profile_response.json()["id"],
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )
    task_id = task_response.json()["id"]
    ineligible_device_profile_id = ineligible_device_profile_response.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={
            "device_profile_id": ineligible_device_profile_id,
        },
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "assignment_not_eligible",
        "message": "Selected device profile does not meet campaign eligibility requirements.",
        "details": {
            "campaign_id": campaign_id,
            "device_profile_id": ineligible_device_profile_id,
            "qualification_status": "not_qualified",
            "matched_rule_id": None,
            "reason_codes": ["install_channel_mismatch"],
            "reason_summary": "主要未符合條件：安裝渠道不符合目前活動條件。",
        },
    }


def test_task_detail_surfaces_qualification_drift_context(client: TestClient) -> None:
    developer = _create_developer_account()
    tester = _create_tester_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project.id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
        headers=_actor_headers(developer.id),
    )
    campaign_id = campaign_response.json()["id"]
    rule_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/eligibility-rules",
        json={
            "platform": "ios",
            "os_name": "iOS",
            "os_version_min": "17.0",
            "install_channel": "testflight",
        },
        headers=_actor_headers(developer.id),
    )
    device_profile_response = client.post(
        "/api/v1/device-profiles",
        headers=_actor_headers(tester.id),
        json={
            "name": "QA iPhone 15",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
            "os_version": "17.4",
            "install_channel": "testflight",
        },
    )
    device_profile_id = device_profile_response.json()["id"]
    task_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": device_profile_id,
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )
    task_id = task_response.json()["id"]

    patch_rule_response = client.patch(
        f"/api/v1/eligibility-rules/{rule_response.json()['id']}",
        json={
            "install_channel": "app-store-connect",
        },
        headers=_actor_headers(developer.id),
    )
    assert patch_rule_response.status_code == 200

    detail_response = client.get(f"/api/v1/tasks/{task_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["qualification_context"] == {
        "device_profile_id": device_profile_id,
        "device_profile_name": "QA iPhone 15",
        "qualification_status": "not_qualified",
        "matched_rule_id": None,
        "reason_summary": "主要未符合條件：安裝渠道不符合目前活動條件。",
        "qualification_drift": True,
    }


def test_task_delete_conflicts_when_feedback_exists(client: TestClient) -> None:
    developer = _create_developer_account()
    tester = _create_tester_account()
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
    task_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": client.post(
                "/api/v1/device-profiles",
                headers=_actor_headers(tester.id),
                json={
                    "name": "QA iPhone 15",
                    "platform": "ios",
                    "device_model": "iPhone 15 Pro",
                    "os_name": "iOS",
                },
            ).json()["id"],
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )
    task_id = task_response.json()["id"]

    client.post(
        f"/api/v1/tasks/{task_id}/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
        },
        headers=_actor_headers(tester.id),
    )

    response = client.delete(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Task cannot be deleted while feedback exists.",
        "details": {
            "resource": "task",
            "id": task_id,
            "related_resource": "feedback",
        },
    }


def test_tasks_list_supports_mine_filter_for_tester_inbox(client: TestClient) -> None:
    tester_response = client.post(
        "/api/v1/accounts",
        json={"display_name": "QA Tester", "role": "tester"},
    )
    other_tester_response = client.post(
        "/api/v1/accounts",
        json={"display_name": "QA Backup", "role": "tester"},
    )
    tester_id = tester_response.json()["id"]
    other_tester_id = other_tester_response.json()["id"]

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

    owned_device_profile_response = client.post(
        "/api/v1/device-profiles",
        headers={"X-Actor-Id": tester_id},
        json={
            "name": "QA iPhone 15",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
        },
    )
    owned_device_profile_id = owned_device_profile_response.json()["id"]
    other_device_profile_response = client.post(
        "/api/v1/device-profiles",
        headers={"X-Actor-Id": other_tester_id},
        json={
            "name": "QA Pixel 9",
            "platform": "android",
            "device_model": "Pixel 9",
            "os_name": "Android",
        },
    )
    other_device_profile_id = other_device_profile_response.json()["id"]

    owned_task_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": owned_device_profile_id,
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )
    client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Check pricing CTA",
            "device_profile_id": other_device_profile_id,
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )

    response = client.get(
        "/api/v1/tasks?mine=true&status=assigned",
        headers={"X-Actor-Id": tester_id},
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": owned_task_response.json()["id"],
                "campaign_id": campaign_id,
                "device_profile_id": owned_device_profile_id,
                "title": "Validate onboarding flow",
                "status": "assigned",
                "updated_at": owned_task_response.json()["updated_at"],
                "qualification_context": {
                    "device_profile_id": owned_device_profile_id,
                    "device_profile_name": "QA iPhone 15",
                    "qualification_status": "qualified",
                    "matched_rule_id": None,
                    "reason_summary": "目前沒有啟用中的資格限制。",
                    "qualification_drift": False,
                },
            }
        ],
        "total": 1,
    }


def test_tasks_mine_filter_returns_empty_when_actor_has_no_owned_device_profiles(
    client: TestClient,
) -> None:
    tester_response = client.post(
        "/api/v1/accounts",
        json={"display_name": "QA Tester", "role": "tester"},
    )
    tester_id = tester_response.json()["id"]

    response = client.get(
        "/api/v1/tasks?mine=true",
        headers={"X-Actor-Id": tester_id},
    )

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0}


def test_tasks_mine_filter_requires_current_actor_header(client: TestClient) -> None:
    response = client.get("/api/v1/tasks?mine=true")

    assert response.status_code == 400
    assert response.json() == {
        "code": "missing_actor_context",
        "message": "Current actor is required.",
        "details": {
            "header": "X-Actor-Id",
        },
    }


def test_task_create_requires_current_actor_header(client: TestClient) -> None:
    developer = _create_developer_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project.id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
        headers=_actor_headers(developer.id),
    )
    campaign_id = campaign_response.json()["id"]

    response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={"title": "Validate onboarding flow"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "missing_actor_context",
        "message": "Current actor is required.",
        "details": {
            "header": "X-Actor-Id",
        },
    }


def test_task_create_rejects_tester_actor(client: TestClient) -> None:
    developer = _create_developer_account()
    tester = _create_tester_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project.id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
        headers=_actor_headers(developer.id),
    )
    campaign_id = campaign_response.json()["id"]

    response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={"title": "Validate onboarding flow"},
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


def test_task_patch_supports_tester_start_for_owned_assigned_task(
    client: TestClient,
) -> None:
    developer = _create_developer_account()
    tester = _create_tester_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project.id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
        headers=_actor_headers(developer.id),
    )
    campaign_id = campaign_response.json()["id"]
    device_profile_response = client.post(
        "/api/v1/device-profiles",
        headers=_actor_headers(tester.id),
        json={
            "name": "QA iPhone 15",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
        },
    )
    task_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": device_profile_response.json()["id"],
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )

    response = client.patch(
        f"/api/v1/tasks/{task_response.json()['id']}",
        json={"status": "in_progress"},
        headers=_actor_headers(tester.id),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    assert response.json()["device_profile_id"] == device_profile_response.json()["id"]


def test_task_patch_rejects_tester_for_unowned_task(client: TestClient) -> None:
    developer = _create_developer_account()
    tester = _create_tester_account("Primary Tester")
    other_tester = _create_tester_account("Other Tester")
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project.id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
        headers=_actor_headers(developer.id),
    )
    campaign_id = campaign_response.json()["id"]
    other_device_profile_response = client.post(
        "/api/v1/device-profiles",
        headers=_actor_headers(other_tester.id),
        json={
            "name": "QA iPhone 15",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
        },
    )
    task_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": other_device_profile_response.json()["id"],
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )

    response = client.patch(
        f"/api/v1/tasks/{task_response.json()['id']}",
        json={"status": "in_progress"},
        headers=_actor_headers(tester.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "ownership_mismatch",
        "message": "Current actor does not own the target resource.",
        "details": {
            "actor_id": tester.id,
            "resource": "task",
            "ownership_anchor": {
                "resource": "device_profile",
                "id": other_device_profile_response.json()["id"],
                "owner_account_id": other_tester.id,
            },
        },
    }


def test_task_patch_rejects_tester_updates_other_than_start(client: TestClient) -> None:
    developer = _create_developer_account()
    tester = _create_tester_account()
    project = create_project(
        ProjectCreate(name="HabitQuest"),
        current_actor_id=developer.id,
    )
    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project.id,
            "name": "Closed Beta Round 1",
            "target_platforms": ["ios"],
        },
        headers=_actor_headers(developer.id),
    )
    campaign_id = campaign_response.json()["id"]
    device_profile_response = client.post(
        "/api/v1/device-profiles",
        headers=_actor_headers(tester.id),
        json={
            "name": "QA iPhone 15",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
        },
    )
    task_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": device_profile_response.json()["id"],
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )

    response = client.patch(
        f"/api/v1/tasks/{task_response.json()['id']}",
        json={"title": "Tester should not rename task"},
        headers=_actor_headers(tester.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "forbidden_actor_role",
        "message": "Tester can only start assigned tasks they own.",
        "details": {
            "actor_id": tester.id,
            "actor_role": "tester",
            "required_role": "developer",
        },
    }
