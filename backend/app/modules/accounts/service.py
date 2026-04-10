from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import status

from app.common.exceptions import AppError
from app.common.responses import build_list_response
from app.modules.accounts import repository
from app.modules.accounts.models import AccountRecord
from app.modules.accounts.schemas import (
    AccountCollaborationSummary,
    AccountCreate,
    AccountDetail,
    AccountListItem,
    AccountListResponse,
    AccountRecentCampaign,
    AccountRecentDeviceProfile,
    AccountRecentFeedback,
    AccountRecentProject,
    AccountRecentTask,
    AccountRole,
    AccountUpdate,
    DeveloperAccountSummary,
    TesterAccountSummary,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _generate_account_id() -> str:
    return f"acct_{uuid4().hex[:12]}"


def _to_account_detail(record: AccountRecord) -> AccountDetail:
    return AccountDetail.model_validate(asdict(record))


def _to_account_list_item(record: AccountRecord) -> AccountListItem:
    return AccountListItem.model_validate(asdict(record))


def _latest_timestamp(values: list[str | None]) -> str | None:
    normalized_values = [value for value in values if value is not None]
    if not normalized_values:
        return None
    return max(normalized_values)


def _take_recent(records: list[object], *, key: str, limit: int = 3) -> list[object]:
    return sorted(
        records,
        key=lambda record: getattr(record, key),
        reverse=True,
    )[:limit]


def ensure_account_exists(account_id: str) -> AccountRecord:
    record = repository.get_account(account_id)
    if record is None:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="resource_not_found",
            message="Account not found.",
            details={
                "resource": "account",
                "id": account_id,
            },
        )

    return record


def _ensure_account_read_visibility(
    account_id: str,
    current_actor_id: str | None,
) -> AccountRecord:
    if current_actor_id is None:
        raise AppError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="missing_actor_context",
            message="Current actor is required.",
            details={
                "header": "X-Actor-Id",
            },
        )

    account = ensure_account_exists(account_id)
    actor = ensure_account_exists(current_actor_id)

    if actor.id != account.id:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="ownership_mismatch",
            message="Current actor does not own the target resource.",
            details={
                "actor_id": actor.id,
                "resource": "account",
                "ownership_anchor": {
                    "resource": "account",
                    "id": account.id,
                    "owner_account_id": account.id,
                },
            },
        )

    return account


def list_accounts() -> AccountListResponse:
    items = [_to_account_list_item(record) for record in repository.list_accounts()]
    return AccountListResponse.model_validate(build_list_response(items))


def get_account(account_id: str) -> AccountDetail:
    return _to_account_detail(ensure_account_exists(account_id))


def get_account_for_actor(
    account_id: str,
    current_actor_id: str | None,
) -> AccountDetail:
    return _to_account_detail(
        _ensure_account_read_visibility(account_id, current_actor_id)
    )


