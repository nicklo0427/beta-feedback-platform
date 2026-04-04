import type { ListResponse } from '~/services/api/client'

import { useApiClient } from '~/services/api/client'

import type {
  ProjectCreatePayload,
  ProjectDetail,
  ProjectListItem,
  ProjectUpdatePayload
} from './types'

export async function fetchProjects(): Promise<ListResponse<ProjectListItem>> {
  const { request } = useApiClient()
  return request<ListResponse<ProjectListItem>>('/projects')
}

export async function fetchProjectDetail(projectId: string): Promise<ProjectDetail> {
  const { request } = useApiClient()
  return request<ProjectDetail>(`/projects/${projectId}`)
}

export async function createProject(
  payload: ProjectCreatePayload
): Promise<ProjectDetail> {
  const { request } = useApiClient()
  return request<ProjectDetail>('/projects', {
    method: 'POST',
    body: payload
  })
}

export async function updateProject(
  projectId: string,
  payload: ProjectUpdatePayload
): Promise<ProjectDetail> {
  const { request } = useApiClient()
  return request<ProjectDetail>(`/projects/${projectId}`, {
    method: 'PATCH',
    body: payload
  })
}
