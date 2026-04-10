from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_current_actor_id_dep

from app.modules.accounts.schemas import (
    AccountCollaborationSummary,
    AccountCreate,
    AccountDetail,
    AccountListResponse,
    AccountUpdate,
)
from app.modules.accounts.service import (
    create_account,
    delete_account,
    get_account_summary_for_actor,
    get_account_for_actor,
    list_accounts,
    update_account,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=AccountListResponse)
def list_accounts_route() -> AccountListResponse:
    return list_accounts()


@router.post("", response_model=AccountDetail, status_code=status.HTTP_201_CREATED)
def create_account_route(payload: AccountCreate) -> AccountDetail:
    return create_account(payload)


@router.get("/{account_id}", response_model=AccountDetail)
def get_account_route(
    account_id: str,
    current_actor_id: Annotated[Optional[str], Depends(get_current_actor_id_dep)] = None,
) -> AccountDetail:
    return get_account_for_actor(account_id, current_actor_id)


@router.get("/{account_id}/summary", response_model=AccountCollaborationSummary)
def get_account_summary_route(
    account_id: str,
    current_actor_id: Annotated[Optional[str], Depends(get_current_actor_id_dep)] = None,
) -> AccountCollaborationSummary:
    return get_account_summary_for_actor(account_id, current_actor_id)


@router.patch("/{account_id}", response_model=AccountDetail)
def update_account_route(account_id: str, payload: AccountUpdate) -> AccountDetail:
    return update_account(account_id, payload)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account_route(account_id: str) -> Response:
    delete_account(account_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
