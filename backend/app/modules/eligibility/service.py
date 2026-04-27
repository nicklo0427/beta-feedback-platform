from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import status

from app.common.exceptions import AppError
from app.common.responses import build_list_response
from app.modules.accounts.capabilities import account_has_role, raise_forbidden_actor_role
from app.modules.accounts.schemas import AccountRole
from app.modules.accounts.service import ensure_account_exists
from app.modules.eligibility import repository
from app.modules.eligibility.models import EligibilityRuleRecord
from app.modules.eligibility.schemas import (
    CampaignQualificationResultItem,
    CampaignQualificationResultListResponse,
    EligibilityRuleCreate,
    EligibilityRuleDetail,
    EligibilityRuleListItem,
    EligibilityRuleListResponse,
    EligibilityRuleUpdate,
    QualificationReasonCode,
    QualificationStatus,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _generate_eligibility_rule_id() -> str:
    return f"er_{uuid4().hex[:12]}"


def _to_eligibility_rule_detail(record: EligibilityRuleRecord) -> EligibilityRuleDetail:
    return EligibilityRuleDetail.model_validate(asdict(record))


def _to_eligibility_rule_list_item(record: EligibilityRuleRecord) -> EligibilityRuleListItem:
    return EligibilityRuleListItem.model_validate(asdict(record))


def _to_campaign_qualification_result_item(
    payload: dict[str, object],
) -> CampaignQualificationResultItem:
    return CampaignQualificationResultItem.model_validate(payload)


def _normalize_comparable_string(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        return None

    return normalized.casefold()


def _parse_dotted_numeric_version(value: str | None) -> tuple[int, ...] | None:
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        return None

    parts = normalized.split(".")
    if any(not part.isdigit() for part in parts):
        return None

    return tuple(int(part) for part in parts)


def _compare_versions(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    max_length = max(len(left), len(right))
    left_padded = left + (0,) * (max_length - len(left))
    right_padded = right + (0,) * (max_length - len(right))

    if left_padded < right_padded:
        return -1
    if left_padded > right_padded:
        return 1
    return 0


def _get_reason_summary(reason_codes: list[str], *, no_active_rules: bool = False) -> str:
    if no_active_rules:
        return "目前沒有啟用中的資格限制。"

    if not reason_codes:
        return "符合目前活動的資格條件。"

    reason_labels = {
        QualificationReasonCode.PLATFORM_MISMATCH.value: "平台不符合目前活動條件",
        QualificationReasonCode.OS_NAME_MISMATCH.value: "作業系統不符合目前活動條件",
        QualificationReasonCode.OS_VERSION_BELOW_MIN.value: "作業系統版本低於最低要求",
        QualificationReasonCode.OS_VERSION_ABOVE_MAX.value: "作業系統版本高於最高允許版本",
        QualificationReasonCode.OS_VERSION_UNCOMPARABLE.value: "作業系統版本格式無法比較",
        QualificationReasonCode.INSTALL_CHANNEL_MISMATCH.value: "安裝渠道不符合目前活動條件",
    }
    labels = [reason_labels.get(code, code) for code in reason_codes]
    return f"主要未符合條件：{'；'.join(labels)}。"


def _dedupe_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def _evaluate_rule_against_device_profile(
    rule: EligibilityRuleRecord,
    device_profile,
) -> list[str]:
    reason_codes: list[str] = []

    if rule.platform != device_profile.platform:
        reason_codes.append(QualificationReasonCode.PLATFORM_MISMATCH.value)

    rule_os_name = _normalize_comparable_string(rule.os_name)
    device_os_name = _normalize_comparable_string(device_profile.os_name)
    if rule_os_name is not None and rule_os_name != device_os_name:
        reason_codes.append(QualificationReasonCode.OS_NAME_MISMATCH.value)

    if rule.os_version_min is not None or rule.os_version_max is not None:
        device_version = _parse_dotted_numeric_version(device_profile.os_version)
        min_version = _parse_dotted_numeric_version(rule.os_version_min)
        max_version = _parse_dotted_numeric_version(rule.os_version_max)

        if device_version is None or (
            rule.os_version_min is not None and min_version is None
        ) or (
            rule.os_version_max is not None and max_version is None
        ):
            reason_codes.append(QualificationReasonCode.OS_VERSION_UNCOMPARABLE.value)
        else:
            if min_version is not None and _compare_versions(device_version, min_version) < 0:
                reason_codes.append(QualificationReasonCode.OS_VERSION_BELOW_MIN.value)
            if max_version is not None and _compare_versions(device_version, max_version) > 0:
                reason_codes.append(QualificationReasonCode.OS_VERSION_ABOVE_MAX.value)

    rule_install_channel = _normalize_comparable_string(rule.install_channel)
    device_install_channel = _normalize_comparable_string(
        getattr(device_profile, "install_channel", None)
    )
    if rule_install_channel is not None and rule_install_channel != device_install_channel:
        reason_codes.append(QualificationReasonCode.INSTALL_CHANNEL_MISMATCH.value)

    return _dedupe_preserving_order(reason_codes)


def _build_campaign_qualification_result_item(
    *,
    device_profile,
    active_rules: list[EligibilityRuleRecord],
) -> CampaignQualificationResultItem:
    if not active_rules:
        return _to_campaign_qualification_result_item(
            {
                "device_profile_id": device_profile.id,
                "device_profile_name": device_profile.name,
                "qualification_status": QualificationStatus.QUALIFIED.value,
                "matched_rule_id": None,
                "reason_codes": [],
                "reason_summary": _get_reason_summary([], no_active_rules=True),
            }
        )

    matched_rule: EligibilityRuleRecord | None = None
    aggregated_reason_codes: list[str] = []

    for rule in active_rules:
        reason_codes = _evaluate_rule_against_device_profile(rule, device_profile)
        if not reason_codes:
            matched_rule = rule
            break

        aggregated_reason_codes.extend(reason_codes)

    if matched_rule is not None:
        return _to_campaign_qualification_result_item(
            {
                "device_profile_id": device_profile.id,
                "device_profile_name": device_profile.name,
                "qualification_status": QualificationStatus.QUALIFIED.value,
                "matched_rule_id": matched_rule.id,
                "reason_codes": [],
                "reason_summary": _get_reason_summary([]),
            }
        )

    deduped_reason_codes = _dedupe_preserving_order(aggregated_reason_codes)
    return _to_campaign_qualification_result_item(
        {
            "device_profile_id": device_profile.id,
            "device_profile_name": device_profile.name,
            "qualification_status": QualificationStatus.NOT_QUALIFIED.value,
            "matched_rule_id": None,
            "reason_codes": deduped_reason_codes,
            "reason_summary": _get_reason_summary(deduped_reason_codes),
        }
    )


def evaluate_campaign_device_profile_qualification(
    campaign_id: str,
    device_profile,
) -> CampaignQualificationResultItem:
    from app.modules.campaigns.service import ensure_campaign_exists

    ensure_campaign_exists(campaign_id)
    active_rules = [
        record
        for record in repository.list_eligibility_rules(campaign_id=campaign_id)
        if record.is_active
    ]

    return _build_campaign_qualification_result_item(
        device_profile=device_profile,
        active_rules=active_rules,
    )


def _ensure_tester_actor(current_actor_id: str):
    actor = ensure_account_exists(current_actor_id)
    if not account_has_role(actor, AccountRole.TESTER):
        raise_forbidden_actor_role(
            actor,
            AccountRole.TESTER,
            "Tester role is required for this operation.",
        )

    return actor


def ensure_eligibility_rule_exists(eligibility_rule_id: str) -> EligibilityRuleRecord:
    record = repository.get_eligibility_rule(eligibility_rule_id)
    if record is None:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="resource_not_found",
            message="Eligibility rule not found.",
            details={
                "resource": "eligibility_rule",
                "id": eligibility_rule_id,
            },
        )

    return record


def has_eligibility_rules_for_campaign(campaign_id: str) -> bool:
    return repository.has_eligibility_rules_for_campaign(campaign_id)


def list_eligibility_rules(campaign_id: str) -> EligibilityRuleListResponse:
    from app.modules.campaigns.service import ensure_campaign_exists

    ensure_campaign_exists(campaign_id)

    items = [
        _to_eligibility_rule_list_item(record)
        for record in repository.list_eligibility_rules(campaign_id=campaign_id)
    ]
    return EligibilityRuleListResponse.model_validate(build_list_response(items))


def list_eligibility_rules_for_actor(
    campaign_id: str,
    current_actor_id: str | None,
) -> EligibilityRuleListResponse:
    from app.modules.campaigns.service import ensure_campaign_owned_by_actor

    ensure_campaign_owned_by_actor(
        campaign_id,
        current_actor_id,
        resource="eligibility_rule",
    )
    return list_eligibility_rules(campaign_id)


def list_campaign_qualification_results(
    campaign_id: str,
    current_actor_id: str,
) -> CampaignQualificationResultListResponse:
    from app.modules.campaigns.service import ensure_campaign_exists
    from app.modules.device_profiles import repository as device_profiles_repository

    ensure_campaign_exists(campaign_id)
    _ensure_tester_actor(current_actor_id)

    owned_device_profiles = [
        record
        for record in device_profiles_repository.list_device_profiles()
        if record.owner_account_id == current_actor_id
    ]

    items: list[CampaignQualificationResultItem] = []
    for device_profile in owned_device_profiles:
        items.append(
            evaluate_campaign_device_profile_qualification(campaign_id, device_profile)
        )

    return CampaignQualificationResultListResponse.model_validate(
        build_list_response(items)
    )


def get_campaign_qualification_check(
    campaign_id: str,
    device_profile_id: str,
    current_actor_id: str | None = None,
) -> CampaignQualificationResultItem:
    from app.modules.campaigns.service import ensure_campaign_owned_by_actor
    from app.modules.device_profiles.service import ensure_device_profile_exists

    ensure_campaign_owned_by_actor(
        campaign_id,
        current_actor_id,
        resource="qualification_check",
    )
    device_profile = ensure_device_profile_exists(device_profile_id)
    active_rules = [
        record
        for record in repository.list_eligibility_rules(campaign_id=campaign_id)
        if record.is_active
    ]

    return _build_campaign_qualification_result_item(
        device_profile=device_profile,
        active_rules=active_rules,
    )


def ensure_device_profile_assignment_is_eligible(
    campaign_id: str,
    device_profile_id: str,
) -> CampaignQualificationResultItem:
    qualification_result = get_campaign_qualification_check(
        campaign_id,
        device_profile_id,
    )

    if qualification_result.qualification_status == QualificationStatus.QUALIFIED.value:
        return qualification_result

    raise AppError(
        status_code=status.HTTP_409_CONFLICT,
        code="assignment_not_eligible",
        message="Selected device profile does not meet campaign eligibility requirements.",
        details={
            "campaign_id": campaign_id,
            "device_profile_id": qualification_result.device_profile_id,
            "qualification_status": qualification_result.qualification_status,
            "matched_rule_id": qualification_result.matched_rule_id,
            "reason_codes": qualification_result.reason_codes,
            "reason_summary": qualification_result.reason_summary,
        },
    )


def get_eligibility_rule(eligibility_rule_id: str) -> EligibilityRuleDetail:
    return _to_eligibility_rule_detail(ensure_eligibility_rule_exists(eligibility_rule_id))


def get_eligibility_rule_for_actor(
    eligibility_rule_id: str,
    current_actor_id: str | None,
) -> EligibilityRuleDetail:
    from app.modules.campaigns.service import ensure_campaign_owned_by_actor

    record = ensure_eligibility_rule_exists(eligibility_rule_id)
    ensure_campaign_owned_by_actor(
        record.campaign_id,
        current_actor_id,
        resource="eligibility_rule",
    )
    return _to_eligibility_rule_detail(record)


def create_eligibility_rule(
    campaign_id: str,
    payload: EligibilityRuleCreate,
    current_actor_id: str | None = None,
) -> EligibilityRuleDetail:
    from app.modules.campaigns.service import ensure_campaign_owned_by_actor

    ensure_campaign_owned_by_actor(
        campaign_id,
        current_actor_id,
        resource="eligibility_rule",
    )

    timestamp = _utc_now_iso()
    record = EligibilityRuleRecord(
        id=_generate_eligibility_rule_id(),
        campaign_id=campaign_id,
        platform=payload.platform.value,
        os_name=payload.os_name,
        os_version_min=payload.os_version_min,
        os_version_max=payload.os_version_max,
        install_channel=payload.install_channel,
        is_active=payload.is_active,
        created_at=timestamp,
        updated_at=timestamp,
    )
    repository.create_eligibility_rule(record)
    return _to_eligibility_rule_detail(record)


def update_eligibility_rule(
    eligibility_rule_id: str,
    payload: EligibilityRuleUpdate,
    current_actor_id: str | None = None,
) -> EligibilityRuleDetail:
    current = ensure_eligibility_rule_exists(eligibility_rule_id)
    from app.modules.campaigns.service import ensure_campaign_owned_by_actor

    ensure_campaign_owned_by_actor(
        current.campaign_id,
        current_actor_id,
        resource="eligibility_rule",
    )

    updated = replace(
        current,
        platform=payload.platform.value if payload.platform is not None else current.platform,
        os_name=payload.os_name if payload.os_name is not None else current.os_name,
        os_version_min=(
            payload.os_version_min
            if payload.os_version_min is not None
            else current.os_version_min
        ),
        os_version_max=(
            payload.os_version_max
            if payload.os_version_max is not None
            else current.os_version_max
        ),
        install_channel=(
            payload.install_channel
            if payload.install_channel is not None
            else current.install_channel
        ),
        is_active=payload.is_active if payload.is_active is not None else current.is_active,
        updated_at=_utc_now_iso(),
    )
    repository.update_eligibility_rule(updated)
    return _to_eligibility_rule_detail(updated)


def delete_eligibility_rule(eligibility_rule_id: str) -> None:
    ensure_eligibility_rule_exists(eligibility_rule_id)
    repository.delete_eligibility_rule(eligibility_rule_id)
