import { useState } from '#imports'
import { watch } from 'vue'

import { fetchCurrentSession } from '~/features/auth/api'
import type { AuthSessionResponse } from '~/features/auth/types'
import { ApiClientError } from '~/services/api/client'

const CURRENT_ACTOR_STORAGE_KEY = 'beta-feedback-platform.current-actor-id'
const AUTH_SESSION_MARKER_KEY = 'beta-feedback-platform.auth-session-enabled'

export function useCurrentActorId() {
  return useState<string | null>('current-actor-id', () => null)
}

export function useAuthSession() {
  return useState<AuthSessionResponse | null>('auth-session', () => null)
}

export function useAuthSessionPending() {
  return useState<boolean>('auth-session-pending', () => false)
}

export function useAuthSessionBootstrapped() {
  return useState<boolean>('auth-session-bootstrapped', () => false)
}

function setAuthSessionMarker(enabled: boolean): void {
  if (!import.meta.client) {
    return
  }

  if (enabled) {
    window.localStorage.setItem(AUTH_SESSION_MARKER_KEY, '1')
    return
  }

  window.localStorage.removeItem(AUTH_SESSION_MARKER_KEY)
}

function hasAuthSessionMarker(): boolean {
  if (!import.meta.client) {
    return false
  }

  return window.localStorage.getItem(AUTH_SESSION_MARKER_KEY) === '1'
}

export function applyAuthenticatedSession(session: AuthSessionResponse): void {
  const currentActorId = useCurrentActorId()
  const authSession = useAuthSession()
  const bootstrapped = useAuthSessionBootstrapped()

  authSession.value = session
  currentActorId.value = session.account.id
  bootstrapped.value = true
  setAuthSessionMarker(true)
}

export function clearAuthenticatedSession(): void {
  const currentActorId = useCurrentActorId()
  const authSession = useAuthSession()
  const bootstrapped = useAuthSessionBootstrapped()

  authSession.value = null
  currentActorId.value = null
  bootstrapped.value = false
  setAuthSessionMarker(false)
}

export async function useAuthSessionBootstrap(): Promise<void> {
  const authSession = useAuthSession()
  const currentActorId = useCurrentActorId()
  const pending = useAuthSessionPending()
  const bootstrapped = useAuthSessionBootstrapped()

  if (
    !import.meta.client ||
    pending.value ||
    bootstrapped.value ||
    authSession.value !== null ||
    !hasAuthSessionMarker()
  ) {
    return
  }

  pending.value = true

  try {
    const session = await fetchCurrentSession()
    authSession.value = session
    currentActorId.value = session.account.id
  } catch (error) {
    authSession.value = null

    if (error instanceof ApiClientError) {
      if (error.code === 'unauthenticated' || error.code === 'session_expired') {
        currentActorId.value = null
        setAuthSessionMarker(false)
      }
    }
  } finally {
    pending.value = false
    bootstrapped.value = true
  }
}

export function useCurrentActorPersistence(): void {
  const currentActorId = useCurrentActorId()
  const authSession = useAuthSession()
  const hydrated = useState<boolean>('current-actor-hydrated', () => false)
  const watchRegistered = useState<boolean>(
    'current-actor-watch-registered',
    () => false
  )

  if (import.meta.client && !hydrated.value) {
    const storedActorId = window.localStorage.getItem(CURRENT_ACTOR_STORAGE_KEY)
    currentActorId.value = storedActorId || authSession.value?.account.id || null
    hydrated.value = true
  }

  void useAuthSessionBootstrap()

  if (import.meta.client && !watchRegistered.value) {
    watch(
      currentActorId,
      (nextActorId) => {
        if (nextActorId) {
          window.localStorage.setItem(CURRENT_ACTOR_STORAGE_KEY, nextActorId)
          return
        }

        window.localStorage.removeItem(CURRENT_ACTOR_STORAGE_KEY)
      },
      {
        flush: 'post'
      }
    )
    watchRegistered.value = true
  }
}

export function buildCurrentActorHeaders(
  actorId?: string | null
): Record<string, string> | undefined {
  if (!actorId) {
    return undefined
  }

  return {
    'X-Actor-Id': actorId
  }
}

