from __future__ import annotations

from fastapi.testclient import TestClient


def test_accounts_crud_flow_returns_expected_shapes(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "Alice QA",
            "role": "tester",
            "bio": "Mobile web tester",
            "locale": "zh-TW",
        },
    )

    assert create_response.status_code == 201
    created_account = create_response.json()
    account_id = created_account["id"]

    assert created_account["display_name"] == "Alice QA"
    assert created_account["role"] == "tester"
    assert created_account["roles"] == ["tester"]
    assert created_account["created_at"]
    assert created_account["updated_at"]

    list_response = client.get("/api/v1/accounts")

    assert list_response.status_code == 200
    assert list_response.json() == {
        "items": [
            {
                "id": account_id,
                "display_name": "Alice QA",
                "role": "tester",
                "roles": ["tester"],
                "updated_at": created_account["updated_at"],
            }
        ],
        "total": 1,
    }

    detail_response = client.get(
        f"/api/v1/accounts/{account_id}",
        headers={"X-Actor-Id": account_id},
    )

    assert detail_response.status_code == 200
    assert detail_response.json() == created_account

    patch_response = client.patch(
        f"/api/v1/accounts/{account_id}",
        json={
            "display_name": "Alice Mobile QA",
            "bio": "Updated tester bio",
        },
    )

    assert patch_response.status_code == 200
    patched_account = patch_response.json()
    assert patched_account["id"] == account_id
    assert patched_account["display_name"] == "Alice Mobile QA"
    assert patched_account["bio"] == "Updated tester bio"

    delete_response = client.delete(f"/api/v1/accounts/{account_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    missing_response = client.get(
        f"/api/v1/accounts/{account_id}",
        headers={"X-Actor-Id": account_id},
    )

    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "code": "resource_not_found",
        "message": "Account not found.",
        "details": {
            "resource": "account",
            "id": account_id,
        },
    }


def test_account_patch_rejects_unknown_fields(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "Builder",
            "role": "developer",
        },
    )
    account_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/accounts/{account_id}",
        json={"unknown_field": "x"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "validation_error",
        "message": "Request validation failed.",
        "details": {
            "fields": [
                {
                    "field": "unknown_field",
                    "message": "Extra inputs are not permitted",
                }
            ]
        },
    }


def test_accounts_create_accepts_dual_roles(client: TestClient) -> None:
    response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "Dual Role User",
            "role": "developer",
            "roles": ["developer", "tester"],
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "developer"
    assert response.json()["roles"] == ["developer", "tester"]


def test_account_summary_returns_developer_owned_resource_counts(client: TestClient) -> None:
    developer_response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "Build Owner",
            "role": "developer",
        },
    )
    developer = developer_response.json()

    project_response = client.post(
        "/api/v1/projects",
        json={
            "name": "Owned Project",
        },
        headers={"X-Actor-Id": developer["id"]},
    )
    project = project_response.json()

    campaign_response = client.post(
        "/api/v1/campaigns",
        json={
            "project_id": project["id"],
            "name": "Owned Campaign",
            "target_platforms": ["ios"],
        },
        headers={"X-Actor-Id": developer["id"]},
    )
    campaign = campaign_response.json()

    summary_response = client.get(
        f"/api/v1/accounts/{developer['id']}/summary",
        headers={"X-Actor-Id": developer["id"]},
    )

    assert summary_response.status_code == 200
    assert summary_response.json() == {
        "account_id": developer["id"],
        "role": "developer",
        "roles": ["developer"],
        "developer_summary": {
            "owned_projects_count": 1,
            "owned_campaigns_count": 1,
            "feedback_to_review_count": 0,
            "recent_projects": [
                {
                    "id": project["id"],
                    "name": "Owned Project",
                    "updated_at": project["updated_at"],
                }
            ],
            "recent_campaigns": [
                {
                    "id": campaign["id"],
                    "project_id": project["id"],
                    "name": "Owned Campaign",
                    "status": "draft",
                    "updated_at": campaign["updated_at"],
                }
            ],
        },
        "tester_summary": None,
        "updated_at": campaign["updated_at"],
    }


def test_account_summary_returns_tester_zero_state_without_owned_resources(
    client: TestClient,
) -> None:
    tester_response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "Zero Tester",
            "role": "tester",
        },
    )
    tester = tester_response.json()

    summary_response = client.get(
        f"/api/v1/accounts/{tester['id']}/summary",
        headers={"X-Actor-Id": tester["id"]},
    )

    assert summary_response.status_code == 200
    assert summary_response.json() == {
        "account_id": tester["id"],
        "role": "tester",
        "roles": ["tester"],
        "developer_summary": None,
        "tester_summary": {
            "owned_device_profiles_count": 0,
            "assigned_tasks_count": 0,
            "submitted_feedback_count": 0,
            "recent_device_profiles": [],
            "recent_tasks": [],
            "recent_feedback": [],
        },
        "updated_at": tester["updated_at"],
    }


def test_account_summary_returns_not_found_for_missing_account(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/accounts/acct_missing/summary",
        headers={"X-Actor-Id": "acct_missing"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "resource_not_found",
        "message": "Account not found.",
        "details": {
            "resource": "account",
            "id": "acct_missing",
        },
    }


def test_account_detail_requires_current_actor_header(client: TestClient) -> None:
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "Alice QA",
            "role": "tester",
        },
    )
    account_id = account_response.json()["id"]

    response = client.get(f"/api/v1/accounts/{account_id}")

    assert response.status_code == 400
    assert response.json() == {
        "code": "missing_actor_context",
        "message": "Current actor is required.",
        "details": {
            "header": "X-Actor-Id",
        },
    }


def test_account_summary_rejects_other_actor_read(client: TestClient) -> None:
    target_response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "Alice QA",
            "role": "tester",
        },
    )
    actor_response = client.post(
        "/api/v1/accounts",
        json={
            "display_name": "Build Owner",
            "role": "developer",
        },
    )
    target_id = target_response.json()["id"]
    actor_id = actor_response.json()["id"]

    response = client.get(
        f"/api/v1/accounts/{target_id}/summary",
        headers={"X-Actor-Id": actor_id},
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "ownership_mismatch",
        "message": "Current actor does not own the target resource.",
        "details": {
            "actor_id": actor_id,
            "resource": "account",
            "ownership_anchor": {
                "resource": "account",
                "id": target_id,
                "owner_account_id": target_id,
            },
        },
    }