def get_account_summary(account_id: str) -> AccountCollaborationSummary:
    from app.modules.campaigns import repository as campaigns_repository
    from app.modules.feedback import repository as feedback_repository
    from app.modules.feedback.schemas import FeedbackReviewStatus
    from app.modules.device_profiles import repository as device_profiles_repository
    from app.modules.projects import repository as projects_repository
    from app.modules.tasks import repository as task_repository

    account = ensure_account_exists(account_id)

    if account.role == AccountRole.DEVELOPER.value:
        owned_projects = [
            record
            for record in projects_repository.list_projects()
            if record.owner_account_id == account_id
        ]
        owned_project_ids = {record.id for record in owned_projects}
        owned_campaigns = [
            record
            for record in campaigns_repository.list_campaigns()
            if record.project_id in owned_project_ids
        ]
        owned_campaign_ids = {record.id for record in owned_campaigns}
        feedback_to_review_items = [
            item
            for item in feedback_repository.list_feedback()
            if item.campaign_id in owned_campaign_ids
            and item.review_status == FeedbackReviewStatus.SUBMITTED.value
        ]

        updated_at = _latest_timestamp(
            [account.updated_at]
            + [record.updated_at for record in owned_projects]
            + [record.updated_at for record in owned_campaigns]
            + [item.updated_at for item in feedback_to_review_items]
        ) or account.updated_at

        return AccountCollaborationSummary(
            account_id=account.id,
            role=AccountRole(account.role),
            developer_summary=DeveloperAccountSummary(
                owned_projects_count=len(owned_projects),
                owned_campaigns_count=len(owned_campaigns),
                feedback_to_review_count=len(feedback_to_review_items),
                recent_projects=[
                    AccountRecentProject(
                        id=record.id,
                        name=record.name,
                        updated_at=record.updated_at,
                    )
                    for record in _take_recent(owned_projects, key="updated_at")
                ],
                recent_campaigns=[
                    AccountRecentCampaign(
                        id=record.id,
                        project_id=record.project_id,
                        name=record.name,
                        status=record.status,
                        updated_at=record.updated_at,
                    )
                    for record in _take_recent(owned_campaigns, key="updated_at")
                ],
            ),
            updated_at=updated_at,
        )

    owned_device_profiles = [
        record
        for record in device_profiles_repository.list_device_profiles()
        if record.owner_account_id == account_id
    ]
    owned_device_profile_ids = {record.id for record in owned_device_profiles}
    assigned_tasks = [
        record
        for record in task_repository.list_tasks()
        if record.device_profile_id in owned_device_profile_ids
    ]
    owned_task_ids = {record.id for record in assigned_tasks}
    submitted_feedback = [
        item
        for item in feedback_repository.list_feedback()
        if item.task_id in owned_task_ids
    ]

    updated_at = _latest_timestamp(
        [account.updated_at]
        + [record.updated_at for record in owned_device_profiles]
        + [record.updated_at for record in assigned_tasks]
        + [item.updated_at for item in submitted_feedback]
    ) or account.updated_at

    return AccountCollaborationSummary(
        account_id=account.id,
        role=AccountRole(account.role),
        tester_summary=TesterAccountSummary(
            owned_device_profiles_count=len(owned_device_profiles),
            assigned_tasks_count=len(assigned_tasks),
            submitted_feedback_count=len(submitted_feedback),
            recent_device_profiles=[
                AccountRecentDeviceProfile(
                    id=record.id,
                    name=record.name,
                    platform=record.platform,
                    updated_at=record.updated_at,
                )
                for record in _take_recent(owned_device_profiles, key="updated_at")
            ],
            recent_tasks=[
                AccountRecentTask(
                    id=record.id,
                    campaign_id=record.campaign_id,
                    title=record.title,
                    status=record.status,
                    updated_at=record.updated_at,
                )
                for record in _take_recent(assigned_tasks, key="updated_at")
            ],
            recent_feedback=[
                AccountRecentFeedback(
                    id=item.id,
                    task_id=item.task_id,
                    summary=item.summary,
                    review_status=item.review_status,
                    submitted_at=item.submitted_at,
                )
                for item in _take_recent(submitted_feedback, key="submitted_at")
            ],
        ),
        updated_at=updated_at,
    )


def get_account_summary_for_actor(
    account_id: str,
    current_actor_id: str | None,
) -> AccountCollaborationSummary:
    _ensure_account_read_visibility(account_id, current_actor_id)
    return get_account_summary(account_id)


def create_account(payload: AccountCreate) -> AccountDetail:
    return create_account_with_auth(payload)


def create_account_with_auth(
    payload: AccountCreate,
    *,
    email: str | None = None,
    password_hash: str | None = None,
    is_active: bool = True,
) -> AccountDetail:
    timestamp = _utc_now_iso()
    record = AccountRecord(
        id=_generate_account_id(),
        display_name=payload.display_name,
        role=payload.role.value,
        bio=payload.bio,
        locale=payload.locale,
        created_at=timestamp,
        updated_at=timestamp,
        email=email.strip().lower() if email else None,
        password_hash=password_hash,
        is_active=is_active,
    )
    repository.create_account(record)
    return _to_account_detail(record)


def update_account(account_id: str, payload: AccountUpdate) -> AccountDetail:
    current = ensure_account_exists(account_id)
    updated = replace(
        current,
        display_name=(
            payload.display_name
            if payload.display_name is not None
            else current.display_name
        ),
        role=payload.role.value if payload.role is not None else current.role,
        bio=payload.bio if payload.bio is not None else current.bio,
        locale=payload.locale if payload.locale is not None else current.locale,
        updated_at=_utc_now_iso(),
    )
    repository.update_account(updated)
    return _to_account_detail(updated)


def delete_account(account_id: str) -> None:
    ensure_account_exists(account_id)
    repository.delete_account(account_id)
