import type { ListResponse } from '~/services/api/client'

import { useApiClient } from '~/services/api/client'
import { buildCurrentActorHeaders } from '~/features/accounts/current-actor'

import type {
  ProjectCreatePayload,
  ProjectDetail,
  ProjectListItem,
  ProjectUpdatePayload
} from './types'

export interface ProjectListOptions {
  mine?: boolean
  actorId?: string | null
}

function buildProjectsListPath(options: ProjectListOptions = {}): string {
  const searchParams = new URLSearchParams()

  if (options.mine) {
    searchParams.set('mine', 'true')
  }

  const queryString = searchParams.toString()
  return queryString ? `/projects?${queryString}` : '/projects'
}

export async function fetchProjects(
  options: ProjectListOptions = {}
): Promise<ListResponse<ProjectListItem>> {
  const { request } = useApiClient()
  return request<ListResponse<ProjectListItem>>(buildProjectsListPath(options), {
    headers: buildCurrentActorHeaders(options.actorId)
  })
}

export async function fetchProjectDetail(projectId: string): Promise<ProjectDetail> {
  const { request } = useApiClient()
  return request<ProjectDetail>(`/projects/${projectId}`)
}

export async function createProject(
  payload: ProjectCreatePayload,
  actorId?: string | null
): Promise<ProjectDetail> {
  const { request } = useApiClient()
  return request<ProjectDetail>('/projects', {
    method: 'POST',
    body: payload,
    headers: buildCurrentActorHeaders(actorId)
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
