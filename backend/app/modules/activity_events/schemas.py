from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ActivityEntityType(str, Enum):
    PARTICIPATION_REQUEST = "participation_request"
    TASK = "task"
    FEEDBACK = "feedback"


class ActivityEventType(str, Enum):
    PARTICIPATION_REQUEST_CREATED = "participation_request_created"
    PARTICIPATION_REQUEST_ACCEPTED = "participation_request_accepted"
    PARTICIPATION_REQUEST_DECLINED = "participation_request_declined"
    PARTICIPATION_REQUEST_WITHDRAWN = "participation_request_withdrawn"
    TASK_CREATED = "task_created"
    TASK_CREATED_FROM_PARTICIPATION_REQUEST = "task_created_from_participation_request"
    FEEDBACK_SUBMITTED = "feedback_submitted"
    FEEDBACK_REVIEWED = "feedback_reviewed"
    FEEDBACK_NEEDS_MORE_INFO = "feedback_needs_more_info"
    FEEDBACK_RESUBMITTED = "feedback_resubmitted"
    TASK_RESOLVED = "task_resolved"


class ActivityEventItem(BaseModel):
    id: str
    entity_type: ActivityEntityType
    entity_id: str
    event_type: ActivityEventType
    actor_account_id: str
    actor_account_display_name: Optional[str] = None
    summary: str
    created_at: str


class ActivityTimelineResponse(BaseModel):
    items: list[ActivityEventItem]
    total: int
