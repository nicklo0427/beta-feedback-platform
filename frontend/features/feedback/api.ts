import type { ListResponse } from '~/services/api/client'

import { useApiClient } from '~/services/api/client'

import type { FeedbackDetail, FeedbackListItem } from './types'

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
