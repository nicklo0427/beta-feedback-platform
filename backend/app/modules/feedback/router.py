from __future__ import annotations

from fastapi import APIRouter, Response, status

from app.modules.feedback.schemas import (
    FeedbackCreate,
    FeedbackDetail,
    FeedbackListResponse,
    FeedbackUpdate,
)
from app.modules.feedback.service import (
    create_feedback,
    delete_feedback,
    get_feedback,
    list_feedback,
    update_feedback,
)

router = APIRouter(tags=["feedback"])


@router.get("/tasks/{task_id}/feedback", response_model=FeedbackListResponse)
def list_feedback_route(task_id: str) -> FeedbackListResponse:
    return list_feedback(task_id)


@router.post(
    "/tasks/{task_id}/feedback",
    response_model=FeedbackDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_feedback_route(task_id: str, payload: FeedbackCreate) -> FeedbackDetail:
    return create_feedback(task_id, payload)


@router.get("/feedback/{feedback_id}", response_model=FeedbackDetail)
def get_feedback_route(feedback_id: str) -> FeedbackDetail:
    return get_feedback(feedback_id)


@router.patch("/feedback/{feedback_id}", response_model=FeedbackDetail)
def update_feedback_route(feedback_id: str, payload: FeedbackUpdate) -> FeedbackDetail:
    return update_feedback(feedback_id, payload)


@router.delete("/feedback/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback_route(feedback_id: str) -> Response:
    delete_feedback(feedback_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
