from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.common.responses import build_list_response
from app.modules.accounts import repository as accounts_repository
from app.modules.activity_events import repository
from app.modules.activity_events.models import ActivityEventRecord
from app.modules.activity_events.schemas import (
    ActivityEntityType,
    ActivityEventItem,
    ActivityEventType,
    ActivityTimelineResponse,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _generate_activity_event_id() -> str:
    return f"evt_{uuid4().hex[:12]}"


def _resolve_actor_display_name(actor_account_id: str) -> str | None:
    account = accounts_repository.get_account(actor_account_id)
    if account is None:
        return None
    return account.display_name


def _to_activity_event_item(record: ActivityEventRecord) -> ActivityEventItem:
    return ActivityEventItem.model_validate(
        {
            "id": record.id,
            "entity_type": record.entity_type,
            "entity_id": record.entity_id,
            "event_type": record.event_type,
            "actor_account_id": record.actor_account_id,
            "actor_account_display_name": _resolve_actor_display_name(
                record.actor_account_id
            ),
            "summary": record.summary,
            "created_at": record.created_at,
        }
    )


def record_activity_event(
    *,
    entity_type: ActivityEntityType,
    entity_id: str,
    event_type: ActivityEventType,
    actor_account_id: str | None,
    summary: str,
    created_at: str | None = None,
) -> ActivityEventRecord | None:
    if actor_account_id is None:
        return None

    record = ActivityEventRecord(
        id=_generate_activity_event_id(),
        entity_type=entity_type.value,
        entity_id=entity_id,
        event_type=event_type.value,
        actor_account_id=actor_account_id,
        summary=summary,
        created_at=created_at or _utc_now_iso(),
    )
    repository.create_activity_event(record)
    return record


def list_activity_events_for_entity(
    entity_type: ActivityEntityType,
    entity_id: str,
) -> ActivityTimelineResponse:
    items = [
        _to_activity_event_item(record)
        for record in repository.list_activity_events(
            entity_type=entity_type.value,
            entity_id=entity_id,
        )
    ]
    return ActivityTimelineResponse.model_validate(build_list_response(items))


def list_participation_request_timeline(
    request_id: str,
    current_actor_id: str,
) -> ActivityTimelineResponse:
    from app.modules.participation_requests.service import get_participation_request

    get_participation_request(request_id, current_actor_id)
    return list_activity_events_for_entity(
        ActivityEntityType.PARTICIPATION_REQUEST,
        request_id,
    )


def list_task_timeline(
    task_id: str,
    current_actor_id: str | None,
) -> ActivityTimelineResponse:
    from app.modules.tasks.service import get_task

    get_task(task_id, current_actor_id)
    return list_activity_events_for_entity(ActivityEntityType.TASK, task_id)


def list_feedback_timeline(
    feedback_id: str,
    current_actor_id: str | None,
) -> ActivityTimelineResponse:
    from app.modules.feedback.service import get_feedback_for_actor

    get_feedback_for_actor(feedback_id, current_actor_id)
    return list_activity_events_for_entity(ActivityEntityType.FEEDBACK, feedback_id)
