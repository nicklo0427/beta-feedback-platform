from __future__ import annotations

from typing import Optional

from app.modules.safety.models import CampaignSafetyRecord

_SAFETY_BY_CAMPAIGN_ID: dict[str, CampaignSafetyRecord] = {}


def get_campaign_safety(campaign_id: str) -> Optional[CampaignSafetyRecord]:
    return _SAFETY_BY_CAMPAIGN_ID.get(campaign_id)


def has_safety_for_campaign(campaign_id: str) -> bool:
    return campaign_id in _SAFETY_BY_CAMPAIGN_ID


def create_campaign_safety(record: CampaignSafetyRecord) -> CampaignSafetyRecord:
    _SAFETY_BY_CAMPAIGN_ID[record.campaign_id] = record
    return record


def update_campaign_safety(record: CampaignSafetyRecord) -> CampaignSafetyRecord:
    _SAFETY_BY_CAMPAIGN_ID[record.campaign_id] = record
    return record


def delete_campaign_safety(campaign_id: str) -> None:
    _SAFETY_BY_CAMPAIGN_ID.pop(campaign_id, None)


def clear_campaign_safety_profiles() -> None:
    _SAFETY_BY_CAMPAIGN_ID.clear()
