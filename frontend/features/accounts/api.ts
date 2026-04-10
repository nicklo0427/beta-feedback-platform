import { buildCurrentActorHeaders } from '~/features/accounts/current-actor'
import type { ListResponse } from '~/services/api/client'

import { useApiClient } from '~/services/api/client'

import type {
  AccountCollaborationSummary,
  AccountCreatePayload,
  AccountDetail,
  AccountListItem,
  AccountUpdatePayload
} from './types'

export async function fetchAccounts(): Promise<ListResponse<AccountListItem>> {
  const { request } = useApiClient()
  return request<ListResponse<AccountListItem>>('/accounts')
}

export async function fetchAccountDetail(
  accountId: string,
  actorId?: string | null
): Promise<AccountDetail> {
  const { request } = useApiClient()
  return request<AccountDetail>(`/accounts/${accountId}`, {
    headers: buildCurrentActorHeaders(actorId)
  })
}

export async function fetchAccountSummary(
  accountId: string,
  actorId?: string | null
): Promise<AccountCollaborationSummary> {
  const { request } = useApiClient()
  return request<AccountCollaborationSummary>(`/accounts/${accountId}/summary`, {
    headers: buildCurrentActorHeaders(actorId)
  })
}

export async function createAccount(
  payload: AccountCreatePayload
): Promise<AccountDetail> {
  const { request } = useApiClient()
  return request<AccountDetail>('/accounts', {
    method: 'POST',
    body: payload
  })
}

export async function updateAccount(
  accountId: string,
  payload: AccountUpdatePayload
): Promise<AccountDetail> {
  const { request } = useApiClient()
  return request<AccountDetail>(`/accounts/${accountId}`, {
    method: 'PATCH',
    body: payload
  })
}
