import type { ListResponse } from '~/services/api/client'

import { useApiClient } from '~/services/api/client'

import type {
  DeviceProfileCreatePayload,
  DeviceProfileDetail,
  DeviceProfileListItem,
  DeviceProfileUpdatePayload
} from './types'

export async function fetchDeviceProfiles(): Promise<ListResponse<DeviceProfileListItem>> {
  const { request } = useApiClient()
  return request<ListResponse<DeviceProfileListItem>>('/device-profiles')
}

export async function fetchDeviceProfileDetail(
  deviceProfileId: string
): Promise<DeviceProfileDetail> {
  const { request } = useApiClient()
  return request<DeviceProfileDetail>(`/device-profiles/${deviceProfileId}`)
}

export async function createDeviceProfile(
  payload: DeviceProfileCreatePayload
): Promise<DeviceProfileDetail> {
  const { request } = useApiClient()
  return request<DeviceProfileDetail>('/device-profiles', {
    method: 'POST',
    body: payload
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
