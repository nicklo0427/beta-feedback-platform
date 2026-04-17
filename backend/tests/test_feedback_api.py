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


def test_feedback_crud_flow_derives_relations_and_updates_task_status(client: TestClient) -> None:
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

    create_response = client.post(
        f"/api/v1/tasks/{task_id}/feedback",
        json={
            "summary": "App crashes on launch",
            "rating": 4,
            "severity": "high",
            "category": "bug",
            "actual_result": "App exits immediately.",
        },
        headers=_actor_headers(tester.id),
    )

    assert create_response.status_code == 201
    created_feedback = create_response.json()
    feedback_id = created_feedback["id"]

    assert created_feedback["task_id"] == task_id
    assert created_feedback["campaign_id"] == campaign_id
    assert created_feedback["device_profile_id"] == device_profile_id
    assert created_feedback["summary"] == "App crashes on launch"
    assert created_feedback["review_status"] == "submitted"
    assert created_feedback["developer_note"] is None
    assert created_feedback["submitted_at"]
    assert created_feedback["resubmitted_at"] is None
    assert created_feedback["updated_at"]

    list_response = client.get(
        f"/api/v1/tasks/{task_id}/feedback",
        headers=_actor_headers(tester.id),
    )
    assert list_response.status_code == 200
    assert list_response.json() == {
        "items": [
            {
                "id": feedback_id,
                "task_id": task_id,
                "summary": "App crashes on launch",
                "severity": "high",
                "category": "bug",
                "submitted_at": created_feedback["submitted_at"],
            }
        ],
        "total": 1,
    }

    detail_response = client.get(
        f"/api/v1/feedback/{feedback_id}",
        headers=_actor_headers(tester.id),
    )
    assert detail_response.status_code == 200
    assert detail_response.json() == created_feedback

    patch_response = client.patch(
        f"/api/v1/feedback/{feedback_id}",
        json={
            "review_status": "needs_more_info",
            "developer_note": "Please add exact repro timing from a cold launch.",
        },
        headers=_actor_headers(developer.id),
    )
    assert patch_response.status_code == 200
    patched_feedback = patch_response.json()
    assert patched_feedback["id"] == feedback_id
    assert patched_feedback["task_id"] == task_id
    assert patched_feedback["rating"] == 4
    assert patched_feedback["note"] is None
    assert patched_feedback["review_status"] == "needs_more_info"
    assert (
        patched_feedback["developer_note"]
        == "Please add exact repro timing from a cold launch."
    )
    assert patched_feedback["resubmitted_at"] is None

    task_detail_response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers=_actor_headers(developer.id),
    )
    assert task_detail_response.status_code == 200
    assert task_detail_response.json()["status"] == "submitted"
    assert task_detail_response.json()["submitted_at"] is not None

    timeline_response = client.get(
        f"/api/v1/feedback/{feedback_id}/timeline",
        headers=_actor_headers(developer.id),
    )
    assert timeline_response.status_code == 200
    timeline_payload = timeline_response.json()
    assert timeline_payload["total"] == 2
    assert [item["event_type"] for item in timeline_payload["items"]] == [
        "feedback_needs_more_info",
        "feedback_submitted",
    ]

    delete_response = client.delete(f"/api/v1/feedback/{feedback_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""


def test_feedback_create_requires_existing_task(client: TestClient) -> None:
    tester = _create_tester_account()
    response = client.post(
        "/api/v1/tasks/task_missing/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
        },
        headers=_actor_headers(tester.id),
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "resource_not_found",
        "message": "Task not found.",
        "details": {
            "resource": "task",
            "id": "task_missing",
        },
    }


