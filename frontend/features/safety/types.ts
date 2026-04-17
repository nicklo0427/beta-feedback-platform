import type { AppLocale } from '~/features/i18n/use-app-i18n'

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

const DISTRIBUTION_CHANNEL_LABELS: Record<
  AppLocale,
  Record<DistributionChannel, string>
> = {
  'zh-TW': {
    web_url: '網頁連結',
    pwa_url: 'PWA 連結',
    testflight: 'TestFlight',
    google_play_testing: 'Google Play 測試',
    manual_invite: '手動邀請',
    other: '其他'
  },
  en: {
    web_url: 'Web URL',
    pwa_url: 'PWA URL',
    testflight: 'TestFlight',
    google_play_testing: 'Google Play testing',
    manual_invite: 'Manual invite',
    other: 'Other'
  }
}

const RISK_LEVEL_LABELS: Record<AppLocale, Record<RiskLevel, string>> = {
  'zh-TW': {
    low: '低',
    medium: '中',
    high: '高'
  },
  en: {
    low: 'Low',
    medium: 'Medium',
    high: 'High'
  }
}

const REVIEW_STATUS_LABELS: Record<AppLocale, Record<ReviewStatus, string>> = {
  'zh-TW': {
    pending: '待審核',
    approved: '已核准',
    rejected: '已拒絕'
  },
  en: {
    pending: 'Pending',
    approved: 'Approved',
    rejected: 'Rejected'
  }
}

export function formatDistributionChannelLabel(
  value: DistributionChannel,
  locale: AppLocale = 'zh-TW'
): string {
  return DISTRIBUTION_CHANNEL_LABELS[locale][value]
}

export function formatRiskLevelLabel(
  value: RiskLevel,
  locale: AppLocale = 'zh-TW'
): string {
  return RISK_LEVEL_LABELS[locale][value]
}

export function formatReviewStatusLabel(
  value: ReviewStatus,
  locale: AppLocale = 'zh-TW'
): string {
  return REVIEW_STATUS_LABELS[locale][value]
}
