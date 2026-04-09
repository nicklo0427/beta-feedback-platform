from __future__ import annotations

from typing import Optional

from app.modules.participation_requests.models import ParticipationRequestRecord

_PARTICIPATION_REQUESTS: dict[str, ParticipationRequestRecord] = {}


def list_participation_requests() -> list[ParticipationRequestRecord]:
    return list(_PARTICIPATION_REQUESTS.values())


def get_participation_request(
    request_id: str,
) -> Optional[ParticipationRequestRecord]:
    return _PARTICIPATION_REQUESTS.get(request_id)


def create_participation_request(
    record: ParticipationRequestRecord,
) -> ParticipationRequestRecord:
    _PARTICIPATION_REQUESTS[record.id] = record
    return record


def update_participation_request(
    record: ParticipationRequestRecord,
) -> ParticipationRequestRecord:
    _PARTICIPATION_REQUESTS[record.id] = record
    return record


def clear_participation_requests() -> None:
    _PARTICIPATION_REQUESTS.clear()

