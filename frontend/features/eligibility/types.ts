import type { AppLocale } from '~/features/i18n/use-app-i18n'

export type EligibilityRulePlatform = 'web' | 'h5' | 'pwa' | 'ios' | 'android'
export type QualificationStatus = 'qualified' | 'not_qualified'

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

export interface CampaignQualificationResultItem {
  device_profile_id: string
  device_profile_name: string
  qualification_status: QualificationStatus
  matched_rule_id: string | null
  reason_codes: string[]
  reason_summary: string | null
}

export const QUALIFICATION_STATUS_LABELS: Record<
  AppLocale,
  Record<QualificationStatus, string>
> = {
  'zh-TW': {
    qualified: '符合資格',
    not_qualified: '不符合資格'
  },
  en: {
    qualified: 'Qualified',
    not_qualified: 'Not qualified'
  }
}

export function formatQualificationStatusLabel(
  status: QualificationStatus,
  locale: AppLocale = 'zh-TW'
): string {
  return QUALIFICATION_STATUS_LABELS[locale][status]
}
