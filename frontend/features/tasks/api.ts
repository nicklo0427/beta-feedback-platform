import type { ListResponse } from '~/services/api/client'

import { buildCurrentActorHeaders } from '~/features/accounts/current-actor'
import { useApiClient } from '~/services/api/client'

import type {
  TaskAssignmentQualificationPreview,
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
  mine?: boolean
  actorId?: string | null
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

  if (filters.mine) {
    params.set('mine', 'true')
  }

  const query = params.toString()

  return request<ListResponse<TaskListItem>>(`/tasks${query ? `?${query}` : ''}`, {
    headers: buildCurrentActorHeaders(filters.actorId)
  })
}

export async function fetchTaskDetail(taskId: string): Promise<TaskDetail> {
  const { request } = useApiClient()
  return request<TaskDetail>(`/tasks/${taskId}`)
}

export async function createTask(
  campaignId: string,
  payload: TaskCreatePayload,
  actorId?: string | null
): Promise<TaskDetail> {
  const { request } = useApiClient()
  return request<TaskDetail>(`/campaigns/${campaignId}/tasks`, {
    method: 'POST',
    body: payload,
    headers: buildCurrentActorHeaders(actorId)
  })
}

export async function updateTask(
  taskId: string,
  payload: TaskUpdatePayload,
  actorId?: string | null
): Promise<TaskDetail> {
  const { request } = useApiClient()
  return request<TaskDetail>(`/tasks/${taskId}`, {
    method: 'PATCH',
    body: payload,
    headers: buildCurrentActorHeaders(actorId)
  })
}

export async function startAssignedTask(
  taskId: string,
  actorId?: string | null
): Promise<TaskDetail> {
  return updateTask(taskId, {
    status: 'in_progress'
  }, actorId)
}

export async function fetchTaskAssignmentQualificationPreview(
  campaignId: string,
  deviceProfileId: string,
  actorId?: string | null
): Promise<TaskAssignmentQualificationPreview> {
  const { request } = useApiClient()
  const params = new URLSearchParams({
    device_profile_id: deviceProfileId
  })

  return request<TaskAssignmentQualificationPreview>(
    `/campaigns/${campaignId}/qualification-check?${params.toString()}`,
    {
      headers: buildCurrentActorHeaders(actorId)
    }
  )
}
