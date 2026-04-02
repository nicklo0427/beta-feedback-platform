import type { ListResponse } from '~/services/api/client'

import { useApiClient } from '~/services/api/client'

import type { CampaignDetail, CampaignListItem } from './types'

export async function fetchCampaigns(
  projectId?: string
): Promise<ListResponse<CampaignListItem>> {
  const { request } = useApiClient()
  const query = projectId ? `?project_id=${encodeURIComponent(projectId)}` : ''

  return request<ListResponse<CampaignListItem>>(`/campaigns${query}`)
}

export async function fetchCampaignDetail(
  campaignId: string
): Promise<CampaignDetail> {
  const { request } = useApiClient()
  return request<CampaignDetail>(`/campaigns/${campaignId}`)
}
