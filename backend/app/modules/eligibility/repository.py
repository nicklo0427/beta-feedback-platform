from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, select

from app.db.entities import EligibilityRuleEntity
from app.db.session import database_persistence_enabled, db_session_scope
from app.modules.eligibility.models import EligibilityRuleRecord

_ELIGIBILITY_RULES: dict[str, EligibilityRuleRecord] = {}


def _to_record(entity: EligibilityRuleEntity) -> EligibilityRuleRecord:
    return EligibilityRuleRecord(
        id=entity.id,
        campaign_id=entity.campaign_id,
        platform=entity.platform,
        os_name=entity.os_name,
        os_version_min=entity.os_version_min,
        os_version_max=entity.os_version_max,
        install_channel=entity.install_channel,
        is_active=entity.is_active,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def _to_entity(record: EligibilityRuleRecord) -> EligibilityRuleEntity:
    return EligibilityRuleEntity(
        id=record.id,
        campaign_id=record.campaign_id,
        platform=record.platform,
        os_name=record.os_name,
        os_version_min=record.os_version_min,
        os_version_max=record.os_version_max,
        install_channel=record.install_channel,
        is_active=record.is_active,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def list_eligibility_rules(campaign_id: Optional[str] = None) -> list[EligibilityRuleRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            statement = select(EligibilityRuleEntity)
            if campaign_id is not None:
                statement = statement.where(EligibilityRuleEntity.campaign_id == campaign_id)
            items = session.scalars(
                statement.order_by(
                    EligibilityRuleEntity.created_at.asc(),
                    EligibilityRuleEntity.id.asc(),
                )
            ).all()
            return [_to_record(item) for item in items]

    items = list(_ELIGIBILITY_RULES.values())
    if campaign_id is None:
        return items

    return [item for item in items if item.campaign_id == campaign_id]


def get_eligibility_rule(eligibility_rule_id: str) -> Optional[EligibilityRuleRecord]:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(EligibilityRuleEntity, eligibility_rule_id)
            return None if entity is None else _to_record(entity)

    return _ELIGIBILITY_RULES.get(eligibility_rule_id)


def create_eligibility_rule(record: EligibilityRuleRecord) -> EligibilityRuleRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _ELIGIBILITY_RULES[record.id] = record
    return record


def update_eligibility_rule(record: EligibilityRuleRecord) -> EligibilityRuleRecord:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.merge(_to_entity(record))
        return record

    _ELIGIBILITY_RULES[record.id] = record
    return record


def delete_eligibility_rule(eligibility_rule_id: str) -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            entity = session.get(EligibilityRuleEntity, eligibility_rule_id)
            if entity is not None:
                session.delete(entity)
        return

    _ELIGIBILITY_RULES.pop(eligibility_rule_id, None)


def has_eligibility_rules_for_campaign(campaign_id: str) -> bool:
    if database_persistence_enabled():
        with db_session_scope() as session:
            return (
                session.scalar(
                    select(EligibilityRuleEntity.id)
                    .where(EligibilityRuleEntity.campaign_id == campaign_id)
                    .limit(1)
                )
                is not None
            )

    return any(record.campaign_id == campaign_id for record in _ELIGIBILITY_RULES.values())


def clear_eligibility_rules() -> None:
    if database_persistence_enabled():
        with db_session_scope() as session:
            session.execute(delete(EligibilityRuleEntity))
        return

    _ELIGIBILITY_RULES.clear()