export function getActorAwareMutationErrorMessage(
  error: unknown,
  fallbackMessage: string
): string {
  if (!(error instanceof ApiClientError)) {
    return fallbackMessage
  }

  if (error.code === 'missing_actor_context') {
    return '請先選擇目前操作帳號，再繼續操作。'
  }

  if (error.code === 'unauthenticated') {
    return '請先登入，再繼續操作。'
  }

  if (error.code === 'session_expired') {
    return '登入已過期，請重新登入後再試一次。'
  }

  if (error.code === 'forbidden_actor_role') {
    return '目前操作帳號角色不符合這項操作。'
  }

  if (error.code === 'ownership_mismatch') {
    return '你不能操作不屬於自己的資源。'
  }

  if (error.code === 'assignment_not_eligible') {
    const errorDetails = (
      error.details && typeof error.details === 'object'
        ? error.details
        : {}
    ) as { reason_summary?: unknown }
    const reasonSummary =
      typeof errorDetails.reason_summary === 'string'
        ? errorDetails.reason_summary
        : null

    return reasonSummary
      ? `選擇的裝置設定檔不符合活動資格條件：${reasonSummary}`
      : '選擇的裝置設定檔不符合這個活動的資格條件。'
  }

  if (error.code === 'participation_not_qualified') {
    const errorDetails = (
      error.details && typeof error.details === 'object'
        ? error.details
        : {}
    ) as { reason_summary?: unknown }
    const reasonSummary =
      typeof errorDetails.reason_summary === 'string'
        ? errorDetails.reason_summary
        : null

    return reasonSummary
      ? `選擇的裝置設定檔目前不能送出參與意圖：${reasonSummary}`
      : '選擇的裝置設定檔目前不能對這個活動送出參與意圖。'
  }

  if (error.code === 'duplicate_pending_participation_request') {
    return '這個裝置設定檔已經對此活動送出待處理的參與意圖。'
  }

  if (error.code === 'invalid_participation_transition') {
    return '這筆參與意圖目前不能執行這個狀態變更。'
  }

  if (error.code === 'participation_request_not_accepted') {
    return '只有已接受的參與意圖才能建立對應任務。'
  }

  if (error.code === 'participation_request_task_already_created') {
    return '這筆參與意圖已經建立過對應任務。'
  }

  return error.message
}

export function getActorAwareReadErrorMessage(
  error: unknown,
  fallbackMessage: string
): string {
  const candidates = [
    error,
    typeof error === 'object' && error !== null && 'data' in error
      ? (error as { data?: unknown }).data
      : null,
    typeof error === 'object' && error !== null && 'cause' in error
      ? (error as { cause?: unknown }).cause
      : null
  ]

  let normalizedError: ApiClientError | null = null
  for (const candidate of candidates) {
    if (candidate instanceof ApiClientError) {
      normalizedError = candidate
      break
    }

    if (
      candidate &&
      typeof candidate === 'object' &&
      'code' in candidate &&
      'message' in candidate
    ) {
      const payload = candidate as {
        code?: unknown
        message?: unknown
        details?: unknown
      }
      normalizedError = new ApiClientError({
        code: typeof payload.code === 'string' ? payload.code : 'internal_error',
        message:
          typeof payload.message === 'string' ? payload.message : fallbackMessage,
        details: 'details' in payload ? payload.details : null
      })
      break
    }
  }

  if (!normalizedError) {
    return fallbackMessage
  }

  if (normalizedError.code === 'missing_actor_context') {
    return '這筆資料包含受保護的協作上下文，請先選擇目前操作帳號。'
  }

  if (normalizedError.code === 'unauthenticated') {
    return '這筆資料需要先登入後才能查看。'
  }

  if (normalizedError.code === 'session_expired') {
    return '登入已過期，請重新登入後再查看這筆資料。'
  }

  if (normalizedError.code === 'forbidden_actor_role') {
    return '目前操作帳號角色無法查看這筆資料。'
  }

  if (normalizedError.code === 'ownership_mismatch') {
    return '你不能查看不屬於自己工作範圍的資料。'
  }

  return normalizedError.message
}
