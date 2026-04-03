import type { ListResponse } from '~/services/api/client'

import { useApiClient } from '~/services/api/client'

import type {
  FeedbackCreatePayload,
  FeedbackDetail,
  FeedbackListItem,
  FeedbackUpdatePayload
} from './types'

export async function fetchTaskFeedback(
  taskId: string
): Promise<ListResponse<FeedbackListItem>> {
  const { request } = useApiClient()
  return request<ListResponse<FeedbackListItem>>(`/tasks/${taskId}/feedback`)
}

export async function fetchFeedbackDetail(
  feedbackId: string
): Promise<FeedbackDetail> {
  const { request } = useApiClient()
  return request<FeedbackDetail>(`/feedback/${feedbackId}`)
}

export async function createFeedback(
  taskId: string,
  payload: FeedbackCreatePayload
): Promise<FeedbackDetail> {
  const { request } = useApiClient()
  return request<FeedbackDetail>(`/tasks/${taskId}/feedback`, {
    method: 'POST',
    body: payload
  })
}

export async function updateFeedback(
  feedbackId: string,
  payload: FeedbackUpdatePayload
): Promise<FeedbackDetail> {
  const { request } = useApiClient()
  return request<FeedbackDetail>(`/feedback/${feedbackId}`, {
    method: 'PATCH',
    body: payload
  })
}
