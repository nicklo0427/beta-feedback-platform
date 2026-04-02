export type TargetPlatform = 'web' | 'h5' | 'pwa' | 'ios' | 'android'

export type CampaignStatus = 'draft' | 'active' | 'closed'

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
