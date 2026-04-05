import type { ListResponse } from '~/services/api/client'

import { buildCurrentActorHeaders } from '~/features/accounts/current-actor'
import { useApiClient } from '~/services/api/client'

import type {
  FeedbackCreatePayload,
  FeedbackDetail,
  FeedbackListItem,
  FeedbackQueueFilters,
  FeedbackQueueItem,
  FeedbackUpdatePayload
} from './types'

export async function fetchTaskFeedback(
  taskId: string
): Promise<ListResponse<FeedbackListItem>> {
  const { request } = useApiClient()
  return request<ListResponse<FeedbackListItem>>(`/tasks/${taskId}/feedback`)
}

export async function fetchFeedbackQueue(
  filters: FeedbackQueueFilters = {}
): Promise<ListResponse<FeedbackQueueItem>> {
  const { request } = useApiClient()
  const query = new URLSearchParams()

  if (filters.mine) {
    query.set('mine', 'true')
  }

  if (filters.reviewStatus) {
    query.set('review_status', filters.reviewStatus)
  }

  const suffix = query.toString() ? `?${query.toString()}` : ''

  return request<ListResponse<FeedbackQueueItem>>(`/feedback${suffix}`, {
    headers: buildCurrentActorHeaders(filters.actorId)
  })
}

export async function fetchFeedbackDetail(
  feedbackId: string
): Promise<FeedbackDetail> {
  const { request } = useApiClient()
  return request<FeedbackDetail>(`/feedback/${feedbackId}`)
}

export async function createFeedback(
  taskId: string,
  payload: FeedbackCreatePayload,
  actorId?: string | null
): Promise<FeedbackDetail> {
  const { request } = useApiClient()
  return request<FeedbackDetail>(`/tasks/${taskId}/feedback`, {
    method: 'POST',
    body: payload,
    headers: buildCurrentActorHeaders(actorId)
  })
}

export async function updateFeedback(
  feedbackId: string,
  payload: FeedbackUpdatePayload,
  actorId?: string | null
): Promise<FeedbackDetail> {
  const { request } = useApiClient()
  return request<FeedbackDetail>(`/feedback/${feedbackId}`, {
    method: 'PATCH',
    body: payload,
    headers: buildCurrentActorHeaders(actorId)
  })
}
