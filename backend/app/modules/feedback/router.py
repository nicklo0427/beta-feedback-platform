from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_current_actor_id_dep, require_current_actor_id
from app.modules.activity_events.schemas import ActivityTimelineResponse
from app.modules.feedback.schemas import (
    FeedbackCreate,
    FeedbackDetail,
    FeedbackListResponse,
    FeedbackQueueResponse,
    FeedbackReviewStatus,
    FeedbackUpdate,
)
from app.modules.activity_events.service import list_feedback_timeline
from app.modules.feedback.service import (
    create_feedback,
    delete_feedback,
    get_feedback_for_actor,
    list_feedback_for_actor,
    list_feedback_queue,
    update_feedback,
)

router = APIRouter(tags=["feedback"])


@router.get("/tasks/{task_id}/feedback", response_model=FeedbackListResponse)
def list_feedback_route(
    task_id: str,
    current_actor_id: Annotated[Optional[str], Depends(get_current_actor_id_dep)] = None,
) -> FeedbackListResponse:
    return list_feedback_for_actor(
        task_id,
        require_current_actor_id(current_actor_id),
    )


@router.post(
    "/tasks/{task_id}/feedback",
    response_model=FeedbackDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_feedback_route(
    task_id: str,
    payload: FeedbackCreate,
    current_actor_id: Annotated[Optional[str], Depends(get_current_actor_id_dep)] = None,
) -> FeedbackDetail:
    return create_feedback(
        task_id,
        payload,
        require_current_actor_id(current_actor_id),
    )


@router.get("/feedback", response_model=FeedbackQueueResponse)
def list_feedback_queue_route(
    mine: bool = False,
    review_status: Optional[FeedbackReviewStatus] = None,
    current_actor_id: Annotated[Optional[str], Depends(get_current_actor_id_dep)] = None,
) -> FeedbackQueueResponse:
    return list_feedback_queue(
        review_status=review_status,
        mine=mine,
        current_actor_id=current_actor_id,
    )


@router.get("/feedback/{feedback_id}", response_model=FeedbackDetail)
def get_feedback_route(
    feedback_id: str,
    current_actor_id: Annotated[Optional[str], Depends(get_current_actor_id_dep)] = None,
) -> FeedbackDetail:
    return get_feedback_for_actor(feedback_id, current_actor_id)


@router.get("/feedback/{feedback_id}/timeline", response_model=ActivityTimelineResponse)
def get_feedback_timeline_route(
    feedback_id: str,
    current_actor_id: Annotated[Optional[str], Depends(get_current_actor_id_dep)] = None,
) -> ActivityTimelineResponse:
    return list_feedback_timeline(
        feedback_id,
        require_current_actor_id(current_actor_id),
    )


@router.patch("/feedback/{feedback_id}", response_model=FeedbackDetail)
def update_feedback_route(
    feedback_id: str,
    payload: FeedbackUpdate,
    current_actor_id: Annotated[Optional[str], Depends(get_current_actor_id_dep)] = None,
) -> FeedbackDetail:
    return update_feedback(
        feedback_id,
        payload,
        require_current_actor_id(current_actor_id),
    )


@router.delete("/feedback/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback_route(feedback_id: str) -> Response:
    delete_feedback(feedback_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
