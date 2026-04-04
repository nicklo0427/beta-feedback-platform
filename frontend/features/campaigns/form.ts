import type {
  CampaignCreatePayload,
  CampaignDetail,
  CampaignFormValues,
  CampaignUpdatePayload,
  TargetPlatform
} from './types'

import { CAMPAIGN_TARGET_PLATFORM_OPTIONS } from './types'

function normalizeRequiredValue(value: string): string {
  return value.trim()
}

function normalizeOptionalValue(value: string): string | null {
  const normalized = value.trim()
  return normalized || null
}

function normalizeTargetPlatforms(platforms: TargetPlatform[]): TargetPlatform[] {
  const uniquePlatforms = new Set(platforms)

  return CAMPAIGN_TARGET_PLATFORM_OPTIONS.filter((platform) =>
    uniquePlatforms.has(platform)
  )
}

export function createEmptyCampaignFormValues(): CampaignFormValues {
  return {
    name: '',
    description: '',
    target_platforms: [],
    version_label: '',
    status: 'draft'
  }
}

export function toCampaignFormValues(campaign: CampaignDetail): CampaignFormValues {
  return {
    name: campaign.name,
    description: campaign.description ?? '',
    target_platforms: [...campaign.target_platforms],
    version_label: campaign.version_label ?? '',
    status: campaign.status
  }
}

export function buildCampaignCreatePayload(
  projectId: string,
  values: CampaignFormValues
): CampaignCreatePayload {
  return {
    project_id: normalizeRequiredValue(projectId),
    name: normalizeRequiredValue(values.name),
    description: normalizeOptionalValue(values.description),
    target_platforms: normalizeTargetPlatforms(values.target_platforms),
    version_label: normalizeOptionalValue(values.version_label)
  }
}

export function buildCampaignUpdatePayload(
  values: CampaignFormValues,
  initialValues: CampaignFormValues
): CampaignUpdatePayload | null {
  const payload: CampaignUpdatePayload = {}

  const currentName = normalizeRequiredValue(values.name)
  const initialName = normalizeRequiredValue(initialValues.name)
  if (currentName !== initialName) {
    payload.name = currentName
  }

  const currentDescription = normalizeOptionalValue(values.description)
  const initialDescription = normalizeOptionalValue(initialValues.description)
  if (currentDescription !== initialDescription) {
    payload.description = currentDescription
  }

  const currentPlatforms = normalizeTargetPlatforms(values.target_platforms)
  const initialPlatforms = normalizeTargetPlatforms(initialValues.target_platforms)
  if (JSON.stringify(currentPlatforms) !== JSON.stringify(initialPlatforms)) {
    payload.target_platforms = currentPlatforms
  }

  const currentVersionLabel = normalizeOptionalValue(values.version_label)
  const initialVersionLabel = normalizeOptionalValue(initialValues.version_label)
  if (currentVersionLabel !== initialVersionLabel) {
    payload.version_label = currentVersionLabel
  }

  if (values.status !== initialValues.status) {
    payload.status = values.status
  }

  if (Object.keys(payload).length === 0) {
    return null
  }

  return payload
}
