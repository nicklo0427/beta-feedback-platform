export type AuthRole = 'developer' | 'tester'

export interface AuthenticatedActor {
  id: string
  display_name: string
  role: AuthRole
  email: string
  is_active: boolean
}

export interface AuthSessionResponse {
  account: AuthenticatedActor
  expires_at: string
}

export interface RegisterPayload {
  display_name: string
  role: AuthRole
  email: string
  password: string
  bio?: string | null
  locale?: string | null
}

export interface LoginPayload {
  email: string
  password: string
}