def test_feedback_patch_rejects_immutable_relation_updates(client: TestClient) -> None:
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
    feedback_response = client.post(
        f"/api/v1/tasks/{task_id}/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
        },
        headers=_actor_headers(tester.id),
    )
    feedback_id = feedback_response.json()["id"]

    response = client.patch(
        f"/api/v1/feedback/{feedback_id}",
        json={"task_id": "task_other"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "validation_error",
        "message": "Request validation failed.",
        "details": {
            "fields": [
                {
                    "field": "task_id",
                    "message": "Extra inputs are not permitted",
                }
            ]
        },
    }


def test_feedback_patch_rejects_invalid_review_status(client: TestClient) -> None:
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
    feedback_response = client.post(
        f"/api/v1/tasks/{task_id}/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
        },
        headers=_actor_headers(tester.id),
    )
    feedback_id = feedback_response.json()["id"]

    response = client.patch(
        f"/api/v1/feedback/{feedback_id}",
        json={"review_status": "triaged"},
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
    assert response.json()["message"] == "Request validation failed."


def test_feedback_patch_supports_resubmission_after_needs_more_info(client: TestClient) -> None:
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
    feedback_response = client.post(
        f"/api/v1/tasks/{task_id}/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
            "actual_result": "App exits immediately.",
        },
        headers=_actor_headers(tester.id),
    )
    feedback_id = feedback_response.json()["id"]

    review_request_response = client.patch(
        f"/api/v1/feedback/{feedback_id}",
        json={
            "review_status": "needs_more_info",
            "developer_note": "Please include the exact time between launch and crash.",
        },
        headers=_actor_headers(developer.id),
    )
    assert review_request_response.status_code == 200
    assert review_request_response.json()["review_status"] == "needs_more_info"
    assert review_request_response.json()["resubmitted_at"] is None

    resubmit_response = client.patch(
        f"/api/v1/feedback/{feedback_id}",
        json={
            "actual_result": "App exits immediately after three seconds on a cold launch.",
            "note": "Retested with screen recording enabled.",
        },
        headers=_actor_headers(tester.id),
    )

    assert resubmit_response.status_code == 200
    assert resubmit_response.json()["review_status"] == "submitted"
    assert (
        resubmit_response.json()["developer_note"]
        == "Please include the exact time between launch and crash."
    )
    assert (
        resubmit_response.json()["actual_result"]
        == "App exits immediately after three seconds on a cold launch."
    )
    assert resubmit_response.json()["resubmitted_at"] is not None


def test_feedback_queue_supports_mine_filter_for_developer_review(client: TestClient) -> None:
    developer_response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "Release Owner",
            "role": "developer",
        },
    )
    developer_id = developer_response.json()["id"]
    other_developer_response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "Other Developer",
            "role": "developer",
        },
    )
    other_developer_id = other_developer_response.json()["id"]
    tester_response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "QA Tester",
            "role": "tester",
        },
    )
    tester_id = tester_response.json()["id"]

    owned_project_response = client.post(
        "/api/v1/projects",
        headers={"X-Actor-Id": developer_id},
        json={"name": "HabitQuest"},
    )
    owned_project_id = owned_project_response.json()["id"]
    other_project_response = client.post(
        "/api/v1/projects",
        headers={"X-Actor-Id": other_developer_id},
        json={"name": "FocusFlow"},
    )
    other_project_id = other_project_response.json()["id"]

    owned_campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": owned_project_id,
            "name": "Owned Campaign",
            "target_platforms": ["ios"],
        },
        headers={"X-Actor-Id": developer_id},
    )
    owned_campaign_id = owned_campaign_response.json()["id"]
    other_campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": other_project_id,
            "name": "Other Campaign",
            "target_platforms": ["android"],
        },
        headers={"X-Actor-Id": other_developer_id},
    )
    other_campaign_id = other_campaign_response.json()["id"]

    device_profile_response = client.post(
        "/api/v1/device-profiles",
        headers={"X-Actor-Id": tester_id},
        json={
            "name": "QA iPhone 15",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
        },
    )
    device_profile_id = device_profile_response.json()["id"]

    owned_task_response = client.post(
        f"/api/v1/campaigns/{owned_campaign_id}/tasks",
        json={
            "title": "Validate owned onboarding",
            "device_profile_id": device_profile_id,
            "status": "submitted",
        },
        headers=_actor_headers(developer_id),
    )
    owned_task_id = owned_task_response.json()["id"]
    other_task_response = client.post(
        f"/api/v1/campaigns/{other_campaign_id}/tasks",
        json={
            "title": "Validate other onboarding",
            "device_profile_id": device_profile_id,
            "status": "submitted",
        },
        headers=_actor_headers(other_developer_id),
    )
    other_task_id = other_task_response.json()["id"]

    owned_feedback_response = client.post(
        f"/api/v1/tasks/{owned_task_id}/feedback",
        json={
            "summary": "Owned feedback",
            "severity": "high",
            "category": "bug",
        },
        headers=_actor_headers(tester_id),
    )
    owned_feedback = owned_feedback_response.json()
    client.post(
        f"/api/v1/tasks/{other_task_id}/feedback",
        json={
            "summary": "Other feedback",
            "severity": "medium",
            "category": "usability",
        },
        headers=_actor_headers(tester_id),
    )

    response = client.get(
        "/api/v1/feedback?mine=true&review_status=submitted",
        headers={"X-Actor-Id": developer_id},
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": owned_feedback["id"],
                "task_id": owned_task_id,
                "campaign_id": owned_campaign_id,
                "summary": "Owned feedback",
                "severity": "high",
                "category": "bug",
                "review_status": "submitted",
                "submitted_at": owned_feedback["submitted_at"],
            }
        ],
        "total": 1,
    }


