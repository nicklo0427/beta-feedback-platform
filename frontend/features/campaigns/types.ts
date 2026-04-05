export type TargetPlatform = 'web' | 'h5' | 'pwa' | 'ios' | 'android'

export type CampaignStatus = 'draft' | 'active' | 'closed'

export const CAMPAIGN_TARGET_PLATFORM_OPTIONS: TargetPlatform[] = [
  'web',
  'h5',
  'pwa',
  'ios',
  'android'
]

export const CAMPAIGN_STATUSES: CampaignStatus[] = [
  'draft',
  'active',
  'closed'
]

const CAMPAIGN_STATUS_LABELS: Record<CampaignStatus, string> = {
  draft: '草稿',
  active: '啟用中',
  closed: '已關閉'
}

export function formatCampaignStatusLabel(value: CampaignStatus): string {
  return CAMPAIGN_STATUS_LABELS[value]
}

export interface CampaignListItem {
  id: string
  project_id: string
  name: string
  target_platforms: TargetPlatform[]
  version_label: string | null
  status: CampaignStatus
  updated_at: string
}

export interface CampaignDetail {
  id: string
  project_id: string
  name: string
  description: string | null
  target_platforms: TargetPlatform[]
  version_label: string | null
  status: CampaignStatus
  created_at: string
  updated_at: string
}

export interface CampaignFormValues {
  name: string
  description: string
  target_platforms: TargetPlatform[]
  version_label: string
  status: CampaignStatus
}

export interface CampaignCreatePayload {
  project_id: string
  name: string
  description: string | null
  target_platforms: TargetPlatform[]
  version_label: string | null
}

export interface CampaignUpdatePayload {
  name?: string
  description?: string | null
  target_platforms?: TargetPlatform[]
  version_label?: string | null
  status?: CampaignStatus
}
