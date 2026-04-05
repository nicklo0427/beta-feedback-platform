import type { ListResponse } from '~/services/api/client'

import { buildCurrentActorHeaders } from '~/features/accounts/current-actor'
import { useApiClient } from '~/services/api/client'

import type {
  DeviceProfileCreatePayload,
  DeviceProfileDetail,
  DeviceProfileListItem,
  DeviceProfileUpdatePayload
} from './types'

export interface DeviceProfileListOptions {
  mine?: boolean
  actorId?: string | null
}

function buildDeviceProfilesListPath(options: DeviceProfileListOptions = {}): string {
  const searchParams = new URLSearchParams()

  if (options.mine) {
    searchParams.set('mine', 'true')
  }

  const queryString = searchParams.toString()
  return queryString ? `/device-profiles?${queryString}` : '/device-profiles'
}

export async function fetchDeviceProfiles(
  options: DeviceProfileListOptions = {}
): Promise<ListResponse<DeviceProfileListItem>> {
  const { request } = useApiClient()
  return request<ListResponse<DeviceProfileListItem>>(
    buildDeviceProfilesListPath(options),
    {
      headers: buildCurrentActorHeaders(options.actorId)
    }
  )
}

export async function fetchDeviceProfileDetail(
  deviceProfileId: string
): Promise<DeviceProfileDetail> {
  const { request } = useApiClient()
  return request<DeviceProfileDetail>(`/device-profiles/${deviceProfileId}`)
}

export async function createDeviceProfile(
  payload: DeviceProfileCreatePayload,
  actorId?: string | null
): Promise<DeviceProfileDetail> {
  const { request } = useApiClient()
  return request<DeviceProfileDetail>('/device-profiles', {
    method: 'POST',
    body: payload,
    headers: buildCurrentActorHeaders(actorId)
  })
}

export async function updateDeviceProfile(
  deviceProfileId: string,
  payload: DeviceProfileUpdatePayload
): Promise<DeviceProfileDetail> {
  const { request } = useApiClient()
  return request<DeviceProfileDetail>(`/device-profiles/${deviceProfileId}`, {
    method: 'PATCH',
    body: payload
  })
}
