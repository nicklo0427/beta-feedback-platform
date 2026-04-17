import { ApiClientError, useApiClient } from '~/services/api/client'
import { buildCurrentActorHeaders } from '~/features/accounts/current-actor'

import type {
  CampaignSafetyCreatePayload,
  CampaignSafetyDetail,
  CampaignSafetyUpdatePayload
} from './types'

export async function fetchCampaignSafety(
  campaignId: string,
  actorId?: string | null
): Promise<CampaignSafetyDetail | null> {
  const { request } = useApiClient()

  try {
    return await request<CampaignSafetyDetail>(`/campaigns/${campaignId}/safety`, {
      headers: buildCurrentActorHeaders(actorId)
    })
  } catch (error) {
    if (error instanceof ApiClientError && error.code === 'resource_not_found') {
      return null
    }

    throw error
  }
}

export async function fetchCampaignSafetyDetail(
  campaignId: string,
  actorId?: string | null
): Promise<CampaignSafetyDetail> {
  const { request } = useApiClient()
  return request<CampaignSafetyDetail>(`/campaigns/${campaignId}/safety`, {
    headers: buildCurrentActorHeaders(actorId)
  })
}

export async function createCampaignSafety(
  campaignId: string,
  payload: CampaignSafetyCreatePayload,
  actorId?: string | null
): Promise<CampaignSafetyDetail> {
  const { request } = useApiClient()
  return request<CampaignSafetyDetail>(`/campaigns/${campaignId}/safety`, {
    method: 'POST',
    body: payload,
    headers: buildCurrentActorHeaders(actorId)
  })
}

export async function updateCampaignSafety(
  campaignId: string,
  payload: CampaignSafetyUpdatePayload,
  actorId?: string | null
): Promise<CampaignSafetyDetail> {
  const { request } = useApiClient()
  return request<CampaignSafetyDetail>(`/campaigns/${campaignId}/safety`, {
    method: 'PATCH',
    body: payload,
    headers: buildCurrentActorHeaders(actorId)
  })
}
