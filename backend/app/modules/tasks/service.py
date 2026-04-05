from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import status

from app.common.exceptions import AppError
from app.common.responses import build_list_response
from app.modules.accounts.schemas import AccountRole
from app.modules.accounts.service import ensure_account_exists
from app.modules.tasks import repository
from app.modules.tasks.models import TaskRecord
from app.modules.tasks.schemas import (
    TaskCreate,
    TaskDetail,
    TaskListItem,
    TaskListResponse,
    TaskStatus,
    TaskUpdate,
)

_TASKS_REQUIRING_ASSIGNMENT = {
    TaskStatus.ASSIGNED.value,
    TaskStatus.IN_PROGRESS.value,
    TaskStatus.SUBMITTED.value,
    TaskStatus.CLOSED.value,
}

_ALLOWED_STATUS_TRANSITIONS: dict[str, set[str]] = {
    TaskStatus.DRAFT.value: {TaskStatus.DRAFT.value, TaskStatus.OPEN.value, TaskStatus.CLOSED.value},
    TaskStatus.OPEN.value: {TaskStatus.OPEN.value, TaskStatus.ASSIGNED.value, TaskStatus.CLOSED.value},
    TaskStatus.ASSIGNED.value: {
        TaskStatus.ASSIGNED.value,
        TaskStatus.IN_PROGRESS.value,
        TaskStatus.CLOSED.value,
    },
    TaskStatus.IN_PROGRESS.value: {
        TaskStatus.IN_PROGRESS.value,
        TaskStatus.SUBMITTED.value,
        TaskStatus.CLOSED.value,
    },
    TaskStatus.SUBMITTED.value: {TaskStatus.SUBMITTED.value, TaskStatus.CLOSED.value},
    TaskStatus.CLOSED.value: {TaskStatus.CLOSED.value},
}

_TESTER_MUTATION_ALLOWED_STATUSES = {
    TaskStatus.IN_PROGRESS.value,
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _generate_task_id() -> str:
    return f"task_{uuid4().hex[:12]}"


def _to_task_detail(record: TaskRecord) -> TaskDetail:
    return TaskDetail.model_validate(asdict(record))


def _to_task_list_item(record: TaskRecord) -> TaskListItem:
    return TaskListItem.model_validate(asdict(record))


def _status_value(status_value: Optional[TaskStatus], *, default: str) -> str:
    if status_value is None:
        return default
    return status_value.value


def _validate_status_transition(current_status: str, next_status: str) -> None:
    if next_status not in _ALLOWED_STATUS_TRANSITIONS[current_status]:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="conflict",
            message="Task status transition is not allowed.",
            details={
                "resource": "task",
                "current_status": current_status,
                "next_status": next_status,
            },
        )


def _raise_forbidden_actor_role(
    *,
    actor_id: str,
    actor_role: str,
    required_role: str,
    message: str,
) -> None:
    raise AppError(
        status_code=status.HTTP_409_CONFLICT,
        code="forbidden_actor_role",
        message=message,
        details={
            "actor_id": actor_id,
            "actor_role": actor_role,
            "required_role": required_role,
        },
    )


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


def _ensure_tester_actor(current_actor_id: str | None):
    if current_actor_id is None:
        return None

    actor = ensure_account_exists(current_actor_id)
    if actor.role != AccountRole.TESTER.value:
        _raise_forbidden_actor_role(
            actor_id=actor.id,
            actor_role=actor.role,
            required_role=AccountRole.TESTER.value,
            message="Tester role is required for this operation.",
        )

    return actor


def _ensure_assignment_requirements(
    *,
    next_status: str,
    device_profile_id: Optional[str],
) -> None:
    if next_status in _TASKS_REQUIRING_ASSIGNMENT and device_profile_id is None:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="conflict",
            message="Task requires a device profile before entering this status.",
            details={
                "resource": "task",
                "status": next_status,
            },
        )


def ensure_task_exists(task_id: str) -> TaskRecord:
    record = repository.get_task(task_id)
    if record is None:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="resource_not_found",
            message="Task not found.",
            details={
                "resource": "task",
                "id": task_id,
            },
        )

    return record


def has_tasks_for_campaign(campaign_id: str) -> bool:
    return repository.has_tasks_for_campaign(campaign_id)


def has_tasks_for_device_profile(device_profile_id: str) -> bool:
    return repository.has_tasks_for_device_profile(device_profile_id)


def _resolve_owned_device_profile_ids_for_actor(current_actor_id: str) -> set[str]:
    from app.modules.device_profiles import repository as device_profiles_repository

    ensure_account_exists(current_actor_id)

    return {
        record.id
        for record in device_profiles_repository.list_device_profiles()
        if record.owner_account_id == current_actor_id
    }


def ensure_task_owned_by_developer(
    task_id: str,
    current_actor_id: str | None,
    resource: str = "task",
) -> TaskRecord:
    from app.modules.campaigns.service import ensure_campaign_owned_by_actor

    task = ensure_task_exists(task_id)
    ensure_campaign_owned_by_actor(
        task.campaign_id,
        current_actor_id,
        resource=resource,
    )
    return task


def ensure_task_owned_by_tester(
    task_id: str,
    current_actor_id: str | None,
    resource: str = "task",
) -> TaskRecord:
    from app.modules.device_profiles.service import ensure_device_profile_exists

    actor = _ensure_tester_actor(current_actor_id)
    task = ensure_task_exists(task_id)

    if actor is None:
        return task

    if task.device_profile_id is None:
        _raise_ownership_mismatch(
            actor.id,
            resource,
            {
                "resource": "device_profile",
                "id": None,
                "owner_account_id": None,
            },
        )

    device_profile = ensure_device_profile_exists(task.device_profile_id)
    if device_profile.owner_account_id != actor.id:
        _raise_ownership_mismatch(
            actor.id,
            resource,
            {
                "resource": "device_profile",
                "id": device_profile.id,
                "owner_account_id": device_profile.owner_account_id,
            },
        )

    return task


