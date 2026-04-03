from __future__ import annotations

from app.modules.campaigns.service import ensure_campaign_exists
from app.modules.device_profiles.service import ensure_device_profile_exists
from app.modules.feedback import repository as feedback_repository
from app.modules.reputation.schemas import (
    CampaignReputationSummary,
    DeviceProfileReputationSummary,
)
from app.modules.tasks import repository as task_repository
from app.modules.tasks.schemas import TaskStatus

_ASSIGNED_OR_LATER_STATUSES = {
    TaskStatus.ASSIGNED.value,
    TaskStatus.IN_PROGRESS.value,
    TaskStatus.SUBMITTED.value,
    TaskStatus.CLOSED.value,
}

_SUBMITTED_OR_CLOSED_STATUSES = {
    TaskStatus.SUBMITTED.value,
    TaskStatus.CLOSED.value,
}


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _latest_timestamp(values: list[str | None]) -> str | None:
    normalized_values = [value for value in values if value is not None]
    if not normalized_values:
        return None
    return max(normalized_values)


def get_device_profile_reputation(
    device_profile_id: str,
) -> DeviceProfileReputationSummary:
    device_profile = ensure_device_profile_exists(device_profile_id)

    tasks = task_repository.list_tasks(device_profile_id=device_profile_id)
    feedback_items = [
        item
        for item in feedback_repository.list_feedback()
        if item.device_profile_id == device_profile_id
    ]

    tasks_assigned_count = len(
        [task for task in tasks if task.status in _ASSIGNED_OR_LATER_STATUSES]
    )
    tasks_submitted_count = len(
        [
            task
            for task in tasks
            if task.status in _SUBMITTED_OR_CLOSED_STATUSES and task.submitted_at is not None
        ]
    )
    feedback_submitted_count = len(feedback_items)
    last_feedback_at = _latest_timestamp(
        [item.submitted_at for item in feedback_items]
    )
    updated_at = _latest_timestamp(
        [device_profile.updated_at]
        + [task.updated_at for task in tasks]
        + [item.updated_at for item in feedback_items]
    ) or device_profile.updated_at

    return DeviceProfileReputationSummary(
        device_profile_id=device_profile_id,
        tasks_assigned_count=tasks_assigned_count,
        tasks_submitted_count=tasks_submitted_count,
        feedback_submitted_count=feedback_submitted_count,
        submission_rate=_safe_rate(tasks_submitted_count, tasks_assigned_count),
        last_feedback_at=last_feedback_at,
        updated_at=updated_at,
    )


def get_campaign_reputation(campaign_id: str) -> CampaignReputationSummary:
    campaign = ensure_campaign_exists(campaign_id)

    tasks = task_repository.list_tasks(campaign_id=campaign_id)
    feedback_items = [
        item for item in feedback_repository.list_feedback() if item.campaign_id == campaign_id
    ]

    tasks_total_count = len(tasks)
    tasks_closed_count = len(
        [task for task in tasks if task.status == TaskStatus.CLOSED.value]
    )
    feedback_received_count = len(feedback_items)
    last_feedback_at = _latest_timestamp(
        [item.submitted_at for item in feedback_items]
    )
    updated_at = _latest_timestamp(
        [campaign.updated_at]
        + [task.updated_at for task in tasks]
        + [item.updated_at for item in feedback_items]
    ) or campaign.updated_at

    return CampaignReputationSummary(
        campaign_id=campaign_id,
        tasks_total_count=tasks_total_count,
        tasks_closed_count=tasks_closed_count,
        feedback_received_count=feedback_received_count,
        closure_rate=_safe_rate(tasks_closed_count, tasks_total_count),
        last_feedback_at=last_feedback_at,
        updated_at=updated_at,
    )
