from __future__ import annotations

from typing import Optional

from app.modules.feedback.models import FeedbackRecord

_FEEDBACK: dict[str, FeedbackRecord] = {}


def list_feedback(*, task_id: Optional[str] = None) -> list[FeedbackRecord]:
    items = list(_FEEDBACK.values())
    if task_id is not None:
        items = [item for item in items if item.task_id == task_id]
    return items


def get_feedback(feedback_id: str) -> Optional[FeedbackRecord]:
    return _FEEDBACK.get(feedback_id)


def create_feedback(record: FeedbackRecord) -> FeedbackRecord:
    _FEEDBACK[record.id] = record
    return record


def update_feedback(record: FeedbackRecord) -> FeedbackRecord:
    _FEEDBACK[record.id] = record
    return record


def delete_feedback(feedback_id: str) -> None:
    _FEEDBACK.pop(feedback_id, None)


def has_feedback_for_task(task_id: str) -> bool:
    return any(record.task_id == task_id for record in _FEEDBACK.values())


def clear_feedback() -> None:
    _FEEDBACK.clear()
