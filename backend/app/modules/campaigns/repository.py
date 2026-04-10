from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, select

from app.db.entities import CampaignEntity
from app.db.session import database_persistence_enabled, db_session_scope
from app.modules.campaigns.models import CampaignRecord

_CAMPAIGNS: dict[str, CampaignRecord] = {}


def _to_record(entity: CampaignEntity) -> CampaignRecord:
    return CampaignRecord(
        id=entity.id,
        project_id=entity.project_id,
        name=entity.name,
        description=entity.description,
        target_platforms=list(entity.target_platforms or []),
        version_label=entity.version_label,
        status=entity.status,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def _to_entity(record: CampaignRecord) -> CampaignEntity:
    return CampaignEntity(
        id=record.id,
        project_id=record.project_id,
        name=record.name,
        description=record.description,
        target_platforms=list(record.target_platforms),
        version_label=record.version_label,
        status=record.status,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def list_campaigns(project_id: Optional[str] = None) -> list[CampaignRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            statement = select(CampaignEntity)
            if project_id is not None:
                statement = statement.where(CampaignEntity.project_id == project_id)
            items = session.scalars(
                statement.order_by(CampaignEntity.created_at.asc(), CampaignEntity.id.asc())
            ).all()
            return [_to_record(item) for item in items]

    items = list(_CAMPAIGNS.values())
    if project_id is None:
        return items

    return [item for item in items if item.project_id == project_id]


def get_campaign(campaign_id: str) -> Optional[CampaignRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(CampaignEntity, campaign_id)
            return None if entity is None else _to_record(entity)

    return _CAMPAIGNS.get(campaign_id)


def create_campaign(record: CampaignRecord) -> CampaignRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _CAMPAIGNS[record.id] = record
    return record


def update_campaign(record: CampaignRecord) -> CampaignRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _CAMPAIGNS[record.id] = record
    return record


def delete_campaign(campaign_id: str) -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(CampaignEntity, campaign_id)
            if entity is not None:
                session.delete(entity)
        return

    _CAMPAIGNS.pop(campaign_id, None)


def has_campaigns_for_project(project_id: str) -> bool:
    if database_persistence_enabled():
        with db_session_scope() as session:
            return (
                session.scalar(
                    select(CampaignEntity.id)
                    .where(CampaignEntity.project_id == project_id)
                    .limit(1)
                )
                is not None
            )

    return any(record.project_id == project_id for record in _CAMPAIGNS.values())


def clear_campaigns() -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.execute(delete(CampaignEntity))
        return

    _CAMPAIGNS.clear()
