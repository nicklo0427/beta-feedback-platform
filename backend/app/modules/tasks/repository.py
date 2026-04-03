from __future__ import annotations

from typing import Optional

from app.modules.tasks.models import TaskRecord

_TASKS: dict[str, TaskRecord] = {}


def list_tasks(
    *,
    campaign_id: Optional[str] = None,
    device_profile_id: Optional[str] = None,
    status: Optional[str] = None,
) -> list[TaskRecord]:
    items = list(_TASKS.values())

    if campaign_id is not None:
        items = [item for item in items if item.campaign_id == campaign_id]

    if device_profile_id is not None:
        items = [item for item in items if item.device_profile_id == device_profile_id]

    if status is not None:
        items = [item for item in items if item.status == status]

    return items


def get_task(task_id: str) -> Optional[TaskRecord]:
    return _TASKS.get(task_id)


def create_task(record: TaskRecord) -> TaskRecord:
    _TASKS[record.id] = record
    return record


def update_task(record: TaskRecord) -> TaskRecord:
    _TASKS[record.id] = record
    return record


def delete_task(task_id: str) -> None:
    _TASKS.pop(task_id, None)


def has_tasks_for_campaign(campaign_id: str) -> bool:
    return any(record.campaign_id == campaign_id for record in _TASKS.values())


def has_tasks_for_device_profile(device_profile_id: str) -> bool:
    return any(record.device_profile_id == device_profile_id for record in _TASKS.values())


def clear_tasks() -> None:
    _TASKS.clear()
