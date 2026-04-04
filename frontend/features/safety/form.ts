import type {
  CampaignSafetyCreatePayload,
  CampaignSafetyDetail,
  CampaignSafetyFormValues,
  CampaignSafetyUpdatePayload,
  DistributionChannel,
  RiskLevel
} from './types'

function normalizeRequiredValue(value: string): string {
  return value.trim()
}

function normalizeOptionalValue(value: string): string | null {
  const normalized = value.trim()
  return normalized || null
}

export function createEmptyCampaignSafetyFormValues(): CampaignSafetyFormValues {
  return {
    distribution_channel: '',
    source_label: '',
    source_url: '',
    risk_level: '',
    review_status: 'pending',
    official_channel_only: false,
    risk_note: ''
  }
}

export function toCampaignSafetyFormValues(
  safety: CampaignSafetyDetail
): CampaignSafetyFormValues {
  return {
    distribution_channel: safety.distribution_channel,
    source_label: safety.source_label,
    source_url: safety.source_url ?? '',
    risk_level: safety.risk_level,
    review_status: safety.review_status,
    official_channel_only: safety.official_channel_only,
    risk_note: safety.risk_note ?? ''
  }
}

export function buildCampaignSafetyCreatePayload(
  values: CampaignSafetyFormValues
): CampaignSafetyCreatePayload {
  return {
    distribution_channel: values.distribution_channel as DistributionChannel,
    source_label: normalizeRequiredValue(values.source_label),
    source_url: normalizeOptionalValue(values.source_url),
    risk_level: values.risk_level as RiskLevel,
    review_status: values.review_status,
    official_channel_only: values.official_channel_only,
    risk_note: normalizeOptionalValue(values.risk_note)
  }
}

export function buildCampaignSafetyUpdatePayload(
  values: CampaignSafetyFormValues,
  initialValues: CampaignSafetyFormValues
): CampaignSafetyUpdatePayload | null {
  const payload: CampaignSafetyUpdatePayload = {}

  if (values.distribution_channel !== initialValues.distribution_channel) {
    payload.distribution_channel = values.distribution_channel as DistributionChannel
  }

  const currentSourceLabel = normalizeRequiredValue(values.source_label)
  const initialSourceLabel = normalizeRequiredValue(initialValues.source_label)
  if (currentSourceLabel !== initialSourceLabel) {
    payload.source_label = currentSourceLabel
  }

  const currentSourceUrl = normalizeOptionalValue(values.source_url)
  const initialSourceUrl = normalizeOptionalValue(initialValues.source_url)
  if (currentSourceUrl !== initialSourceUrl) {
    payload.source_url = currentSourceUrl
  }

  if (values.risk_level !== initialValues.risk_level) {
    payload.risk_level = values.risk_level as RiskLevel
  }

  if (values.review_status !== initialValues.review_status) {
    payload.review_status = values.review_status
  }

  if (values.official_channel_only !== initialValues.official_channel_only) {
    payload.official_channel_only = values.official_channel_only
  }

  const currentRiskNote = normalizeOptionalValue(values.risk_note)
  const initialRiskNote = normalizeOptionalValue(initialValues.risk_note)
  if (currentRiskNote !== initialRiskNote) {
    payload.risk_note = currentRiskNote
  }

  if (Object.keys(payload).length === 0) {
    return null
  }

  return payload
}
