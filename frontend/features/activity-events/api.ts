import type { ListResponse } from '~/services/api/client'

import { buildCurrentActorHeaders } from '~/features/accounts/current-actor'
import { useApiClient } from '~/services/api/client'

import type { ActivityEventItem } from './types'

export async function fetchParticipationRequestTimeline(
  requestId: string,
  actorId?: string | null
): Promise<ListResponse<ActivityEventItem>> {
  const { request } = useApiClient()
  return request<ListResponse<ActivityEventItem>>(
    `/participation-requests/${requestId}/timeline`,
    {
      headers: buildCurrentActorHeaders(actorId)
    }
  )
}

export async function fetchTaskTimeline(
  taskId: string,
  actorId?: string | null
): Promise<ListResponse<ActivityEventItem>> {
  const { request } = useApiClient()
  return request<ListResponse<ActivityEventItem>>(`/tasks/${taskId}/timeline`, {
    headers: buildCurrentActorHeaders(actorId)
  })
}

export async function fetchFeedbackTimeline(
  feedbackId: string,
  actorId?: string | null
): Promise<ListResponse<ActivityEventItem>> {
  const { request } = useApiClient()
  return request<ListResponse<ActivityEventItem>>(`/feedback/${feedbackId}/timeline`, {
    headers: buildCurrentActorHeaders(actorId)
  })
}
