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
from app.modules.activity_events.schemas import ActivityEntityType, ActivityEventType
from app.modules.activity_events.service import record_activity_event
from app.modules.tasks import repository
from app.modules.tasks.models import TaskRecord
from app.modules.tasks.schemas import (
    TaskCreate,
    TaskDetail,
    TaskListItem,
    TaskListResponse,
    TaskParticipationRequestContext,
    TaskQualificationContext,
    TaskResolutionContext,
    TaskResolutionOutcome,
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

_TASK_RESOLUTION_OUTCOME_SUMMARIES: dict[str, str] = {
    TaskResolutionOutcome.CONFIRMED_ISSUE.value: "確認問題",
    TaskResolutionOutcome.NEEDS_FOLLOW_UP.value: "需要後續追蹤",
    TaskResolutionOutcome.NOT_REPRODUCIBLE.value: "無法重現",
    TaskResolutionOutcome.CANCELLED.value: "取消處理",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _generate_task_id() -> str:
    return f"task_{uuid4().hex[:12]}"


def _summarize_task_resolution_outcome(outcome: str | None) -> str:
    if outcome is None:
        return "記錄任務處理結果。"
    return f"記錄任務處理結果：{_TASK_RESOLUTION_OUTCOME_SUMMARIES.get(outcome, outcome)}。"


def _build_task_qualification_context(
    record: TaskRecord,
) -> TaskQualificationContext | None:
    if record.device_profile_id is None:
        return None

    from app.modules.device_profiles.service import ensure_device_profile_exists
    from app.modules.eligibility.service import (
        evaluate_campaign_device_profile_qualification,
    )
    from app.modules.eligibility.schemas import QualificationStatus

    device_profile = ensure_device_profile_exists(record.device_profile_id)
    qualification_result = evaluate_campaign_device_profile_qualification(
        record.campaign_id,
        device_profile,
    )

    return TaskQualificationContext.model_validate(
        {
            "device_profile_id": qualification_result.device_profile_id,
            "device_profile_name": qualification_result.device_profile_name,
            "qualification_status": qualification_result.qualification_status,
            "matched_rule_id": qualification_result.matched_rule_id,
            "reason_summary": qualification_result.reason_summary,
            "qualification_drift": (
                qualification_result.qualification_status
                != QualificationStatus.QUALIFIED.value
            ),
        }
    )


def _build_task_participation_request_context(
    record: TaskRecord,
) -> TaskParticipationRequestContext | None:
    from app.modules.accounts.service import get_account
    from app.modules.participation_requests import (
        repository as participation_requests_repository,
    )

    linked_request = next(
        (
            request_record
            for request_record in participation_requests_repository.list_participation_requests()
            if request_record.linked_task_id == record.id
        ),
        None,
    )

    if linked_request is None:
        return None

    tester_account = get_account(linked_request.tester_account_id)

    return TaskParticipationRequestContext.model_validate(
        {
            "request_id": linked_request.id,
            "request_status": linked_request.status,
            "tester_account_id": linked_request.tester_account_id,
            "tester_account_display_name": tester_account.display_name,
            "assignment_created_at": linked_request.assignment_created_at,
        }
    )


def _build_task_resolution_context(
    record: TaskRecord,
) -> TaskResolutionContext | None:
    from app.modules.accounts.service import get_account

    if record.resolution_outcome is None or record.resolved_at is None or record.resolved_by_account_id is None:
        return None

    resolved_by_account = get_account(record.resolved_by_account_id)
    return TaskResolutionContext.model_validate(
        {
            "resolution_outcome": record.resolution_outcome,
            "resolution_note": record.resolution_note,
            "resolved_at": record.resolved_at,
            "resolved_by_account_id": record.resolved_by_account_id,
            "resolved_by_account_display_name": resolved_by_account.display_name,
        }
    )


def _ensure_task_read_visibility(
    task: TaskRecord,
    current_actor_id: str | None,
) -> TaskRecord:
    if current_actor_id is None:
        raise AppError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="missing_actor_context",
            message="Current actor is required.",
            details={
                "header": "X-Actor-Id",
            },
        )

    actor = ensure_account_exists(current_actor_id)
    if actor.role == AccountRole.DEVELOPER.value:
        return ensure_task_owned_by_developer(
            task.id,
            current_actor_id,
            resource="task",
        )

    if actor.role == AccountRole.TESTER.value:
        return ensure_task_owned_by_tester(
            task.id,
            current_actor_id,
            resource="task",
        )

    _raise_forbidden_actor_role(
        actor_id=actor.id,
        actor_role=actor.role,
        required_role=AccountRole.DEVELOPER.value,
        message="Developer or tester role is required to view this task.",
    )
    return task


def _to_task_detail(record: TaskRecord) -> TaskDetail:
    payload = asdict(record)
    qualification_context = _build_task_qualification_context(record)
    if qualification_context is not None:
        payload["qualification_context"] = qualification_context.model_dump()
    participation_request_context = _build_task_participation_request_context(record)
    if participation_request_context is not None:
        payload["participation_request_context"] = participation_request_context.model_dump()
    resolution_context = _build_task_resolution_context(record)
    if resolution_context is not None:
        payload["resolution_context"] = resolution_context.model_dump()
    return TaskDetail.model_validate(payload)


def _to_task_list_item(record: TaskRecord) -> TaskListItem:
    payload = asdict(record)
    qualification_context = _build_task_qualification_context(record)
    if qualification_context is not None:
        payload["qualification_context"] = qualification_context.model_dump()
    resolution_context = _build_task_resolution_context(record)
    if resolution_context is not None:
        payload["resolution_context"] = resolution_context.model_dump()
    return TaskListItem.model_validate(payload)


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


def _ensure_resolution_payload_allowed(
    *,
    current: TaskRecord,
    payload: TaskUpdate,
    next_status: str,
    current_actor_id: str | None,
) -> tuple[str | None, str | None, str | None, str | None]:
    resolution_fields_touched = bool(
        {"resolution_outcome", "resolution_note"} & payload.model_fields_set
    )
    next_resolution_outcome = (
        payload.resolution_outcome.value
        if "resolution_outcome" in payload.model_fields_set and payload.resolution_outcome is not None
        else (
            None
            if "resolution_outcome" in payload.model_fields_set
            else current.resolution_outcome
        )
    )
    next_resolution_note = (
        payload.resolution_note
        if "resolution_note" in payload.model_fields_set
        else current.resolution_note
    )
    resolved_at = current.resolved_at
    resolved_by_account_id = current.resolved_by_account_id

    if not resolution_fields_touched:
        return (
            next_resolution_outcome,
            next_resolution_note,
            resolved_at,
            resolved_by_account_id,
        )

    if current_actor_id is None:
        raise AppError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="missing_actor_context",
            message="Current actor is required.",
            details={
                "header": "X-Actor-Id",
            },
        )

    actor = ensure_account_exists(current_actor_id)
    if actor.role != AccountRole.DEVELOPER.value:
        _raise_forbidden_actor_role(
            actor_id=actor.id,
            actor_role=actor.role,
            required_role=AccountRole.DEVELOPER.value,
            message="Developer role is required to resolve a task.",
        )

    ensure_task_owned_by_developer(
        current.id,
        current_actor_id,
        resource="task_resolution",
    )

    if next_status != TaskStatus.CLOSED.value:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="invalid_task_resolution_state",
            message="Task resolution can only be recorded when the task is closed.",
            details={
                "resource": "task",
                "task_id": current.id,
                "status": next_status,
                "required_status": TaskStatus.CLOSED.value,
            },
        )

    if next_resolution_outcome is None and current.resolution_outcome is None:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="resolution_outcome_required",
            message="Resolution outcome is required before saving task resolution.",
            details={
                "resource": "task",
                "task_id": current.id,
            },
        )

    resolution_changed = (
        next_resolution_outcome != current.resolution_outcome
        or next_resolution_note != current.resolution_note
    )
    if resolution_changed:
        if next_resolution_outcome is None:
            resolved_at = None
            resolved_by_account_id = None
        else:
            resolved_at = _utc_now_iso()
            resolved_by_account_id = actor.id

    return (
        next_resolution_outcome,
        next_resolution_note,
        resolved_at,
        resolved_by_account_id,
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


def _resolve_owned_campaign_ids_for_actor(current_actor_id: str) -> set[str]:
    from app.modules.campaigns import repository as campaigns_repository
    from app.modules.projects import repository as projects_repository

    actor = ensure_account_exists(current_actor_id)
    if actor.role != AccountRole.DEVELOPER.value:
        _raise_forbidden_actor_role(
            actor_id=actor.id,
            actor_role=actor.role,
            required_role=AccountRole.DEVELOPER.value,
            message="Developer role is required to read owned tasks.",
        )

    owned_project_ids = {
        record.id
        for record in projects_repository.list_projects()
        if record.owner_account_id == current_actor_id
    }

    return {
        record.id
        for record in campaigns_repository.list_campaigns()
        if record.project_id in owned_project_ids
    }


def _filter_task_records_for_actor(
    records: list[TaskRecord],
    current_actor_id: str | None,
) -> list[TaskRecord]:
    if current_actor_id is None:
        raise AppError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="missing_actor_context",
            message="Current actor is required.",
            details={
                "header": "X-Actor-Id",
            },
        )

    actor = ensure_account_exists(current_actor_id)
    if actor.role == AccountRole.DEVELOPER.value:
        owned_campaign_ids = _resolve_owned_campaign_ids_for_actor(current_actor_id)
        return [
            record
            for record in records
            if record.campaign_id in owned_campaign_ids
        ]

    if actor.role == AccountRole.TESTER.value:
        owned_device_profile_ids = _resolve_owned_device_profile_ids_for_actor(
            current_actor_id
        )
        return [
            record
            for record in records
            if record.device_profile_id in owned_device_profile_ids
        ]

    _raise_forbidden_actor_role(
        actor_id=actor.id,
        actor_role=actor.role,
        required_role=AccountRole.DEVELOPER.value,
        message="Developer or tester role is required to read tasks.",
    )
    return records


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

    _ = mine
    records = _filter_task_records_for_actor(records, current_actor_id)

    items = [
        _to_task_list_item(record)
        for record in records
    ]
    return TaskListResponse.model_validate(build_list_response(items))


