from __future__ import annotations

from fastapi import status

from app.common.exceptions import AppError
from app.modules.accounts.capabilities import account_has_role, raise_forbidden_actor_role
from app.modules.accounts.schemas import AccountRole
from app.modules.accounts.service import ensure_account_exists
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


def _raise_ownership_mismatch(
    actor_id: str,
    resource: str,
    ownership_anchor: dict[str, str | None],
) -> None:
    raise AppError(
        status_code=status.HTTP_409_CONFLICT,
        code="ownership_mismatch",
        message="Current actor does not own the target resource.",
        details={
            "actor_id": actor_id,
            "resource": resource,
            "ownership_anchor": ownership_anchor,
        },
    )


def _ensure_current_actor(current_actor_id: str | None) -> str:
    if current_actor_id is None:
        raise AppError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="missing_actor_context",
            message="Current actor is required.",
            details={
                "header": "X-Actor-Id",
            },
        )

    return current_actor_id


def _ensure_campaign_reputation_read_visibility(
    campaign_id: str,
    current_actor_id: str | None,
) -> None:
    from app.modules.campaigns.service import ensure_campaign_owned_by_actor
    from app.modules.device_profiles import repository as device_profiles_repository
    from app.modules.eligibility.schemas import QualificationStatus
    from app.modules.eligibility.service import (
        evaluate_campaign_device_profile_qualification,
    )
    from app.modules.participation_requests import (
        repository as participation_requests_repository,
    )

    actor_id = _ensure_current_actor(current_actor_id)
    actor = ensure_account_exists(actor_id)

    developer_error: AppError | None = None
    if account_has_role(actor, AccountRole.DEVELOPER):
        try:
            ensure_campaign_owned_by_actor(
                campaign_id,
                actor.id,
                resource="campaign_reputation",
            )
            return
        except AppError as error:
            if error.code != "ownership_mismatch":
                raise
            developer_error = error

    if not account_has_role(actor, AccountRole.TESTER):
        if developer_error is not None:
            raise developer_error
        raise_forbidden_actor_role(
            actor,
            AccountRole.TESTER,
            "Developer or tester role is required to read campaign reputation.",
        )

    owned_device_profiles = [
        record
        for record in device_profiles_repository.list_device_profiles()
        if record.owner_account_id == actor.id
    ]
    owned_device_profile_ids = {record.id for record in owned_device_profiles}

    if any(
        task.campaign_id == campaign_id and task.device_profile_id in owned_device_profile_ids
        for task in task_repository.list_tasks()
    ):
        return

    if any(
        item.campaign_id == campaign_id and item.device_profile_id in owned_device_profile_ids
        for item in feedback_repository.list_feedback()
    ):
        return

    if any(
        record.campaign_id == campaign_id and record.device_profile_id in owned_device_profile_ids
        for record in participation_requests_repository.list_participation_requests()
    ):
        return

    for device_profile in owned_device_profiles:
        qualification = evaluate_campaign_device_profile_qualification(
            campaign_id,
            device_profile,
        )
        if qualification.qualification_status == QualificationStatus.QUALIFIED.value:
            return

    _raise_ownership_mismatch(
        actor.id,
        "campaign_reputation",
        {
            "resource": "campaign",
            "id": campaign_id,
            "owner_account_id": None,
        },
    )


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


def get_campaign_reputation_for_actor(
    campaign_id: str,
    current_actor_id: str | None,
) -> CampaignReputationSummary:
    _ensure_campaign_reputation_read_visibility(campaign_id, current_actor_id)
    return get_campaign_reputation(campaign_id)
