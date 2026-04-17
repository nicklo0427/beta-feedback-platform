from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import status

from app.common.exceptions import AppError
from app.common.responses import build_list_response
from app.modules.accounts.schemas import AccountRole
from app.modules.accounts.service import ensure_account_exists
from app.modules.activity_events.schemas import ActivityEntityType, ActivityEventType
from app.modules.activity_events.service import record_activity_event
from app.modules.participation_requests import repository
from app.modules.participation_requests.models import ParticipationRequestRecord
from app.modules.participation_requests.schemas import (
    ParticipationAssignmentStatus,
    ParticipationRequestCreate,
    ParticipationRequestDetail,
    ParticipationRequestEnrichedDetail,
    ParticipationRequestListItem,
    ParticipationRequestListResponse,
    ParticipationRequestStatus,
    ParticipationRequestTaskCreate,
    ParticipationRequestUpdate,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _generate_participation_request_id() -> str:
    return f"pr_{uuid4().hex[:12]}"


def _resolve_campaign_name(campaign_id: str) -> str:
    from app.modules.campaigns import repository as campaigns_repository

    campaign = campaigns_repository.get_campaign(campaign_id)
    return campaign.name if campaign is not None else campaign_id


def _resolve_device_profile_name(device_profile_id: str) -> str:
    from app.modules.device_profiles import repository as device_profiles_repository

    device_profile = device_profiles_repository.get_device_profile(device_profile_id)
    return device_profile.name if device_profile is not None else device_profile_id


def _resolve_assignment_status(
    record: ParticipationRequestRecord,
) -> ParticipationAssignmentStatus:
    if record.linked_task_id is not None:
        return ParticipationAssignmentStatus.TASK_CREATED

    return ParticipationAssignmentStatus.NOT_ASSIGNED


def _to_participation_request_detail(
    record: ParticipationRequestRecord,
) -> ParticipationRequestDetail:
    return ParticipationRequestDetail.model_validate(
        {
            "id": record.id,
            "campaign_id": record.campaign_id,
            "campaign_name": _resolve_campaign_name(record.campaign_id),
            "tester_account_id": record.tester_account_id,
            "device_profile_id": record.device_profile_id,
            "device_profile_name": _resolve_device_profile_name(record.device_profile_id),
            "status": record.status,
            "note": record.note,
            "decision_note": record.decision_note,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
            "decided_at": record.decided_at,
            "linked_task_id": record.linked_task_id,
            "assignment_created_at": record.assignment_created_at,
            "assignment_status": _resolve_assignment_status(record),
        }
    )


def _to_participation_request_enriched_detail(
    record: ParticipationRequestRecord,
) -> ParticipationRequestEnrichedDetail:
    from app.modules.accounts.service import get_account, get_account_summary
    from app.modules.campaigns.service import get_campaign
    from app.modules.device_profiles.service import get_device_profile
    from app.modules.eligibility.service import (
        evaluate_campaign_device_profile_qualification,
    )
    from app.modules.device_profiles.service import ensure_device_profile_exists
    from app.modules.reputation.service import (
        get_campaign_reputation,
        get_device_profile_reputation,
    )

    device_profile = ensure_device_profile_exists(record.device_profile_id)
    qualification_snapshot = evaluate_campaign_device_profile_qualification(
        record.campaign_id,
        device_profile,
    )

    return ParticipationRequestEnrichedDetail.model_validate(
        {
            "id": record.id,
            "campaign_id": record.campaign_id,
            "campaign_name": _resolve_campaign_name(record.campaign_id),
            "tester_account_id": record.tester_account_id,
            "device_profile_id": record.device_profile_id,
            "device_profile_name": _resolve_device_profile_name(record.device_profile_id),
            "status": record.status,
            "note": record.note,
            "decision_note": record.decision_note,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
            "decided_at": record.decided_at,
            "linked_task_id": record.linked_task_id,
            "assignment_created_at": record.assignment_created_at,
            "assignment_status": _resolve_assignment_status(record),
            "tester_account": get_account(record.tester_account_id).model_dump(),
            "tester_account_summary": get_account_summary(record.tester_account_id).model_dump(),
            "device_profile": get_device_profile(record.device_profile_id).model_dump(),
            "device_profile_reputation": get_device_profile_reputation(
                record.device_profile_id
            ).model_dump(),
            "qualification_snapshot": qualification_snapshot.model_dump(),
            "campaign": get_campaign(record.campaign_id).model_dump(),
            "campaign_reputation": get_campaign_reputation(record.campaign_id).model_dump(),
        }
    )


def _to_participation_request_list_item(
    record: ParticipationRequestRecord,
) -> ParticipationRequestListItem:
    return ParticipationRequestListItem.model_validate(
        {
            "id": record.id,
            "campaign_id": record.campaign_id,
            "campaign_name": _resolve_campaign_name(record.campaign_id),
            "tester_account_id": record.tester_account_id,
            "device_profile_id": record.device_profile_id,
            "device_profile_name": _resolve_device_profile_name(record.device_profile_id),
            "status": record.status,
            "note": record.note,
            "decision_note": record.decision_note,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
            "decided_at": record.decided_at,
            "linked_task_id": record.linked_task_id,
            "assignment_created_at": record.assignment_created_at,
            "assignment_status": _resolve_assignment_status(record),
        }
    )


def _ensure_tester_actor(current_actor_id: str) -> str:
    actor = ensure_account_exists(current_actor_id)
    if actor.role != AccountRole.TESTER.value:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="forbidden_actor_role",
            message="Tester role is required for this operation.",
            details={
                "actor_id": actor.id,
                "actor_role": actor.role,
                "required_role": AccountRole.TESTER.value,
            },
        )

    return actor.id


