from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_actor_id_dep, require_current_actor_id
from app.modules.activity_events.schemas import ActivityTimelineResponse
from app.modules.participation_requests.schemas import (
    ParticipationRequestCreate,
    ParticipationRequestDetail,
    ParticipationRequestEnrichedDetail,
    ParticipationRequestListResponse,
    ParticipationRequestTaskCreate,
    ParticipationRequestUpdate,
)
from app.modules.participation_requests.service import (
    create_task_from_participation_request,
    create_participation_request,
    get_participation_request,
    list_participation_requests,
    update_participation_request,
)
from app.modules.activity_events.service import list_participation_request_timeline
from app.modules.tasks.schemas import TaskDetail

router = APIRouter(tags=["participation_requests"])


@router.get(
    "/participation-requests",
    response_model=ParticipationRequestListResponse,
    response_model_exclude_unset=True,
)
def list_participation_requests_route(
    mine: bool = Query(default=False),
    review_mine: bool = Query(default=False),
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> ParticipationRequestListResponse:
    return list_participation_requests(
        mine=mine,
        review_mine=review_mine,
        current_actor_id=require_current_actor_id(current_actor_id),
    )


@router.get(
    "/participation-requests/{request_id}",
    response_model=ParticipationRequestEnrichedDetail,
    response_model_exclude_unset=True,
)
def get_participation_request_route(
    request_id: str,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> ParticipationRequestEnrichedDetail:
    return get_participation_request(
        request_id,
        require_current_actor_id(current_actor_id),
    )


@router.get(
    "/participation-requests/{request_id}/timeline",
    response_model=ActivityTimelineResponse,
    response_model_exclude_unset=True,
)
def get_participation_request_timeline_route(
    request_id: str,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> ActivityTimelineResponse:
    return list_participation_request_timeline(
        request_id,
        require_current_actor_id(current_actor_id),
    )


@router.post(
    "/campaigns/{campaign_id}/participation-requests",
    response_model=ParticipationRequestDetail,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_unset=True,
)
def create_participation_request_route(
    campaign_id: str,
    payload: ParticipationRequestCreate,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> ParticipationRequestDetail:
    return create_participation_request(
        campaign_id,
        payload,
        require_current_actor_id(current_actor_id),
    )


@router.patch(
    "/participation-requests/{request_id}",
    response_model=ParticipationRequestDetail,
    response_model_exclude_unset=True,
)
def update_participation_request_route(
    request_id: str,
    payload: ParticipationRequestUpdate,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> ParticipationRequestDetail:
    return update_participation_request(
        request_id,
        payload,
        require_current_actor_id(current_actor_id),
    )


@router.post(
    "/participation-requests/{request_id}/tasks",
    response_model=TaskDetail,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_unset=True,
)
def create_task_from_participation_request_route(
    request_id: str,
    payload: ParticipationRequestTaskCreate,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> TaskDetail:
    return create_task_from_participation_request(
        request_id,
        payload,
        require_current_actor_id(current_actor_id),
    )
