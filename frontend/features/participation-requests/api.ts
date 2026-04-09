import type { ListResponse } from '~/services/api/client'

import { buildCurrentActorHeaders } from '~/features/accounts/current-actor'
import { useApiClient } from '~/services/api/client'

import type {
  ParticipationRequestCreatePayload,
  ParticipationRequestDecisionPayload,
  ParticipationRequestDetail,
  ParticipationRequestEnrichedDetail,
  ParticipationRequestListItem
} from './types'

export async function fetchMyParticipationRequests(
  actorId?: string | null
): Promise<ListResponse<ParticipationRequestListItem>> {
  const { request } = useApiClient()
  return request<ListResponse<ParticipationRequestListItem>>(
    '/participation-requests?mine=true',
    {
      headers: buildCurrentActorHeaders(actorId)
    }
  )
}

export async function fetchReviewParticipationRequests(
  actorId?: string | null
): Promise<ListResponse<ParticipationRequestListItem>> {
  const { request } = useApiClient()
  return request<ListResponse<ParticipationRequestListItem>>(
    '/participation-requests?review_mine=true',
    {
      headers: buildCurrentActorHeaders(actorId)
    }
  )
}

export async function fetchParticipationRequestDetail(
  requestId: string,
  actorId?: string | null
): Promise<ParticipationRequestEnrichedDetail> {
  const { request } = useApiClient()
  return request<ParticipationRequestEnrichedDetail>(
    `/participation-requests/${requestId}`,
    {
      headers: buildCurrentActorHeaders(actorId)
    }
  )
}

export async function createParticipationRequest(
  campaignId: string,
  payload: ParticipationRequestCreatePayload,
  actorId?: string | null
): Promise<ParticipationRequestDetail> {
  const { request } = useApiClient()
  return request<ParticipationRequestDetail>(
    `/campaigns/${campaignId}/participation-requests`,
    {
      method: 'POST',
      body: payload,
      headers: buildCurrentActorHeaders(actorId)
    }
  )
}

export async function withdrawParticipationRequest(
  requestId: string,
  actorId?: string | null
): Promise<ParticipationRequestDetail> {
  const { request } = useApiClient()
  return request<ParticipationRequestDetail>(`/participation-requests/${requestId}`, {
    method: 'PATCH',
    body: {
      status: 'withdrawn'
    },
    headers: buildCurrentActorHeaders(actorId)
  })
}

export async function decideParticipationRequest(
  requestId: string,
  payload: ParticipationRequestDecisionPayload,
  actorId?: string | null
): Promise<ParticipationRequestDetail> {
  const { request } = useApiClient()
  return request<ParticipationRequestDetail>(`/participation-requests/${requestId}`, {
    method: 'PATCH',
    body: payload,
    headers: buildCurrentActorHeaders(actorId)
  })
}
