import type { ListResponse } from '~/services/api/client'

import { useApiClient } from '~/services/api/client'

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
  payload: EligibilityRuleCreatePayload
): Promise<EligibilityRuleDetail> {
  const { request } = useApiClient()
  return request<EligibilityRuleDetail>(`/campaigns/${campaignId}/eligibility-rules`, {
    method: 'POST',
    body: payload
  })
}

export async function updateEligibilityRule(
  eligibilityRuleId: string,
  payload: EligibilityRuleUpdatePayload
): Promise<EligibilityRuleDetail> {
  const { request } = useApiClient()
  return request<EligibilityRuleDetail>(`/eligibility-rules/${eligibilityRuleId}`, {
    method: 'PATCH',
    body: payload
  })
}
