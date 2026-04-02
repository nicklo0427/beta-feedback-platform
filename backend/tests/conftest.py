from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.campaigns.repository import clear_campaigns
from app.modules.projects.repository import clear_projects


@pytest.fixture(autouse=True)
def clear_in_memory_state() -> Generator[None, None, None]:
    # Keep the in-memory repositories isolated between tests.
    clear_campaigns()
    clear_projects()
    yield
    clear_campaigns()
    clear_projects()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