def _ensure_developer_actor(current_actor_id: str) -> str:
    actor = ensure_account_exists(current_actor_id)
    if actor.role != AccountRole.DEVELOPER.value:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="forbidden_actor_role",
            message="Developer role is required for this operation.",
            details={
                "actor_id": actor.id,
                "actor_role": actor.role,
                "required_role": AccountRole.DEVELOPER.value,
            },
        )

    return actor.id


def _raise_ownership_mismatch(
    actor_id: str,
    resource: str,
    ownership_anchor: dict[str, str | None],
) -> None:
    raise AppError(
        status_code=status.HTTP_409_CONFLICT,
        code="ownership_mismatch",
        message="Current actor does not own the target resource.",
        details={
            "actor_id": actor_id,
            "resource": resource,
            "ownership_anchor": ownership_anchor,
        },
    )


def _raise_invalid_participation_transition(
    *,
    request_id: str,
    current_status: str,
    next_status: str,
) -> None:
    raise AppError(
        status_code=status.HTTP_409_CONFLICT,
        code="invalid_participation_transition",
        message="Participation request status transition is not allowed.",
        details={
            "resource": "participation_request",
            "id": request_id,
            "current_status": current_status,
            "next_status": next_status,
        },
    )


def _raise_participation_request_not_accepted(
    *,
    request_id: str,
    current_status: str,
) -> None:
    raise AppError(
        status_code=status.HTTP_409_CONFLICT,
        code="participation_request_not_accepted",
        message="Only accepted participation requests can be turned into tasks.",
        details={
            "resource": "participation_request",
            "id": request_id,
            "current_status": current_status,
            "required_status": ParticipationRequestStatus.ACCEPTED.value,
        },
    )


def _raise_participation_request_task_already_created(
    *,
    request_id: str,
    linked_task_id: str,
) -> None:
    raise AppError(
        status_code=status.HTTP_409_CONFLICT,
        code="participation_request_task_already_created",
        message="This participation request already has a linked task.",
        details={
            "resource": "participation_request",
            "id": request_id,
            "linked_task_id": linked_task_id,
        },
    )


def _resolve_owned_campaign_ids_for_actor(current_actor_id: str) -> set[str]:
    from app.modules.campaigns import repository as campaigns_repository
    from app.modules.projects import repository as projects_repository

    developer_account_id = _ensure_developer_actor(current_actor_id)
    owned_project_ids = {
        record.id
        for record in projects_repository.list_projects()
        if record.owner_account_id == developer_account_id
    }
    return {
        record.id
        for record in campaigns_repository.list_campaigns()
        if record.project_id in owned_project_ids
    }


def ensure_participation_request_exists(
    request_id: str,
) -> ParticipationRequestRecord:
    record = repository.get_participation_request(request_id)
    if record is None:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="resource_not_found",
            message="Participation request not found.",
            details={
                "resource": "participation_request",
                "id": request_id,
            },
        )

    return record


def get_participation_request(
    request_id: str,
    current_actor_id: str,
) -> ParticipationRequestEnrichedDetail:
    from app.modules.campaigns.service import ensure_campaign_owned_by_actor

    record = ensure_participation_request_exists(request_id)
    actor = ensure_account_exists(current_actor_id)

    if actor.role == AccountRole.TESTER.value:
        if record.tester_account_id != actor.id:
            _raise_ownership_mismatch(
                actor.id,
                "participation_request",
                {
                    "resource": "tester_account",
                    "id": record.tester_account_id,
                    "owner_account_id": record.tester_account_id,
                },
            )
        return _to_participation_request_enriched_detail(record)

    if actor.role == AccountRole.DEVELOPER.value:
        ensure_campaign_owned_by_actor(
            record.campaign_id,
            actor.id,
            resource="participation_request",
        )
        return _to_participation_request_enriched_detail(record)

    raise AppError(
        status_code=status.HTTP_409_CONFLICT,
        code="forbidden_actor_role",
        message="Current actor role cannot access participation request details.",
        details={
            "actor_id": actor.id,
            "actor_role": actor.role,
        },
    )


