from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import status

from app.common.exceptions import AppError
from app.common.responses import build_list_response
from app.modules.feedback import repository
from app.modules.feedback.models import FeedbackRecord
from app.modules.accounts.schemas import AccountRole
from app.modules.accounts.service import ensure_account_exists
from app.modules.feedback.schemas import (
    FeedbackCreate,
    FeedbackDetail,
    FeedbackListItem,
    FeedbackListResponse,
    FeedbackQueueItem,
    FeedbackQueueResponse,
    FeedbackReviewStatus,
    FeedbackUpdate,
)

FEEDBACK_CONTENT_FIELDS = {
    "summary",
    "rating",
    "severity",
    "category",
    "reproduction_steps",
    "expected_result",
    "actual_result",
    "note",
}

FEEDBACK_REVIEW_FIELDS = {
    "review_status",
    "developer_note",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _generate_feedback_id() -> str:
    return f"fb_{uuid4().hex[:12]}"


def _to_feedback_detail(record: FeedbackRecord) -> FeedbackDetail:
    return FeedbackDetail.model_validate(asdict(record))


def _to_feedback_list_item(record: FeedbackRecord) -> FeedbackListItem:
    return FeedbackListItem.model_validate(asdict(record))


def _to_feedback_queue_item(record: FeedbackRecord) -> FeedbackQueueItem:
    return FeedbackQueueItem.model_validate(asdict(record))


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


def ensure_feedback_exists(feedback_id: str) -> FeedbackRecord:
    record = repository.get_feedback(feedback_id)
    if record is None:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="resource_not_found",
            message="Feedback not found.",
            details={
                "resource": "feedback",
                "id": feedback_id,
            },
        )

    return record


def has_feedback_for_task(task_id: str) -> bool:
    return repository.has_feedback_for_task(task_id)


