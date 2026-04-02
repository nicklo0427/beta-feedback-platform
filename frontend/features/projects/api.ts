import type { ListResponse } from '~/services/api/client'

import { useApiClient } from '~/services/api/client'

import type { ProjectDetail, ProjectListItem } from './types'

export async function fetchProjects(): Promise<ListResponse<ProjectListItem>> {
  const { request } = useApiClient()
  return request<ListResponse<ProjectListItem>>('/projects')
}

export async function fetchProjectDetail(projectId: string): Promise<ProjectDetail> {
  const { request } = useApiClient()
  return request<ProjectDetail>(`/projects/${projectId}`)
}
