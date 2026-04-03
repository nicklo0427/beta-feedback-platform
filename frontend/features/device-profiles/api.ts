import type { ListResponse } from '~/services/api/client'

import { useApiClient } from '~/services/api/client'

import type { DeviceProfileDetail, DeviceProfileListItem } from './types'

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
