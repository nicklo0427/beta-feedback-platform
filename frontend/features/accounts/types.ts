import type { CampaignStatus } from '~/features/campaigns/types'
import type { FeedbackReviewStatus } from '~/features/feedback/types'
import type { AppLocale } from '~/features/i18n/use-app-i18n'
import type { PlatformDisplayValue } from '~/features/platform-display'
import type { TaskStatus } from '~/features/tasks/types'

export type AccountRole = 'developer' | 'tester'

export const ACCOUNT_ROLE_OPTIONS: AccountRole[] = ['developer', 'tester']

const ACCOUNT_ROLE_LABELS: Record<AppLocale, Record<AccountRole, string>> = {
  'zh-TW': {
    developer: '開發者',
    tester: '測試者'
  },
  en: {
    developer: 'Developer',
    tester: 'Tester'
  }
}

export function formatAccountRoleLabel(
  role: string,
  locale: AppLocale = 'zh-TW'
): string {
  const labels = ACCOUNT_ROLE_LABELS[locale]

  if (role in labels) {
    return labels[role as AccountRole]
  }

  return role
}

export interface AccountListItem {
  id: string
  display_name: string
  role: AccountRole
  updated_at: string
}

export interface AccountDetail {
  id: string
  display_name: string
  role: AccountRole
  bio: string | null
  locale: string | null
  created_at: string
  updated_at: string
}

export interface AccountRecentProject {
  id: string
  name: string
  updated_at: string
}

export interface AccountRecentCampaign {
  id: string
  project_id: string
  name: string
  status: CampaignStatus
  updated_at: string
}

export interface AccountRecentDeviceProfile {
  id: string
  name: string
  platform: PlatformDisplayValue
  updated_at: string
}

export interface AccountRecentTask {
  id: string
  campaign_id: string
  title: string
  status: TaskStatus
  updated_at: string
}

export interface AccountRecentFeedback {
  id: string
  task_id: string
  summary: string
  review_status: FeedbackReviewStatus
  submitted_at: string
}

export interface DeveloperAccountSummary {
  owned_projects_count: number
  owned_campaigns_count: number
  feedback_to_review_count: number
  recent_projects: AccountRecentProject[]
  recent_campaigns: AccountRecentCampaign[]
}

export interface TesterAccountSummary {
  owned_device_profiles_count: number
  assigned_tasks_count: number
  submitted_feedback_count: number
  recent_device_profiles: AccountRecentDeviceProfile[]
  recent_tasks: AccountRecentTask[]
  recent_feedback: AccountRecentFeedback[]
}

export interface AccountCollaborationSummary {
  account_id: string
  role: AccountRole
  developer_summary: DeveloperAccountSummary | null
  tester_summary: TesterAccountSummary | null
  updated_at: string
}

export interface AccountFormValues {
  display_name: string
  role: AccountRole | ''
  bio: string
  locale: string
}

export interface AccountCreatePayload {
  display_name: string
  role: AccountRole
  bio: string | null
  locale: string | null
}

export interface AccountUpdatePayload {
  display_name?: string
  role?: AccountRole
  bio?: string | null
  locale?: string | null
}
