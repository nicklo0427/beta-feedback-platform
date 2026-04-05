from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import get_current_actor_id_dep, require_current_actor_id
from app.modules.tasks.schemas import (
    TaskCreate,
    TaskDetail,
    TaskListResponse,
    TaskStatus,
    TaskUpdate,
)
from app.modules.tasks.service import (
    create_task,
    delete_task,
    get_task,
    list_tasks,
    update_task,
)

router = APIRouter(tags=["tasks"])


@router.get("/tasks", response_model=TaskListResponse)
def list_tasks_route(
    campaign_id: Optional[str] = Query(default=None),
    device_profile_id: Optional[str] = Query(default=None),
    status: Optional[TaskStatus] = Query(default=None),
    mine: bool = False,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> TaskListResponse:
    return list_tasks(
        campaign_id=campaign_id,
        device_profile_id=device_profile_id,
        status_filter=status,
        mine=mine,
        current_actor_id=current_actor_id,
    )


@router.post(
    "/campaigns/{campaign_id}/tasks",
    response_model=TaskDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_task_route(
    campaign_id: str,
    payload: TaskCreate,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> TaskDetail:
    return create_task(
        campaign_id,
        payload,
        require_current_actor_id(current_actor_id),
    )


@router.get("/tasks/{task_id}", response_model=TaskDetail)
def get_task_route(task_id: str) -> TaskDetail:
    return get_task(task_id)


@router.patch("/tasks/{task_id}", response_model=TaskDetail)
def update_task_route(
    task_id: str,
    payload: TaskUpdate,
    current_actor_id: Optional[str] = Depends(get_current_actor_id_dep),
) -> TaskDetail:
    return update_task(
        task_id,
        payload,
        require_current_actor_id(current_actor_id),
    )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_route(task_id: str) -> Response:
    delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
