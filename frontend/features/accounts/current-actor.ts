import { useState } from '#imports'
import { watch } from 'vue'

import { ApiClientError } from '~/services/api/client'

const CURRENT_ACTOR_STORAGE_KEY = 'beta-feedback-platform.current-actor-id'

export function useCurrentActorId() {
  return useState<string | null>('current-actor-id', () => null)
}

export function useCurrentActorPersistence(): void {
  const currentActorId = useCurrentActorId()
  const hydrated = useState<boolean>('current-actor-hydrated', () => false)
  const watchRegistered = useState<boolean>(
    'current-actor-watch-registered',
    () => false
  )

  if (import.meta.client && !hydrated.value) {
    const storedActorId = window.localStorage.getItem(CURRENT_ACTOR_STORAGE_KEY)
    currentActorId.value = storedActorId || null
    hydrated.value = true
  }

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

  return error.message
}
