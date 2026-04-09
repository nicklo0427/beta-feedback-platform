import type { ListResponse } from '~/services/api/client'

import { useApiClient } from '~/services/api/client'
import { buildCurrentActorHeaders } from '~/features/accounts/current-actor'

import type {
  CampaignCreatePayload,
  CampaignDetail,
  CampaignListItem,
  CampaignUpdatePayload
} from './types'

export interface CampaignListOptions {
  projectId?: string
  mine?: boolean
  qualifiedForMe?: boolean
  actorId?: string | null
}

export async function fetchCampaigns(
  options: CampaignListOptions = {}
): Promise<ListResponse<CampaignListItem>> {
  const { request } = useApiClient()
  const searchParams = new URLSearchParams()

  if (options.projectId) {
    searchParams.set('project_id', options.projectId)
  }

  if (options.mine) {
    searchParams.set('mine', 'true')
  }

  if (options.qualifiedForMe) {
    searchParams.set('qualified_for_me', 'true')
  }

  const query = searchParams.toString()

  return request<ListResponse<CampaignListItem>>(
    `/campaigns${query ? `?${query}` : ''}`,
    {
      headers: buildCurrentActorHeaders(options.actorId)
    }
  )
}

export async function fetchCampaignDetail(
  campaignId: string
): Promise<CampaignDetail> {
  const { request } = useApiClient()
  return request<CampaignDetail>(`/campaigns/${campaignId}`)
}

export async function createCampaign(
  payload: CampaignCreatePayload,
  actorId?: string | null
): Promise<CampaignDetail> {
  const { request } = useApiClient()
  return request<CampaignDetail>('/campaigns', {
    method: 'POST',
    body: payload,
    headers: buildCurrentActorHeaders(actorId)
  })
}

export async function updateCampaign(
  campaignId: string,
  payload: CampaignUpdatePayload,
  actorId?: string | null
): Promise<CampaignDetail> {
  const { request } = useApiClient()
  return request<CampaignDetail>(`/campaigns/${campaignId}`, {
    method: 'PATCH',
    body: payload,
    headers: buildCurrentActorHeaders(actorId)
  })
}
