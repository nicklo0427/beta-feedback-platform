from __future__ import annotations

from typing import Optional

from app.modules.eligibility.models import EligibilityRuleRecord

_ELIGIBILITY_RULES: dict[str, EligibilityRuleRecord] = {}


def list_eligibility_rules(campaign_id: Optional[str] = None) -> list[EligibilityRuleRecord]:
    items = list(_ELIGIBILITY_RULES.values())
    if campaign_id is None:
        return items

    return [item for item in items if item.campaign_id == campaign_id]


def get_eligibility_rule(eligibility_rule_id: str) -> Optional[EligibilityRuleRecord]:
    return _ELIGIBILITY_RULES.get(eligibility_rule_id)


def create_eligibility_rule(record: EligibilityRuleRecord) -> EligibilityRuleRecord:
    _ELIGIBILITY_RULES[record.id] = record
    return record


def update_eligibility_rule(record: EligibilityRuleRecord) -> EligibilityRuleRecord:
    _ELIGIBILITY_RULES[record.id] = record
    return record


def delete_eligibility_rule(eligibility_rule_id: str) -> None:
    _ELIGIBILITY_RULES.pop(eligibility_rule_id, None)


def has_eligibility_rules_for_campaign(campaign_id: str) -> bool:
    return any(record.campaign_id == campaign_id for record in _ELIGIBILITY_RULES.values())


def clear_eligibility_rules() -> None:
    _ELIGIBILITY_RULES.clear()
