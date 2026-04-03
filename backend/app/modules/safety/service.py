from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import status

from app.common.exceptions import AppError
from app.modules.safety import repository
from app.modules.safety.models import CampaignSafetyRecord
from app.modules.safety.schemas import (
    CampaignSafetyCreate,
    CampaignSafetyDetail,
    CampaignSafetyUpdate,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _generate_campaign_safety_id() -> str:
    return f"safe_{uuid4().hex[:12]}"


def _to_campaign_safety_detail(record: CampaignSafetyRecord) -> CampaignSafetyDetail:
    return CampaignSafetyDetail.model_validate(asdict(record))


def has_safety_for_campaign(campaign_id: str) -> bool:
    return repository.has_safety_for_campaign(campaign_id)


def ensure_campaign_safety_exists(campaign_id: str) -> CampaignSafetyRecord:
    record = repository.get_campaign_safety(campaign_id)
    if record is None:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="resource_not_found",
            message="Campaign safety not found.",
            details={
                "resource": "campaign_safety",
                "campaign_id": campaign_id,
            },
        )

    return record


def get_campaign_safety(campaign_id: str) -> CampaignSafetyDetail:
    from app.modules.campaigns.service import ensure_campaign_exists

    ensure_campaign_exists(campaign_id)
    return _to_campaign_safety_detail(ensure_campaign_safety_exists(campaign_id))


def create_campaign_safety(
    campaign_id: str,
    payload: CampaignSafetyCreate,
) -> CampaignSafetyDetail:
    from app.modules.campaigns.service import ensure_campaign_exists

    ensure_campaign_exists(campaign_id)

    if repository.has_safety_for_campaign(campaign_id):
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="conflict",
            message="Campaign safety already exists.",
            details={
                "resource": "campaign_safety",
                "campaign_id": campaign_id,
            },
        )

    timestamp = _utc_now_iso()
    record = CampaignSafetyRecord(
        id=_generate_campaign_safety_id(),
        campaign_id=campaign_id,
        distribution_channel=payload.distribution_channel.value,
        source_label=payload.source_label,
        source_url=payload.source_url,
        risk_level=payload.risk_level.value,
        review_status=payload.review_status.value,
        official_channel_only=payload.official_channel_only,
        risk_note=payload.risk_note,
        created_at=timestamp,
        updated_at=timestamp,
    )
    repository.create_campaign_safety(record)
    return _to_campaign_safety_detail(record)


def update_campaign_safety(
    campaign_id: str,
    payload: CampaignSafetyUpdate,
) -> CampaignSafetyDetail:
    from app.modules.campaigns.service import ensure_campaign_exists

    ensure_campaign_exists(campaign_id)

    current = ensure_campaign_safety_exists(campaign_id)
    updated = replace(
        current,
        distribution_channel=(
            payload.distribution_channel.value
            if payload.distribution_channel is not None
            else current.distribution_channel
        ),
        source_label=payload.source_label if payload.source_label is not None else current.source_label,
        source_url=payload.source_url if payload.source_url is not None else current.source_url,
        risk_level=payload.risk_level.value if payload.risk_level is not None else current.risk_level,
        review_status=(
            payload.review_status.value
            if payload.review_status is not None
            else current.review_status
        ),
        official_channel_only=(
            payload.official_channel_only
            if payload.official_channel_only is not None
            else current.official_channel_only
        ),
        risk_note=payload.risk_note if payload.risk_note is not None else current.risk_note,
        updated_at=_utc_now_iso(),
    )
    repository.update_campaign_safety(updated)
    return _to_campaign_safety_detail(updated)


def delete_campaign_safety(campaign_id: str) -> None:
    from app.modules.campaigns.service import ensure_campaign_exists

    ensure_campaign_exists(campaign_id)
    ensure_campaign_safety_exists(campaign_id)
    repository.delete_campaign_safety(campaign_id)
