export type DistributionChannel =
  | 'web_url'
  | 'pwa_url'
  | 'testflight'
  | 'google_play_testing'
  | 'manual_invite'
  | 'other'

export type RiskLevel = 'low' | 'medium' | 'high'

export type ReviewStatus = 'pending' | 'approved' | 'rejected'

export const DISTRIBUTION_CHANNEL_OPTIONS: DistributionChannel[] = [
  'web_url',
  'pwa_url',
  'testflight',
  'google_play_testing',
  'manual_invite',
  'other'
]

export const RISK_LEVEL_OPTIONS: RiskLevel[] = ['low', 'medium', 'high']

export const REVIEW_STATUS_OPTIONS: ReviewStatus[] = [
  'pending',
  'approved',
  'rejected'
]

export interface CampaignSafetyDetail {
  id: string
  campaign_id: string
  distribution_channel: DistributionChannel
  source_label: string
  source_url: string | null
  risk_level: RiskLevel
  review_status: ReviewStatus
  official_channel_only: boolean
  risk_note: string | null
  created_at: string
  updated_at: string
}

export interface CampaignSafetyFormValues {
  distribution_channel: DistributionChannel | ''
  source_label: string
  source_url: string
  risk_level: RiskLevel | ''
  review_status: ReviewStatus
  official_channel_only: boolean
  risk_note: string
}

export interface CampaignSafetyCreatePayload {
  distribution_channel: DistributionChannel
  source_label: string
  source_url: string | null
  risk_level: RiskLevel
  review_status: ReviewStatus
  official_channel_only: boolean
  risk_note: string | null
}

export interface CampaignSafetyUpdatePayload {
  distribution_channel?: DistributionChannel
  source_label?: string
  source_url?: string | null
  risk_level?: RiskLevel
  review_status?: ReviewStatus
  official_channel_only?: boolean
  risk_note?: string | null
}

const DISTRIBUTION_CHANNEL_LABELS: Record<DistributionChannel, string> = {
  web_url: 'Web URL',
  pwa_url: 'PWA URL',
  testflight: 'TestFlight',
  google_play_testing: 'Google Play Testing',
  manual_invite: 'Manual Invite',
  other: 'Other'
}

export function formatDistributionChannelLabel(value: DistributionChannel): string {
  return DISTRIBUTION_CHANNEL_LABELS[value]
}

export function formatRiskLevelLabel(value: RiskLevel): string {
  return value
}

export function formatReviewStatusLabel(value: ReviewStatus): string {
  return value
}