def get_task(task_id: str, current_actor_id: str | None = None) -> TaskDetail:
    task = ensure_task_exists(task_id)
    task = _ensure_task_read_visibility(task, current_actor_id)
    return _to_task_detail(task)


def create_task(
    campaign_id: str,
    payload: TaskCreate,
    current_actor_id: str | None = None,
    *,
    origin_participation_request_id: str | None = None,
) -> TaskDetail:
    from app.modules.campaigns.service import ensure_campaign_owned_by_actor
    from app.modules.device_profiles.service import ensure_device_profile_exists
    from app.modules.eligibility.service import ensure_device_profile_assignment_is_eligible

    ensure_campaign_owned_by_actor(
        campaign_id,
        current_actor_id,
        resource="task",
    )

    if payload.device_profile_id is not None:
        ensure_device_profile_exists(payload.device_profile_id)
        ensure_device_profile_assignment_is_eligible(
            campaign_id,
            payload.device_profile_id,
        )

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
        resolution_outcome=None,
        resolution_note=None,
        resolved_at=None,
        resolved_by_account_id=None,
        created_at=timestamp,
        updated_at=timestamp,
    )
    repository.create_task(record)
    record_activity_event(
        entity_type=ActivityEntityType.TASK,
        entity_id=record.id,
        event_type=(
            ActivityEventType.TASK_CREATED_FROM_PARTICIPATION_REQUEST
            if origin_participation_request_id is not None
            else ActivityEventType.TASK_CREATED
        ),
        actor_account_id=current_actor_id,
        summary=(
            "從參與意圖建立任務。"
            if origin_participation_request_id is not None
            else "建立任務。"
        ),
    )
    return _to_task_detail(record)


