from __future__ import annotations

from typing import Optional

from app.modules.campaigns.models import CampaignRecord

_CAMPAIGNS: dict[str, CampaignRecord] = {}


def list_campaigns(project_id: Optional[str] = None) -> list[CampaignRecord]:
    items = list(_CAMPAIGNS.values())
    if project_id is None:
        return items

    return [item for item in items if item.project_id == project_id]


def get_campaign(campaign_id: str) -> Optional[CampaignRecord]:
    return _CAMPAIGNS.get(campaign_id)


def create_campaign(record: CampaignRecord) -> CampaignRecord:
    _CAMPAIGNS[record.id] = record
    return record


def update_campaign(record: CampaignRecord) -> CampaignRecord:
    _CAMPAIGNS[record.id] = record
    return record


def delete_campaign(campaign_id: str) -> None:
    _CAMPAIGNS.pop(campaign_id, None)


def has_campaigns_for_project(project_id: str) -> bool:
    return any(record.project_id == project_id for record in _CAMPAIGNS.values())


def clear_campaigns() -> None:
    _CAMPAIGNS.clear()
