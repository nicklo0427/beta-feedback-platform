import type {
  AccountCollaborationSummary,
  AccountDetail
} from '~/features/accounts/types'
import type { CampaignDetail } from '~/features/campaigns/types'
import type { DeviceProfileDetail } from '~/features/device-profiles/types'
import type { CampaignQualificationResultItem } from '~/features/eligibility/types'
import type {
  CampaignReputationSummary,
  DeviceProfileReputationSummary
} from '~/features/reputation/types'
import type { TaskStatus } from '~/features/tasks/types'
import type { AppLocale } from '~/features/i18n/use-app-i18n'

export type ParticipationRequestStatus =
  | 'pending'
  | 'accepted'
  | 'declined'
  | 'withdrawn'

export type ParticipationAssignmentStatus = 'not_assigned' | 'task_created'

const PARTICIPATION_REQUEST_STATUS_LABELS: Record<
  AppLocale,
  Record<ParticipationRequestStatus, string>
> = {
  'zh-TW': {
    pending: '待處理',
    accepted: '已接受',
    declined: '已婉拒',
    withdrawn: '已撤回'
  },
  en: {
    pending: 'Pending',
    accepted: 'Accepted',
    declined: 'Declined',
    withdrawn: 'Withdrawn'
  }
}

export function formatParticipationRequestStatusLabel(
  value: ParticipationRequestStatus,
  locale: AppLocale = 'zh-TW'
): string {
  return PARTICIPATION_REQUEST_STATUS_LABELS[locale][value]
}

const PARTICIPATION_ASSIGNMENT_STATUS_LABELS: Record<
  AppLocale,
  Record<ParticipationAssignmentStatus, string>
> = {
  'zh-TW': {
    not_assigned: '尚未建立任務',
    task_created: '已建立任務'
  },
  en: {
    not_assigned: 'Task not created',
    task_created: 'Task created'
  }
}

export function formatParticipationAssignmentStatusLabel(
  value: ParticipationAssignmentStatus,
  locale: AppLocale = 'zh-TW'
): string {
  return PARTICIPATION_ASSIGNMENT_STATUS_LABELS[locale][value]
}

export interface ParticipationRequestListItem {
  id: string
  campaign_id: string
  campaign_name: string
  tester_account_id: string
  device_profile_id: string
  device_profile_name: string
  status: ParticipationRequestStatus
  note: string | null
  decision_note: string | null
  created_at: string
  updated_at: string
  decided_at: string | null
  linked_task_id: string | null
  assignment_created_at: string | null
  assignment_status: ParticipationAssignmentStatus
}

export interface ParticipationRequestDetail extends ParticipationRequestListItem {}

export interface ParticipationRequestEnrichedDetail
  extends ParticipationRequestDetail {
  tester_account: AccountDetail
  tester_account_summary: AccountCollaborationSummary
  device_profile: DeviceProfileDetail
  device_profile_reputation: DeviceProfileReputationSummary
  qualification_snapshot: CampaignQualificationResultItem
  campaign: CampaignDetail
  campaign_reputation: CampaignReputationSummary
}

export interface ParticipationRequestFormValues {
  device_profile_id: string
  note: string
}

export interface ParticipationRequestCreatePayload {
  device_profile_id: string
  note: string | null
}

export type ParticipationRequestDecisionStatus = 'accepted' | 'declined'

export interface ParticipationRequestDecisionPayload {
  status: ParticipationRequestDecisionStatus
  decision_note: string | null
}

export interface ParticipationRequestTaskCreatePayload {
  title: string
  instruction_summary: string | null
  status: TaskStatus
}

export interface ParticipationRequestQualifiedDeviceProfileOption {
  id: string
  name: string
}