def update_task(
    task_id: str,
    payload: TaskUpdate,
    current_actor_id: str | None = None,
) -> TaskDetail:
    from app.modules.device_profiles.service import ensure_device_profile_exists
    from app.modules.eligibility.service import ensure_device_profile_assignment_is_eligible

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

    actor = ensure_account_exists(current_actor_id) if current_actor_id is not None else None
    assignment_changed = "device_profile_id" in payload.model_fields_set
    status_entered_assignment = (
        current.status not in _TASKS_REQUIRING_ASSIGNMENT
        and next_status in _TASKS_REQUIRING_ASSIGNMENT
    )
    if (
        actor is None or actor.role == AccountRole.DEVELOPER.value
    ) and next_device_profile_id is not None and (
        assignment_changed or status_entered_assignment
    ):
        ensure_device_profile_assignment_is_eligible(
            current.campaign_id,
            next_device_profile_id,
        )

    _ensure_assignment_requirements(
        next_status=next_status,
        device_profile_id=next_device_profile_id,
    )

    (
        next_resolution_outcome,
        next_resolution_note,
        resolved_at,
        resolved_by_account_id,
    ) = _ensure_resolution_payload_allowed(
        current=current,
        payload=payload,
        next_status=next_status,
        current_actor_id=current_actor_id,
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
        resolution_outcome=next_resolution_outcome,
        resolution_note=next_resolution_note,
        resolved_at=resolved_at,
        resolved_by_account_id=resolved_by_account_id,
        updated_at=_utc_now_iso(),
    )
    repository.update_task(updated)
    if updated.resolution_outcome is not None and (
        updated.resolution_outcome != current.resolution_outcome
        or updated.resolution_note != current.resolution_note
        or updated.resolved_at != current.resolved_at
    ):
        record_activity_event(
            entity_type=ActivityEntityType.TASK,
            entity_id=updated.id,
            event_type=ActivityEventType.TASK_RESOLVED,
            actor_account_id=updated.resolved_by_account_id,
            summary=_summarize_task_resolution_outcome(updated.resolution_outcome),
        )
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
