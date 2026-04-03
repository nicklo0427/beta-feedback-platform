export type EligibilityRulePlatform = 'web' | 'h5' | 'pwa' | 'ios' | 'android'

export const ELIGIBILITY_RULE_PLATFORM_OPTIONS: EligibilityRulePlatform[] = [
  'web',
  'h5',
  'pwa',
  'ios',
  'android'
]

export interface EligibilityRuleListItem {
  id: string
  campaign_id: string
  platform: EligibilityRulePlatform
  os_name: string | null
  install_channel: string | null
  is_active: boolean
  updated_at: string
}

export interface EligibilityRuleDetail {
  id: string
  campaign_id: string
  platform: EligibilityRulePlatform
  os_name: string | null
  os_version_min: string | null
  os_version_max: string | null
  install_channel: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface EligibilityRuleFormValues {
  platform: EligibilityRulePlatform | ''
  os_name: string
  os_version_min: string
  os_version_max: string
  install_channel: string
  is_active: boolean
}

export interface EligibilityRuleCreatePayload {
  platform: EligibilityRulePlatform
  os_name: string | null
  os_version_min: string | null
  os_version_max: string | null
  install_channel: string | null
  is_active: boolean
}

export interface EligibilityRuleUpdatePayload {
  platform?: EligibilityRulePlatform
  os_name?: string | null
  os_version_min?: string | null
  os_version_max?: string | null
  install_channel?: string | null
  is_active?: boolean
}
