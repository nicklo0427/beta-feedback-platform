from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, select

from app.db.entities import CampaignSafetyEntity
from app.db.session import database_persistence_enabled, db_session_scope
from app.modules.safety.models import CampaignSafetyRecord

_SAFETY_BY_CAMPAIGN_ID: dict[str, CampaignSafetyRecord] = {}


def _to_record(entity: CampaignSafetyEntity) -> CampaignSafetyRecord:
    return CampaignSafetyRecord(
        id=entity.id,
        campaign_id=entity.campaign_id,
        distribution_channel=entity.distribution_channel,
        source_label=entity.source_label,
        source_url=entity.source_url,
        risk_level=entity.risk_level,
        review_status=entity.review_status,
        official_channel_only=entity.official_channel_only,
        risk_note=entity.risk_note,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def _to_entity(record: CampaignSafetyRecord) -> CampaignSafetyEntity:
    return CampaignSafetyEntity(
        id=record.id,
        campaign_id=record.campaign_id,
        distribution_channel=record.distribution_channel,
        source_label=record.source_label,
        source_url=record.source_url,
        risk_level=record.risk_level,
        review_status=record.review_status,
        official_channel_only=record.official_channel_only,
        risk_note=record.risk_note,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def get_campaign_safety(campaign_id: str) -> Optional[CampaignSafetyRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.scalar(
                select(CampaignSafetyEntity).where(CampaignSafetyEntity.campaign_id == campaign_id)
            )
            return None if entity is None else _to_record(entity)

    return _SAFETY_BY_CAMPAIGN_ID.get(campaign_id)


def has_safety_for_campaign(campaign_id: str) -> bool:
    if database_persistence_enabled():
        with db_session_scope() as session:
            return (
                session.scalar(
                    select(CampaignSafetyEntity.id)
                    .where(CampaignSafetyEntity.campaign_id == campaign_id)
                    .limit(1)
                )
                is not None
            )

    return campaign_id in _SAFETY_BY_CAMPAIGN_ID


def create_campaign_safety(record: CampaignSafetyRecord) -> CampaignSafetyRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _SAFETY_BY_CAMPAIGN_ID[record.campaign_id] = record
    return record


def update_campaign_safety(record: CampaignSafetyRecord) -> CampaignSafetyRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _SAFETY_BY_CAMPAIGN_ID[record.campaign_id] = record
    return record


def delete_campaign_safety(campaign_id: str) -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.execute(
                delete(CampaignSafetyEntity).where(CampaignSafetyEntity.campaign_id == campaign_id)
            )
        return

    _SAFETY_BY_CAMPAIGN_ID.pop(campaign_id, None)


def clear_campaign_safety_profiles() -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.execute(delete(CampaignSafetyEntity))
        return

    _SAFETY_BY_CAMPAIGN_ID.clear()
