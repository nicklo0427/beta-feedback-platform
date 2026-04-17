import { useRuntimeConfig, useState } from '#imports'
import { watch } from 'vue'

import { fetchCurrentSession } from '~/features/auth/api'
import type { AuthSessionResponse } from '~/features/auth/types'
import {
  translateForLocale,
  useAppLocale,
  type AppLocale
} from '~/features/i18n/use-app-i18n'
import { ApiClientError } from '~/services/api/client'

const CURRENT_ACTOR_STORAGE_KEY = 'beta-feedback-platform.current-actor-id'
const AUTH_SESSION_MARKER_KEY = 'beta-feedback-platform.auth-session-enabled'

export type AuthRuntimeMode = 'session_only' | 'session_with_header_fallback'

function resolveErrorLocale(): AppLocale {
  return useAppLocale().value
}

function tError(
  locale: AppLocale,
  key: string,
  params?: Record<string, string | number>
): string {
  return translateForLocale(locale, key, params)
}

function normalizeAuthRuntimeMode(value: unknown): AuthRuntimeMode {
  return value === 'session_only'
    ? 'session_only'
    : 'session_with_header_fallback'
}

export function useCurrentActorId() {
  return useState<string | null>('current-actor-id', () => null)
}

export function useAuthRuntimeMode() {
  const config = useRuntimeConfig()
  return useState<AuthRuntimeMode>('auth-runtime-mode', () =>
    normalizeAuthRuntimeMode(config.public.authMode)
  )
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
  const authRuntimeMode = useAuthRuntimeMode()
  const hydrated = useState<boolean>('current-actor-hydrated', () => false)
  const watchRegistered = useState<boolean>(
    'current-actor-watch-registered',
    () => false
  )

  if (import.meta.client && !hydrated.value) {
    const storedActorId = window.localStorage.getItem(CURRENT_ACTOR_STORAGE_KEY)
    currentActorId.value =
      authRuntimeMode.value === 'session_only'
        ? authSession.value?.account.id || null
        : storedActorId || authSession.value?.account.id || null

    if (authRuntimeMode.value === 'session_only') {
      window.localStorage.removeItem(CURRENT_ACTOR_STORAGE_KEY)
    }

    hydrated.value = true
  }

  void useAuthSessionBootstrap()

  if (import.meta.client && !watchRegistered.value) {
    watch(
      currentActorId,
      (nextActorId) => {
        if (authRuntimeMode.value === 'session_only') {
          window.localStorage.removeItem(CURRENT_ACTOR_STORAGE_KEY)
          return
        }

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
  const authRuntimeMode = useAuthRuntimeMode()

  if (authRuntimeMode.value === 'session_only') {
    return undefined
  }

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
  const locale = resolveErrorLocale()

  if (!(error instanceof ApiClientError)) {
    return fallbackMessage
  }

  if (error.code === 'missing_actor_context') {
    return useAuthRuntimeMode().value === 'session_only'
      ? tError(locale, 'errors.mutation.missingActorContextSession')
      : tError(locale, 'errors.mutation.missingActorContext')
  }

  if (error.code === 'unauthenticated') {
    return tError(locale, 'errors.common.unauthenticated')
  }

  if (error.code === 'session_expired') {
    return tError(locale, 'errors.common.sessionExpired')
  }

  if (error.code === 'forbidden_actor_role') {
    return tError(locale, 'errors.common.forbiddenActorRole')
  }

  if (error.code === 'ownership_mismatch') {
    return tError(locale, 'errors.common.ownershipMismatchMutation')
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

    if (locale === 'zh-TW' && reasonSummary) {
      return tError(locale, 'errors.mutation.assignmentNotEligibleWithReason', {
        reason: reasonSummary
      })
    }

    return tError(locale, 'errors.mutation.assignmentNotEligible')
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

    if (locale === 'zh-TW' && reasonSummary) {
      return tError(
        locale,
        'errors.mutation.participationNotQualifiedWithReason',
        {
          reason: reasonSummary
        }
      )
    }

    return tError(locale, 'errors.mutation.participationNotQualified')
  }

  if (error.code === 'duplicate_pending_participation_request') {
    return tError(locale, 'errors.mutation.duplicatePendingParticipationRequest')
  }

  if (error.code === 'invalid_participation_transition') {
    return tError(locale, 'errors.mutation.invalidParticipationTransition')
  }

  if (error.code === 'participation_request_not_accepted') {
    return tError(locale, 'errors.mutation.participationRequestNotAccepted')
  }

  if (error.code === 'participation_request_task_already_created') {
    return tError(locale, 'errors.mutation.participationRequestTaskAlreadyCreated')
  }

  if (error.code === 'invalid_task_resolution_state') {
    return tError(locale, 'errors.mutation.invalidTaskResolutionState')
  }

  if (error.code === 'resolution_outcome_required') {
    return tError(locale, 'errors.mutation.resolutionOutcomeRequired')
  }

  return error.message
}

export function getActorAwareReadErrorMessage(
  error: unknown,
  fallbackMessage: string
): string {
  const locale = resolveErrorLocale()
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
    return useAuthRuntimeMode().value === 'session_only'
      ? tError(locale, 'errors.read.missingActorContextSession')
      : tError(locale, 'errors.read.missingActorContext')
  }

  if (normalizedError.code === 'unauthenticated') {
    return tError(locale, 'errors.read.unauthenticated')
  }

  if (normalizedError.code === 'session_expired') {
    return tError(locale, 'errors.read.sessionExpired')
  }

  if (normalizedError.code === 'forbidden_actor_role') {
    return tError(locale, 'errors.read.forbiddenActorRole')
  }

  if (normalizedError.code === 'ownership_mismatch') {
    return tError(locale, 'errors.read.ownershipMismatch')
  }

  return normalizedError.message
}