def _guard_task_update_for_actor(
    current: TaskRecord,
    payload: TaskUpdate,
    current_actor_id: str | None,
) -> TaskRecord:
    if current_actor_id is None:
        return current

    actor = ensure_account_exists(current_actor_id)
    if actor.role == AccountRole.DEVELOPER.value:
        return ensure_task_owned_by_developer(
            current.id,
            current_actor_id,
            resource="task",
        )

    if actor.role != AccountRole.TESTER.value:
        _raise_forbidden_actor_role(
            actor_id=actor.id,
            actor_role=actor.role,
            required_role=AccountRole.DEVELOPER.value,
            message="Developer role is required for this operation.",
        )

    owned_task = ensure_task_owned_by_tester(
        current.id,
        current_actor_id,
        resource="task",
    )
    next_status = _status_value(
        payload.status,
        default=current.status,
    )

    if (
        payload.model_fields_set != {"status"}
        or current.status != TaskStatus.ASSIGNED.value
        or next_status not in _TESTER_MUTATION_ALLOWED_STATUSES
    ):
        _raise_forbidden_actor_role(
            actor_id=actor.id,
            actor_role=actor.role,
            required_role=AccountRole.DEVELOPER.value,
            message="Tester can only start assigned tasks they own.",
        )

    return owned_task


def list_tasks(
    *,
    campaign_id: Optional[str] = None,
    device_profile_id: Optional[str] = None,
    status_filter: Optional[TaskStatus] = None,
    mine: bool = False,
    current_actor_id: Optional[str] = None,
) -> TaskListResponse:
    records = repository.list_tasks(
        campaign_id=campaign_id,
        device_profile_id=device_profile_id,
        status=status_filter.value if status_filter is not None else None,
    )

    if mine:
        if current_actor_id is None:
            raise AppError(
                status_code=status.HTTP_400_BAD_REQUEST,
                code="missing_actor_context",
                message="Current actor is required.",
                details={
                    "header": "X-Actor-Id",
                },
            )

        owned_device_profile_ids = _resolve_owned_device_profile_ids_for_actor(
            current_actor_id
        )
        records = [
            record
            for record in records
            if record.device_profile_id in owned_device_profile_ids
        ]

    items = [
        _to_task_list_item(record)
        for record in records
    ]
    return TaskListResponse.model_validate(build_list_response(items))


def get_task(task_id: str) -> TaskDetail:
    return _to_task_detail(ensure_task_exists(task_id))


def create_task(
    campaign_id: str,
    payload: TaskCreate,
    current_actor_id: str | None = None,
) -> TaskDetail:
    from app.modules.campaigns.service import ensure_campaign_owned_by_actor
    from app.modules.device_profiles.service import ensure_device_profile_exists

    ensure_campaign_owned_by_actor(
        campaign_id,
        current_actor_id,
        resource="task",
    )

    if payload.device_profile_id is not None:
        ensure_device_profile_exists(payload.device_profile_id)

    next_status = _status_value(payload.status, default=TaskStatus.DRAFT.value)
    _ensure_assignment_requirements(
        next_status=next_status,
        device_profile_id=payload.device_profile_id,
    )

    timestamp = _utc_now_iso()
    record = TaskRecord(
        id=_generate_task_id(),
        campaign_id=campaign_id,
        device_profile_id=payload.device_profile_id,
        title=payload.title,
        instruction_summary=payload.instruction_summary,
        status=next_status,
        submitted_at=timestamp if next_status == TaskStatus.SUBMITTED.value else None,
        created_at=timestamp,
        updated_at=timestamp,
    )
    repository.create_task(record)
    return _to_task_detail(record)


def update_task(
    task_id: str,
    payload: TaskUpdate,
    current_actor_id: str | None = None,
) -> TaskDetail:
    from app.modules.device_profiles.service import ensure_device_profile_exists

    current = ensure_task_exists(task_id)
    current = _guard_task_update_for_actor(current, payload, current_actor_id)

    next_device_profile_id = (
        payload.device_profile_id
        if "device_profile_id" in payload.model_fields_set
        else current.device_profile_id
    )
    next_title = payload.title if "title" in payload.model_fields_set else current.title
    next_instruction_summary = (
        payload.instruction_summary
        if "instruction_summary" in payload.model_fields_set
        else current.instruction_summary
    )
    next_status = _status_value(
        payload.status,
        default=current.status,
    )

    _validate_status_transition(current.status, next_status)

    if next_device_profile_id is not None:
        ensure_device_profile_exists(next_device_profile_id)

    _ensure_assignment_requirements(
        next_status=next_status,
        device_profile_id=next_device_profile_id,
    )

    submitted_at = current.submitted_at
    if current.status != TaskStatus.SUBMITTED.value and next_status == TaskStatus.SUBMITTED.value:
        submitted_at = _utc_now_iso()

    updated = replace(
        current,
        device_profile_id=next_device_profile_id,
        title=next_title,
        instruction_summary=next_instruction_summary,
        status=next_status,
        submitted_at=submitted_at,
        updated_at=_utc_now_iso(),
    )
    repository.update_task(updated)
    return _to_task_detail(updated)


def delete_task(task_id: str) -> None:
    ensure_task_exists(task_id)

    from app.modules.feedback.service import has_feedback_for_task

    if has_feedback_for_task(task_id):
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="conflict",
            message="Task cannot be deleted while feedback exists.",
            details={
                "resource": "task",
                "id": task_id,
                "related_resource": "feedback",
            },
        )

    repository.delete_task(task_id)