def _resolve_owned_campaign_ids_for_actor(current_actor_id: str) -> set[str]:
    from app.modules.campaigns import repository as campaigns_repository
    from app.modules.projects import repository as projects_repository

    actor = ensure_account_exists(current_actor_id)
    if actor.role != AccountRole.DEVELOPER.value:
        _raise_forbidden_actor_role(
            actor_id=actor.id,
            actor_role=actor.role,
            required_role=AccountRole.DEVELOPER.value,
            message="Developer role is required to review owned feedback.",
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


def _resolve_owned_device_profile_ids_for_actor(current_actor_id: str) -> set[str]:
    from app.modules.device_profiles import repository as device_profiles_repository

    actor = ensure_account_exists(current_actor_id)
    if actor.role != AccountRole.TESTER.value:
        _raise_forbidden_actor_role(
            actor_id=actor.id,
            actor_role=actor.role,
            required_role=AccountRole.TESTER.value,
            message="Tester role is required to read owned feedback.",
        )

    return {
        record.id
        for record in device_profiles_repository.list_device_profiles()
        if record.owner_account_id == current_actor_id
    }


def ensure_feedback_owned_by_tester(
    feedback_id: str,
    current_actor_id: str | None,
    resource: str = "feedback",
) -> FeedbackRecord:
    from app.modules.device_profiles.service import ensure_device_profile_exists

    if current_actor_id is None:
        return ensure_feedback_exists(feedback_id)

    actor = ensure_account_exists(current_actor_id)
    if actor.role != AccountRole.TESTER.value:
        _raise_forbidden_actor_role(
            actor_id=actor.id,
            actor_role=actor.role,
            required_role=AccountRole.TESTER.value,
            message="Tester role is required for this operation.",
        )

    feedback = ensure_feedback_exists(feedback_id)
    if feedback.device_profile_id is None:
        _raise_ownership_mismatch(
            actor.id,
            resource,
            {
                "resource": "device_profile",
                "id": None,
                "owner_account_id": None,
            },
        )

    device_profile = ensure_device_profile_exists(feedback.device_profile_id)
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

    return feedback


def ensure_feedback_owned_by_developer(
    feedback_id: str,
    current_actor_id: str | None,
    resource: str = "feedback",
) -> FeedbackRecord:
    from app.modules.campaigns.service import ensure_campaign_owned_by_actor

    feedback = ensure_feedback_exists(feedback_id)
    ensure_campaign_owned_by_actor(
        feedback.campaign_id,
        current_actor_id,
        resource=resource,
    )
    return feedback


def list_feedback(task_id: str) -> FeedbackListResponse:
    from app.modules.tasks.service import ensure_task_exists

    ensure_task_exists(task_id)

    items = [
        _to_feedback_list_item(record)
        for record in repository.list_feedback(task_id=task_id)
    ]
    return FeedbackListResponse.model_validate(build_list_response(items))


def list_feedback_queue(
    *,
    review_status: FeedbackReviewStatus | None = None,
    mine: bool = False,
    current_actor_id: str | None = None,
) -> FeedbackQueueResponse:
    records = repository.list_feedback()

    if review_status is not None:
        records = [record for record in records if record.review_status == review_status.value]

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
        records = [
            record for record in records if record.campaign_id in owned_campaign_ids
        ]
    elif actor.role == AccountRole.TESTER.value:
        owned_device_profile_ids = _resolve_owned_device_profile_ids_for_actor(
            current_actor_id
        )
        records = [
            record
            for record in records
            if record.device_profile_id in owned_device_profile_ids
        ]
    else:
        _raise_forbidden_actor_role(
            actor_id=actor.id,
            actor_role=actor.role,
            required_role=AccountRole.DEVELOPER.value,
            message="Developer or tester role is required to read feedback queue.",
        )

    items = [_to_feedback_queue_item(record) for record in records]
    return FeedbackQueueResponse.model_validate(build_list_response(items))


def get_feedback(feedback_id: str) -> FeedbackDetail:
    return _to_feedback_detail(ensure_feedback_exists(feedback_id))


def get_feedback_for_actor(
    feedback_id: str,
    current_actor_id: str | None,
) -> FeedbackDetail:
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
        feedback = ensure_feedback_owned_by_developer(
            feedback_id,
            current_actor_id,
            resource="feedback",
        )
        return _to_feedback_detail(feedback)

    if actor.role == AccountRole.TESTER.value:
        feedback = ensure_feedback_owned_by_tester(
            feedback_id,
            current_actor_id,
            resource="feedback",
        )
        return _to_feedback_detail(feedback)

    _raise_forbidden_actor_role(
        actor_id=actor.id,
        actor_role=actor.role,
        required_role=AccountRole.DEVELOPER.value,
        message="Developer or tester role is required to read feedback detail.",
    )
    return _to_feedback_detail(ensure_feedback_exists(feedback_id))


def create_feedback(
    task_id: str,
    payload: FeedbackCreate,
    current_actor_id: str | None = None,
) -> FeedbackDetail:
    from app.modules.tasks.schemas import TaskStatus, TaskUpdate
    from app.modules.tasks.service import (
        ensure_task_exists,
        ensure_task_owned_by_tester,
        update_task,
    )

    task = ensure_task_owned_by_tester(
        task_id,
        current_actor_id,
        resource="feedback",
    )

    if task.status == TaskStatus.ASSIGNED.value:
        update_task(task.id, TaskUpdate(status=TaskStatus.IN_PROGRESS))
        task = ensure_task_exists(task_id)

    if task.status == TaskStatus.IN_PROGRESS.value:
        update_task(task.id, TaskUpdate(status=TaskStatus.SUBMITTED))
        task = ensure_task_exists(task_id)

    timestamp = _utc_now_iso()
    record = FeedbackRecord(
        id=_generate_feedback_id(),
        task_id=task.id,
        campaign_id=task.campaign_id,
        device_profile_id=task.device_profile_id,
        summary=payload.summary,
        rating=payload.rating,
        severity=payload.severity.value,
        category=payload.category.value,
        reproduction_steps=payload.reproduction_steps,
        expected_result=payload.expected_result,
        actual_result=payload.actual_result,
        note=payload.note,
        review_status=FeedbackReviewStatus.SUBMITTED.value,
        developer_note=None,
        submitted_at=timestamp,
        resubmitted_at=None,
        updated_at=timestamp,
    )
    repository.create_feedback(record)
    return _to_feedback_detail(record)


def update_feedback(
    feedback_id: str,
    payload: FeedbackUpdate,
    current_actor_id: str | None = None,
) -> FeedbackDetail:
    content_fields = FEEDBACK_CONTENT_FIELDS.intersection(payload.model_fields_set)
    review_fields = FEEDBACK_REVIEW_FIELDS.intersection(payload.model_fields_set)

    if current_actor_id is not None:
        actor = ensure_account_exists(current_actor_id)
        if actor.role == AccountRole.DEVELOPER.value:
            if content_fields:
                _raise_forbidden_actor_role(
                    actor_id=actor.id,
                    actor_role=actor.role,
                    required_role=AccountRole.TESTER.value,
                    message="Tester role is required to edit feedback content.",
                )
            current = ensure_feedback_owned_by_developer(
                feedback_id,
                current_actor_id,
                resource="feedback",
            )
        elif actor.role == AccountRole.TESTER.value:
            if review_fields:
                _raise_forbidden_actor_role(
                    actor_id=actor.id,
                    actor_role=actor.role,
                    required_role=AccountRole.DEVELOPER.value,
                    message="Developer role is required to review feedback.",
                )
            current = ensure_feedback_owned_by_tester(
                feedback_id,
                current_actor_id,
                resource="feedback",
            )
        else:
            _raise_forbidden_actor_role(
                actor_id=actor.id,
                actor_role=actor.role,
                required_role=AccountRole.TESTER.value,
                message="Tester role is required for this operation.",
            )
    else:
        current = ensure_feedback_exists(feedback_id)

    timestamp = _utc_now_iso()
    is_resubmission = (
        current.review_status == FeedbackReviewStatus.NEEDS_MORE_INFO.value
        and bool(content_fields)
    )

    updated = replace(
        current,
        summary=payload.summary if "summary" in payload.model_fields_set else current.summary,
        rating=payload.rating if "rating" in payload.model_fields_set else current.rating,
        severity=(
            payload.severity.value
            if "severity" in payload.model_fields_set and payload.severity is not None
            else current.severity
        ),
        category=(
            payload.category.value
            if "category" in payload.model_fields_set and payload.category is not None
            else current.category
        ),
        reproduction_steps=(
            payload.reproduction_steps
            if "reproduction_steps" in payload.model_fields_set
            else current.reproduction_steps
        ),
        expected_result=(
            payload.expected_result
            if "expected_result" in payload.model_fields_set
            else current.expected_result
        ),
        actual_result=(
            payload.actual_result
            if "actual_result" in payload.model_fields_set
            else current.actual_result
        ),
        note=payload.note if "note" in payload.model_fields_set else current.note,
        review_status=(
            FeedbackReviewStatus.SUBMITTED.value
            if is_resubmission
            else (
                payload.review_status.value
                if "review_status" in payload.model_fields_set and payload.review_status is not None
                else current.review_status
            )
        ),
        developer_note=(
            payload.developer_note
            if "developer_note" in payload.model_fields_set
            else current.developer_note
        ),
        resubmitted_at=timestamp if is_resubmission else current.resubmitted_at,
        updated_at=timestamp,
    )
    repository.update_feedback(updated)
    return _to_feedback_detail(updated)


def delete_feedback(feedback_id: str) -> None:
    ensure_feedback_exists(feedback_id)
    repository.delete_feedback(feedback_id)
