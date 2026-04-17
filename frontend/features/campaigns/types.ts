import type { AppLocale } from '~/features/i18n/use-app-i18n'

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

const CAMPAIGN_STATUS_LABELS: Record<AppLocale, Record<CampaignStatus, string>> = {
  'zh-TW': {
    draft: '草稿',
    active: '啟用中',
    closed: '已關閉'
  },
  en: {
    draft: 'Draft',
    active: 'Active',
    closed: 'Closed'
  }
}

export function formatCampaignStatusLabel(
  value: CampaignStatus,
  locale: AppLocale = 'zh-TW'
): string {
  return CAMPAIGN_STATUS_LABELS[locale][value]
}

export interface CampaignQualifyingDeviceProfileRef {
  id: string
  name: string
}

export type CampaignParticipationRequestStatus =
  | 'pending'
  | 'accepted'
  | 'declined'
  | 'withdrawn'

export type CampaignParticipationAssignmentStatus =
  | 'not_assigned'
  | 'task_created'

export interface CampaignParticipationRecentRequest {
  id: string
  tester_account_id: string
  tester_account_display_name: string
  device_profile_id: string
  device_profile_name: string
  status: CampaignParticipationRequestStatus
  linked_task_id: string | null
  assignment_status: CampaignParticipationAssignmentStatus
  created_at: string
}

export interface CampaignParticipationSummary {
  campaign_id: string
  pending_requests_count: number
  accepted_requests_count: number
  linked_tasks_count: number
  recent_participation_requests: CampaignParticipationRecentRequest[]
}

export interface CampaignListItem {
  id: string
  project_id: string
  name: string
  target_platforms: TargetPlatform[]
  version_label: string | null
  status: CampaignStatus
  updated_at: string
  qualifying_device_profiles?: CampaignQualifyingDeviceProfileRef[]
  qualification_summary?: string | null
  participation_summary?: CampaignParticipationSummary | null
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