def list_participation_requests(
    *,
    mine: bool = False,
    review_mine: bool = False,
    current_actor_id: str,
) -> ParticipationRequestListResponse:
    if mine == review_mine:
        raise AppError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="invalid_query",
            message="Use exactly one participation request queue selector.",
            details={
                "supported_queries": ["mine", "review_mine"],
            },
        )

    records = sorted(
        repository.list_participation_requests(),
        key=lambda record: record.created_at,
        reverse=True,
    )

    if mine:
        tester_account_id = _ensure_tester_actor(current_actor_id)
        records = [
            record
            for record in records
            if record.tester_account_id == tester_account_id
        ]

    if review_mine:
        owned_campaign_ids = _resolve_owned_campaign_ids_for_actor(current_actor_id)
        records = [
            record
            for record in records
            if record.campaign_id in owned_campaign_ids
            and (
                record.status == ParticipationRequestStatus.PENDING.value
                or (
                    record.status == ParticipationRequestStatus.ACCEPTED.value
                    and record.linked_task_id is None
                )
            )
        ]

    items = [_to_participation_request_list_item(record) for record in records]
    return ParticipationRequestListResponse.model_validate(build_list_response(items))


def create_participation_request(
    campaign_id: str,
    payload: ParticipationRequestCreate,
    current_actor_id: str,
) -> ParticipationRequestDetail:
    from app.modules.campaigns.service import ensure_campaign_exists
    from app.modules.device_profiles.service import ensure_device_profile_exists
    from app.modules.eligibility.service import evaluate_campaign_device_profile_qualification

    tester_account_id = _ensure_tester_actor(current_actor_id)
    ensure_campaign_exists(campaign_id)
    device_profile = ensure_device_profile_exists(payload.device_profile_id)

    if device_profile.owner_account_id != tester_account_id:
        _raise_ownership_mismatch(
            tester_account_id,
            "participation_request",
            {
                "resource": "device_profile",
                "id": device_profile.id,
                "owner_account_id": device_profile.owner_account_id,
            },
        )

    qualification_result = evaluate_campaign_device_profile_qualification(
        campaign_id,
        device_profile,
    )
    if qualification_result.qualification_status != "qualified":
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="participation_not_qualified",
            message="Selected device profile is not eligible to request participation in this campaign.",
            details={
                "campaign_id": campaign_id,
                "tester_account_id": tester_account_id,
                "device_profile_id": qualification_result.device_profile_id,
                "qualification_status": qualification_result.qualification_status,
                "matched_rule_id": qualification_result.matched_rule_id,
                "reason_codes": qualification_result.reason_codes,
                "reason_summary": qualification_result.reason_summary,
            },
        )

    for existing_record in repository.list_participation_requests():
        if (
            existing_record.campaign_id == campaign_id
            and existing_record.tester_account_id == tester_account_id
            and existing_record.device_profile_id == payload.device_profile_id
            and existing_record.status == ParticipationRequestStatus.PENDING.value
        ):
            raise AppError(
                status_code=status.HTTP_409_CONFLICT,
                code="duplicate_pending_participation_request",
                message="Pending participation request already exists for this campaign and device profile.",
                details={
                    "campaign_id": campaign_id,
                    "tester_account_id": tester_account_id,
                    "device_profile_id": payload.device_profile_id,
                    "existing_request_id": existing_record.id,
                    "existing_status": existing_record.status,
                },
            )

    timestamp = _utc_now_iso()
    record = ParticipationRequestRecord(
        id=_generate_participation_request_id(),
        campaign_id=campaign_id,
        tester_account_id=tester_account_id,
        device_profile_id=payload.device_profile_id,
        status=ParticipationRequestStatus.PENDING.value,
        note=payload.note,
        decision_note=None,
        created_at=timestamp,
        updated_at=timestamp,
        decided_at=None,
        linked_task_id=None,
        assignment_created_at=None,
    )
    repository.create_participation_request(record)
    record_activity_event(
        entity_type=ActivityEntityType.PARTICIPATION_REQUEST,
        entity_id=record.id,
        event_type=ActivityEventType.PARTICIPATION_REQUEST_CREATED,
        actor_account_id=tester_account_id,
        summary="送出參與意圖。",
    )
    return _to_participation_request_detail(record)


