from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import clear_settings_cache
from app.db.session import ensure_database_ready, reset_database_runtime
from app.main import app
from app.modules.accounts.repository import clear_accounts
from app.modules.auth.repository import clear_sessions
from app.modules.campaigns.repository import clear_campaigns
from app.modules.device_profiles.repository import clear_device_profiles
from app.modules.eligibility.repository import clear_eligibility_rules
from app.modules.feedback.repository import clear_feedback
from app.modules.participation_requests.repository import clear_participation_requests
from app.modules.projects.repository import clear_projects
from app.modules.safety.repository import clear_campaign_safety_profiles
from app.modules.tasks.repository import clear_tasks


def sqlite_database_url(database_path: Path) -> str:
    return f"sqlite+pysqlite:////{database_path.as_posix().lstrip('/')}"


@pytest.fixture
def persistent_database(tmp_path, monkeypatch) -> Generator[str, None, None]:
    database_path = tmp_path / "bfp-persistence.sqlite3"
    monkeypatch.setenv("BFP_DATABASE_URL", sqlite_database_url(database_path))
    clear_settings_cache()
    reset_database_runtime()

    yield str(database_path)

    ensure_database_ready()
    clear_sessions()
    clear_feedback()
    clear_tasks()
    clear_participation_requests()
    clear_eligibility_rules()
    clear_campaign_safety_profiles()
    clear_campaigns()
    clear_device_profiles()
    clear_projects()
    clear_accounts()
    reset_database_runtime()
    clear_settings_cache()


def test_alembic_upgrade_command_creates_core_tables(
    persistent_database: str,
) -> None:
    backend_root = Path(__file__).resolve().parents[1]
    env = {
        **os.environ,
        "BFP_DATABASE_URL": sqlite_database_url(Path(persistent_database)),
        "PYTHONPATH": str(backend_root),
    }
    command_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            str(backend_root / "alembic.ini"),
            "upgrade",
            "head",
        ],
        cwd=backend_root,
        env=env,
        capture_output=True,
        text=True,
    )

    assert command_result.returncode == 0, command_result.stderr

    connection = sqlite3.connect(persistent_database)
    try:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    finally:
        connection.close()

    table_names = {row[0] for row in rows}
    assert {
        "accounts",
        "actor_sessions",
        "projects",
        "campaigns",
        "campaign_safety",
        "eligibility_rules",
        "device_profiles",
        "tasks",
        "feedback",
        "participation_requests",
    }.issubset(table_names)


def test_persistence_mode_keeps_core_flow_data_after_runtime_reset(
    persistent_database: str,
) -> None:
    with TestClient(app) as client:
        developer_response = client.post(
            "/api/v1/accounts",
            json={"display_name": "Dev Owner", "role": "developer"},
        )
        tester_response = client.post(
            "/api/v1/accounts",
            json={"display_name": "QA Tester", "role": "tester"},
        )
        developer_id = developer_response.json()["id"]
        tester_id = tester_response.json()["id"]

        project_response = client.post(
            "/api/v1/projects",
            headers={"X-Actor-Id": developer_id},
            json={"name": "HabitQuest"},
        )
        project_id = project_response.json()["id"]

        campaign_response = client.post(
            "/api/v1/campaigns",
            headers={"X-Actor-Id": developer_id},
            json={
                "project_id": project_id,
                "name": "Closed Beta Round 1",
                "target_platforms": ["ios"],
            },
        )
        campaign_id = campaign_response.json()["id"]

        safety_response = client.post(
            f"/api/v1/campaigns/{campaign_id}/safety",
            headers={"X-Actor-Id": developer_id},
            json={
                "distribution_channel": "testflight",
                "source_label": "TestFlight",
                "risk_level": "low",
            },
        )
        safety_id = safety_response.json()["id"]

        eligibility_response = client.post(
            f"/api/v1/campaigns/{campaign_id}/eligibility-rules",
            headers={"X-Actor-Id": developer_id},
            json={
                "platform": "ios",
                "os_name": "iOS",
                "install_channel": "testflight",
            },
        )
        eligibility_rule_id = eligibility_response.json()["id"]

        device_profile_response = client.post(
            "/api/v1/device-profiles",
            headers={"X-Actor-Id": tester_id},
            json={
                "name": "QA iPhone 15",
                "platform": "ios",
                "device_model": "iPhone 15 Pro",
                "os_name": "iOS",
                "install_channel": "testflight",
                "os_version": "17.4",
            },
        )
        device_profile_id = device_profile_response.json()["id"]

        request_response = client.post(
            f"/api/v1/campaigns/{campaign_id}/participation-requests",
            headers={"X-Actor-Id": tester_id},
            json={"device_profile_id": device_profile_id},
        )
        request_id = request_response.json()["id"]

        accepted_request_response = client.patch(
            f"/api/v1/participation-requests/{request_id}",
            headers={"X-Actor-Id": developer_id},
            json={"status": "accepted"},
        )
        assert accepted_request_response.status_code == 200

        task_response = client.post(
            f"/api/v1/participation-requests/{request_id}/tasks",
            headers={"X-Actor-Id": developer_id},
            json={
                "title": "Validate onboarding flow",
                "status": "assigned",
            },
        )
        task_id = task_response.json()["id"]

        feedback_response = client.post(
            f"/api/v1/tasks/{task_id}/feedback",
            headers={"X-Actor-Id": tester_id},
            json={
                "summary": "App crashes on launch",
                "severity": "high",
                "category": "bug",
            },
        )
        feedback_id = feedback_response.json()["id"]

    reset_database_runtime()
    clear_settings_cache()
    ensure_database_ready()

    with TestClient(app) as restarted_client:
        assert (
            restarted_client.get(
                f"/api/v1/accounts/{developer_id}",
                headers={"X-Actor-Id": developer_id},
            ).status_code
            == 200
        )
        assert restarted_client.get(f"/api/v1/projects/{project_id}").status_code == 200
        assert restarted_client.get(f"/api/v1/campaigns/{campaign_id}").status_code == 200
        assert (
            restarted_client.get(
                f"/api/v1/campaigns/{campaign_id}/safety",
                headers={"X-Actor-Id": developer_id},
            ).json()["id"]
            == safety_id
        )
        assert (
            restarted_client.get(
                f"/api/v1/eligibility-rules/{eligibility_rule_id}",
                headers={"X-Actor-Id": developer_id},
            ).status_code
            == 200
        )
        assert (
            restarted_client.get(f"/api/v1/device-profiles/{device_profile_id}").status_code
            == 200
        )
        assert (
            restarted_client.get(
                f"/api/v1/participation-requests/{request_id}",
                headers={"X-Actor-Id": developer_id},
            ).status_code
            == 200
        )
        assert (
            restarted_client.get(
                f"/api/v1/tasks/{task_id}",
                headers={"X-Actor-Id": developer_id},
            ).status_code
            == 200
        )
        assert (
            restarted_client.get(
                f"/api/v1/feedback/{feedback_id}",
                headers={"X-Actor-Id": tester_id},
            ).status_code
            == 200
        )
