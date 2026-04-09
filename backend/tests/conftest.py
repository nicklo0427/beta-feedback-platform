from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.accounts.repository import clear_accounts
from app.modules.campaigns.repository import clear_campaigns
from app.modules.device_profiles.repository import clear_device_profiles
from app.modules.eligibility.repository import clear_eligibility_rules
from app.modules.feedback.repository import clear_feedback
from app.modules.participation_requests.repository import clear_participation_requests
from app.modules.projects.repository import clear_projects
from app.modules.safety.repository import clear_campaign_safety_profiles
from app.modules.tasks.repository import clear_tasks


@pytest.fixture(autouse=True)
def clear_in_memory_state() -> Generator[None, None, None]:
    # Keep the in-memory repositories isolated between tests.
    clear_accounts()
    clear_campaigns()
    clear_device_profiles()
    clear_eligibility_rules()
    clear_feedback()
    clear_participation_requests()
    clear_projects()
    clear_campaign_safety_profiles()
    clear_tasks()
    yield
    clear_accounts()
    clear_campaigns()
    clear_device_profiles()
    clear_eligibility_rules()
    clear_feedback()
    clear_participation_requests()
    clear_projects()
    clear_campaign_safety_profiles()
    clear_tasks()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
