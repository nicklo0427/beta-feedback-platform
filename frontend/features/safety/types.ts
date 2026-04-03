export type DistributionChannel =
  | 'web_url'
  | 'pwa_url'
  | 'testflight'
  | 'google_play_testing'
  | 'manual_invite'
  | 'other'

export type RiskLevel = 'low' | 'medium' | 'high'

export type ReviewStatus = 'pending' | 'approved' | 'rejected'

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
