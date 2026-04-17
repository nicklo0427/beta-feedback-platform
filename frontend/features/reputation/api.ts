import { buildCurrentActorHeaders } from '~/features/accounts/current-actor'
import { useApiClient } from '~/services/api/client'

import type {
  CampaignReputationSummary,
  DeviceProfileReputationSummary
} from './types'

export async function fetchDeviceProfileReputation(
  deviceProfileId: string,
  actorId?: string | null
): Promise<DeviceProfileReputationSummary> {
  const { request } = useApiClient()
  return request<DeviceProfileReputationSummary>(
    `/device-profiles/${deviceProfileId}/reputation`,
    {
      headers: buildCurrentActorHeaders(actorId)
    }
  )
}

export async function fetchCampaignReputation(
  campaignId: string,
  actorId?: string | null
): Promise<CampaignReputationSummary> {
  const { request } = useApiClient()
  return request<CampaignReputationSummary>(`/campaigns/${campaignId}/reputation`, {
    headers: buildCurrentActorHeaders(actorId)
  })
}