def test_feedback_queue_requires_current_actor_header(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/feedback")

    assert response.status_code == 400
    assert response.json() == {
        "code": "missing_actor_context",
        "message": "Current actor is required.",
        "details": {
            "header": "X-Actor-Id",
        },
    }


def test_feedback_queue_scopes_results_for_tester_actor(client: TestClient) -> None:
    tester_response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "QA Tester",
            "role": "tester",
        },
    )
    tester_id = tester_response.json()["id"]
    other_tester_response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "Other QA Tester",
            "role": "tester",
        },
    )
    other_tester_id = other_tester_response.json()["id"]
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
    tester_device_profile = client.post(
        "/api/v1/device-profiles",
        headers=_actor_headers(tester_id),
        json={
            "name": "QA iPhone 15",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
        },
    ).json()
    other_tester_device_profile = client.post(
        "/api/v1/device-profiles",
        headers=_actor_headers(other_tester_id),
        json={
            "name": "Other QA iPhone 15",
            "platform": "ios",
            "device_model": "iPhone 15 Pro",
            "os_name": "iOS",
        },
    ).json()
    tester_task = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Tester task",
            "device_profile_id": tester_device_profile["id"],
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    ).json()
    other_tester_task = client.post(
        f"/api/v1/campaigns/{campaign_id}/tasks",
        json={
            "title": "Other tester task",
            "device_profile_id": other_tester_device_profile["id"],
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    ).json()
    tester_feedback = client.post(
        f"/api/v1/tasks/{tester_task['id']}/feedback",
        json={
            "summary": "Tester feedback",
            "severity": "high",
            "category": "bug",
        },
        headers=_actor_headers(tester_id),
    ).json()
    client.post(
        f"/api/v1/tasks/{other_tester_task['id']}/feedback",
        json={
            "summary": "Other tester feedback",
            "severity": "medium",
            "category": "usability",
        },
        headers=_actor_headers(other_tester_id),
    )

    response = client.get(
        "/api/v1/feedback",
        headers={"X-Actor-Id": tester_id},
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": tester_feedback["id"],
                "task_id": tester_task["id"],
                "campaign_id": campaign_id,
                "summary": "Tester feedback",
                "severity": "high",
                "category": "bug",
                "review_status": "submitted",
                "submitted_at": tester_feedback["submitted_at"],
            }
        ],
        "total": 1,
    }


def test_feedback_detail_requires_current_actor_header(client: TestClient) -> None:
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
        f"/api/v1/campaigns/{campaign_response.json()['id']}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": device_profile_response.json()["id"],
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )
    feedback_response = client.post(
        f"/api/v1/tasks/{task_response.json()['id']}/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
        },
        headers=_actor_headers(tester.id),
    )

    response = client.get(f"/api/v1/feedback/{feedback_response.json()['id']}")

    assert response.status_code == 400
    assert response.json() == {
        "code": "missing_actor_context",
        "message": "Current actor is required.",
        "details": {
            "header": "X-Actor-Id",
        },
    }


