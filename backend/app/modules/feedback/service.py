from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import status

from app.common.exceptions import AppError
from app.common.responses import build_list_response
from app.modules.feedback import repository
from app.modules.feedback.models import FeedbackRecord
from app.modules.feedback.schemas import (
    FeedbackCreate,
    FeedbackDetail,
    FeedbackListItem,
    FeedbackListResponse,
    FeedbackUpdate,
)


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


def list_feedback(task_id: str) -> FeedbackListResponse:
    from app.modules.tasks.service import ensure_task_exists

    ensure_task_exists(task_id)

    items = [
        _to_feedback_list_item(record)
        for record in repository.list_feedback(task_id=task_id)
    ]
    return FeedbackListResponse.model_validate(build_list_response(items))


def get_feedback(feedback_id: str) -> FeedbackDetail:
    return _to_feedback_detail(ensure_feedback_exists(feedback_id))


def create_feedback(task_id: str, payload: FeedbackCreate) -> FeedbackDetail:
    from app.modules.tasks.schemas import TaskStatus, TaskUpdate
    from app.modules.tasks.service import ensure_task_exists, update_task

    task = ensure_task_exists(task_id)

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
        submitted_at=timestamp,
        updated_at=timestamp,
    )
    repository.create_feedback(record)
    return _to_feedback_detail(record)


def update_feedback(feedback_id: str, payload: FeedbackUpdate) -> FeedbackDetail:
    current = ensure_feedback_exists(feedback_id)
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
        updated_at=_utc_now_iso(),
    )
    repository.update_feedback(updated)
    return _to_feedback_detail(updated)


def delete_feedback(feedback_id: str) -> None:
    ensure_feedback_exists(feedback_id)
    repository.delete_feedback(feedback_id)
