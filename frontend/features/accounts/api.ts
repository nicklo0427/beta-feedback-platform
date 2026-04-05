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

export async function fetchAccountDetail(accountId: string): Promise<AccountDetail> {
  const { request } = useApiClient()
  return request<AccountDetail>(`/accounts/${accountId}`)
}

export async function fetchAccountSummary(
  accountId: string
): Promise<AccountCollaborationSummary> {
  const { request } = useApiClient()
  return request<AccountCollaborationSummary>(`/accounts/${accountId}/summary`)
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
