import type { ListResponse } from '~/services/api/client'

import { useApiClient } from '~/services/api/client'

import type {
  TaskCreatePayload,
  TaskDetail,
  TaskListItem,
  TaskStatus,
  TaskUpdatePayload
} from './types'

export interface TaskListFilters {
  campaignId?: string
  deviceProfileId?: string
  status?: TaskStatus
}

export async function fetchTasks(
  filters: TaskListFilters = {}
): Promise<ListResponse<TaskListItem>> {
  const { request } = useApiClient()
  const params = new URLSearchParams()

  if (filters.campaignId) {
    params.set('campaign_id', filters.campaignId)
  }

  if (filters.deviceProfileId) {
    params.set('device_profile_id', filters.deviceProfileId)
  }

  if (filters.status) {
    params.set('status', filters.status)
  }

  const query = params.toString()

  return request<ListResponse<TaskListItem>>(`/tasks${query ? `?${query}` : ''}`)
}

export async function fetchTaskDetail(taskId: string): Promise<TaskDetail> {
  const { request } = useApiClient()
  return request<TaskDetail>(`/tasks/${taskId}`)
}

export async function createTask(
  campaignId: string,
  payload: TaskCreatePayload
): Promise<TaskDetail> {
  const { request } = useApiClient()
  return request<TaskDetail>(`/campaigns/${campaignId}/tasks`, {
    method: 'POST',
    body: payload
  })
}

export async function updateTask(
  taskId: string,
  payload: TaskUpdatePayload
): Promise<TaskDetail> {
  const { request } = useApiClient()
  return request<TaskDetail>(`/tasks/${taskId}`, {
    method: 'PATCH',
    body: payload
  })
}