def update_participation_request(
    request_id: str,
    payload: ParticipationRequestUpdate,
    current_actor_id: str,
) -> ParticipationRequestDetail:
    current = ensure_participation_request_exists(request_id)
    actor = ensure_account_exists(current_actor_id)

    if actor.role == AccountRole.TESTER.value:
        if payload.status != ParticipationRequestStatus.WITHDRAWN.value:
            raise AppError(
                status_code=status.HTTP_409_CONFLICT,
                code="forbidden_actor_role",
                message="Developer role is required to review participation requests.",
                details={
                    "actor_id": actor.id,
                    "actor_role": actor.role,
                    "required_role": AccountRole.DEVELOPER.value,
                },
            )

        if current.tester_account_id != actor.id:
            _raise_ownership_mismatch(
                actor.id,
                "participation_request",
                {
                    "resource": "tester_account",
                    "id": current.tester_account_id,
                    "owner_account_id": current.tester_account_id,
                },
            )

        if current.status != ParticipationRequestStatus.PENDING.value:
            _raise_invalid_participation_transition(
                request_id=current.id,
                current_status=current.status,
                next_status=payload.status,
            )

        updated = replace(
            current,
            status=payload.status,
            updated_at=_utc_now_iso(),
        )
        repository.update_participation_request(updated)
        record_activity_event(
            entity_type=ActivityEntityType.PARTICIPATION_REQUEST,
            entity_id=updated.id,
            event_type=ActivityEventType.PARTICIPATION_REQUEST_WITHDRAWN,
            actor_account_id=actor.id,
            summary="撤回參與意圖。",
        )
        return _to_participation_request_detail(updated)

    if actor.role == AccountRole.DEVELOPER.value:
        from app.modules.campaigns.service import ensure_campaign_owned_by_actor

        ensure_campaign_owned_by_actor(
            current.campaign_id,
            actor.id,
            resource="participation_request",
        )

        if payload.status not in {
            ParticipationRequestStatus.ACCEPTED.value,
            ParticipationRequestStatus.DECLINED.value,
        }:
            _raise_invalid_participation_transition(
                request_id=current.id,
                current_status=current.status,
                next_status=payload.status,
            )

        if current.status != ParticipationRequestStatus.PENDING.value:
            _raise_invalid_participation_transition(
                request_id=current.id,
                current_status=current.status,
                next_status=payload.status,
            )

        timestamp = _utc_now_iso()
        updated = replace(
            current,
            status=payload.status,
            decision_note=payload.decision_note,
            updated_at=timestamp,
            decided_at=timestamp,
        )
        repository.update_participation_request(updated)
        record_activity_event(
            entity_type=ActivityEntityType.PARTICIPATION_REQUEST,
            entity_id=updated.id,
            event_type=(
                ActivityEventType.PARTICIPATION_REQUEST_ACCEPTED
                if updated.status == ParticipationRequestStatus.ACCEPTED.value
                else ActivityEventType.PARTICIPATION_REQUEST_DECLINED
            ),
            actor_account_id=actor.id,
            summary=(
                "接受參與意圖。"
                if updated.status == ParticipationRequestStatus.ACCEPTED.value
                else "婉拒參與意圖。"
            ),
        )
        return _to_participation_request_detail(updated)

    raise AppError(
        status_code=status.HTTP_409_CONFLICT,
        code="forbidden_actor_role",
        message="Current actor role cannot update participation requests.",
        details={
            "actor_id": actor.id,
            "actor_role": actor.role,
        },
    )


def create_task_from_participation_request(
    request_id: str,
    payload: ParticipationRequestTaskCreate,
    current_actor_id: str,
):
    from app.modules.campaigns.service import ensure_campaign_owned_by_actor
    from app.modules.tasks.schemas import TaskCreate
    from app.modules.tasks.service import create_task

    developer_account_id = _ensure_developer_actor(current_actor_id)
    current = ensure_participation_request_exists(request_id)

    ensure_campaign_owned_by_actor(
        current.campaign_id,
        developer_account_id,
        resource="participation_request",
    )

    if current.status != ParticipationRequestStatus.ACCEPTED.value:
        _raise_participation_request_not_accepted(
            request_id=current.id,
            current_status=current.status,
        )

    if current.linked_task_id is not None:
        _raise_participation_request_task_already_created(
            request_id=current.id,
            linked_task_id=current.linked_task_id,
        )

    created_task = create_task(
        current.campaign_id,
        TaskCreate(
            title=payload.title,
            instruction_summary=payload.instruction_summary,
            device_profile_id=current.device_profile_id,
            status=payload.status,
        ),
        developer_account_id,
        origin_participation_request_id=current.id,
    )

    timestamp = _utc_now_iso()
    updated = replace(
        current,
        linked_task_id=created_task.id,
        assignment_created_at=timestamp,
        updated_at=timestamp,
    )
    repository.update_participation_request(updated)
    record_activity_event(
        entity_type=ActivityEntityType.PARTICIPATION_REQUEST,
        entity_id=updated.id,
        event_type=ActivityEventType.TASK_CREATED_FROM_PARTICIPATION_REQUEST,
        actor_account_id=developer_account_id,
        summary="從參與意圖建立任務。",
    )
    return created_task
