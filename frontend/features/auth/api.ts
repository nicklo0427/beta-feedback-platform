import { useApiClient } from '~/services/api/client'

import type { AuthSessionResponse, LoginPayload, RegisterPayload } from './types'

export async function registerWithPassword(
  payload: RegisterPayload
): Promise<AuthSessionResponse> {
  const { request } = useApiClient()
  return request<AuthSessionResponse>('/auth/register', {
    method: 'POST',
    body: payload
  })
}

export async function loginWithPassword(
  payload: LoginPayload
): Promise<AuthSessionResponse> {
  const { request } = useApiClient()
  return request<AuthSessionResponse>('/auth/login', {
    method: 'POST',
    body: payload
  })
}

export async function logoutCurrentSession(): Promise<void> {
  const { request } = useApiClient()
  await request('/auth/logout', {
    method: 'POST'
  })
}

export async function fetchCurrentSession(): Promise<AuthSessionResponse> {
  const { request } = useApiClient()
  return request<AuthSessionResponse>('/auth/me')
}
