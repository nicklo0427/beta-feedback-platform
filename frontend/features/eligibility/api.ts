import type { ListResponse } from '~/services/api/client'

import { useApiClient } from '~/services/api/client'

import type { EligibilityRuleDetail, EligibilityRuleListItem } from './types'

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
