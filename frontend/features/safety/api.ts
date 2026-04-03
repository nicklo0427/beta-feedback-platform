import { ApiClientError, useApiClient } from '~/services/api/client'

import type { CampaignSafetyDetail } from './types'

export async function fetchCampaignSafety(
  campaignId: string
): Promise<CampaignSafetyDetail | null> {
  const { request } = useApiClient()

  try {
    return await request<CampaignSafetyDetail>(`/campaigns/${campaignId}/safety`)
  } catch (error) {
    if (error instanceof ApiClientError && error.code === 'resource_not_found') {
      return null
    }

    throw error
  }
}