def test_feedback_detail_rejects_unowned_tester_read(client: TestClient) -> None:
    developer = _create_developer_account()
    tester = _create_tester_account()
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
    device_profile_response = client.post(
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
        f"/api/v1/campaigns/{campaign_response.json()['id']}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": device_profile_response.json()["id"],
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )
    feedback_response = client.post(
        f"/api/v1/tasks/{task_response.json()['id']}/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
        },
        headers=_actor_headers(other_tester.id),
    )

    response = client.get(
        f"/api/v1/feedback/{feedback_response.json()['id']}",
        headers=_actor_headers(tester.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "ownership_mismatch",
        "message": "Current actor does not own the target resource.",
        "details": {
            "actor_id": tester.id,
            "resource": "feedback",
            "ownership_anchor": {
                "resource": "device_profile",
                "id": device_profile_response.json()["id"],
                "owner_account_id": other_tester.id,
            },
        },
    }


def test_feedback_create_requires_current_actor_header(client: TestClient) -> None:
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
        f"/api/v1/campaigns/{campaign_response.json()['id']}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": device_profile_response.json()["id"],
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )

    response = client.post(
        f"/api/v1/tasks/{task_response.json()['id']}/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
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


def test_feedback_create_rejects_developer_actor(client: TestClient) -> None:
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
        f"/api/v1/campaigns/{campaign_response.json()['id']}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": device_profile_response.json()["id"],
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )

    response = client.post(
        f"/api/v1/tasks/{task_response.json()['id']}/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
        },
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "forbidden_actor_role",
        "message": "Tester role is required for this operation.",
        "details": {
            "actor_id": developer.id,
            "actor_role": "developer",
            "required_role": "tester",
        },
    }


def test_feedback_patch_rejects_tester_review_updates(client: TestClient) -> None:
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
        f"/api/v1/campaigns/{campaign_response.json()['id']}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": device_profile_response.json()["id"],
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )
    feedback_response = client.post(
        f"/api/v1/tasks/{task_response.json()['id']}/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
        },
        headers=_actor_headers(tester.id),
    )

    response = client.patch(
        f"/api/v1/feedback/{feedback_response.json()['id']}",
        json={"review_status": "reviewed"},
        headers=_actor_headers(tester.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "forbidden_actor_role",
        "message": "Developer role is required to review feedback.",
        "details": {
            "actor_id": tester.id,
            "actor_role": "tester",
            "required_role": "developer",
        },
    }


def test_feedback_patch_rejects_developer_content_updates(client: TestClient) -> None:
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
        f"/api/v1/campaigns/{campaign_response.json()['id']}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": device_profile_response.json()["id"],
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )
    feedback_response = client.post(
        f"/api/v1/tasks/{task_response.json()['id']}/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
        },
        headers=_actor_headers(tester.id),
    )

    response = client.patch(
        f"/api/v1/feedback/{feedback_response.json()['id']}",
        json={"summary": "Developer should not edit feedback content"},
        headers=_actor_headers(developer.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "forbidden_actor_role",
        "message": "Tester role is required to edit feedback content.",
        "details": {
            "actor_id": developer.id,
            "actor_role": "developer",
            "required_role": "tester",
        },
    }


def test_feedback_patch_rejects_tester_for_unowned_feedback(client: TestClient) -> None:
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
        f"/api/v1/campaigns/{campaign_response.json()['id']}/tasks",
        json={
            "title": "Validate onboarding flow",
            "device_profile_id": other_device_profile_response.json()["id"],
            "status": "assigned",
        },
        headers=_actor_headers(developer.id),
    )
    feedback_response = client.post(
        f"/api/v1/tasks/{task_response.json()['id']}/feedback",
        json={
            "summary": "App crashes on launch",
            "severity": "high",
            "category": "bug",
        },
        headers=_actor_headers(other_tester.id),
    )

    response = client.patch(
        f"/api/v1/feedback/{feedback_response.json()['id']}",
        json={"note": "This tester should not be able to edit this feedback."},
        headers=_actor_headers(tester.id),
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "ownership_mismatch",
        "message": "Current actor does not own the target resource.",
        "details": {
            "actor_id": tester.id,
            "resource": "feedback",
            "ownership_anchor": {
                "resource": "device_profile",
                "id": other_device_profile_response.json()["id"],
                "owner_account_id": other_tester.id,
            },
        },
    }
