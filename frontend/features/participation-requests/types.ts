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

export type ParticipationRequestStatus =
  | 'pending'
  | 'accepted'
  | 'declined'
  | 'withdrawn'

const PARTICIPATION_REQUEST_STATUS_LABELS: Record<
  ParticipationRequestStatus,
  string
> = {
  pending: '待處理',
  accepted: '已接受',
  declined: '已婉拒',
  withdrawn: '已撤回'
}

export function formatParticipationRequestStatusLabel(
  value: ParticipationRequestStatus
): string {
  return PARTICIPATION_REQUEST_STATUS_LABELS[value]
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

export interface ParticipationRequestQualifiedDeviceProfileOption {
  id: string
  name: string
}
