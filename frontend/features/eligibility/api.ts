import type { ListResponse } from '~/services/api/client'

import { useApiClient } from '~/services/api/client'
import { buildCurrentActorHeaders } from '~/features/accounts/current-actor'

import type {
  EligibilityRuleCreatePayload,
  EligibilityRuleDetail,
  EligibilityRuleListItem,
  EligibilityRuleUpdatePayload
} from './types'

export async function fetchCampaignEligibilityRules(
  campaignId: string
): Promise<ListResponse<EligibilityRuleListItem>> {
  const { request } = useApiClient()
  return request<ListResponse<EligibilityRuleListItem>>(
    `/campaigns/${campaignId}/eligibility-rules`
  )
}

export async function fetchEligibilityRuleDetail(
  eligibilityRuleId: string
): Promise<EligibilityRuleDetail> {
  const { request } = useApiClient()
  return request<EligibilityRuleDetail>(`/eligibility-rules/${eligibilityRuleId}`)
}

export async function createEligibilityRule(
  campaignId: string,
  payload: EligibilityRuleCreatePayload,
  actorId?: string | null
): Promise<EligibilityRuleDetail> {
  const { request } = useApiClient()
  return request<EligibilityRuleDetail>(`/campaigns/${campaignId}/eligibility-rules`, {
    method: 'POST',
    body: payload,
    headers: buildCurrentActorHeaders(actorId)
  })
}

export async function updateEligibilityRule(
  eligibilityRuleId: string,
  payload: EligibilityRuleUpdatePayload,
  actorId?: string | null
): Promise<EligibilityRuleDetail> {
  const { request } = useApiClient()
  return request<EligibilityRuleDetail>(`/eligibility-rules/${eligibilityRuleId}`, {
    method: 'PATCH',
    body: payload,
    headers: buildCurrentActorHeaders(actorId)
  })
}
