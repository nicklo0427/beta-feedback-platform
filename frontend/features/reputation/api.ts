import { useApiClient } from '~/services/api/client'

import type {
  CampaignReputationSummary,
  DeviceProfileReputationSummary
} from './types'

export async function fetchDeviceProfileReputation(
  deviceProfileId: string
): Promise<DeviceProfileReputationSummary> {
  const { request } = useApiClient()
  return request<DeviceProfileReputationSummary>(
    `/device-profiles/${deviceProfileId}/reputation`
  )
}

export async function fetchCampaignReputation(
  campaignId: string
): Promise<CampaignReputationSummary> {
  const { request } = useApiClient()
  return request<CampaignReputationSummary>(`/campaigns/${campaignId}/reputation`)
}
