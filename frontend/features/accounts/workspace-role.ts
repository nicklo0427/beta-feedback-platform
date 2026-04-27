import { useState } from '#imports'
import { computed, watch, type ComputedRef, type Ref } from 'vue'

import {
  ACCOUNT_ROLE_OPTIONS,
  normalizeAccountRoles,
  type AccountRole
} from './types'

export const ACTIVE_WORKSPACE_ROLE_STORAGE_KEY =
  'beta-feedback-platform.active-workspace-role'

type WorkspaceRoleAccount = {
  role?: AccountRole | string | null
  roles?: (AccountRole | string)[] | null
} | null | undefined

function parseWorkspaceRole(value: string | null): AccountRole | null {
  if (value && ACCOUNT_ROLE_OPTIONS.includes(value as AccountRole)) {
    return value as AccountRole
  }

  return null
}

export function resolveActiveWorkspaceRole(
  account: WorkspaceRoleAccount,
  preferredRole: AccountRole | null
): AccountRole | null {
  const availableRoles = normalizeAccountRoles(account ?? {})

  if (availableRoles.length === 0) {
    return null
  }

  if (preferredRole && availableRoles.includes(preferredRole)) {
    return preferredRole
  }

  return availableRoles[0]
}

export function useActiveWorkspaceRole(): Ref<AccountRole | null> {
  return useState<AccountRole | null>('active-workspace-role', () => null)
}

export function useWorkspaceRoleOptions(
  account: Ref<WorkspaceRoleAccount> | ComputedRef<WorkspaceRoleAccount>
): ComputedRef<AccountRole[]> {
  return computed(() => normalizeAccountRoles(account.value ?? {}))
}

export function useActiveWorkspaceRolePersistence(
  account: Ref<WorkspaceRoleAccount> | ComputedRef<WorkspaceRoleAccount>
): Ref<AccountRole | null> {
  const activeWorkspaceRole = useActiveWorkspaceRole()
  const hydrated = useState<boolean>('active-workspace-role-hydrated', () => false)

  if (import.meta.client && !hydrated.value) {
    activeWorkspaceRole.value = parseWorkspaceRole(
      window.localStorage.getItem(ACTIVE_WORKSPACE_ROLE_STORAGE_KEY)
    )
    hydrated.value = true
  }

  watch(
    () => normalizeAccountRoles(account.value ?? {}).join('|'),
    () => {
      const resolvedRole = resolveActiveWorkspaceRole(
        account.value,
        activeWorkspaceRole.value
      )

      if (resolvedRole && activeWorkspaceRole.value !== resolvedRole) {
        activeWorkspaceRole.value = resolvedRole
      }
    },
    {
      immediate: true
    }
  )

  watch(
    activeWorkspaceRole,
    (nextRole) => {
      if (!import.meta.client || !nextRole) {
        return
      }

      window.localStorage.setItem(ACTIVE_WORKSPACE_ROLE_STORAGE_KEY, nextRole)
    },
    {
      flush: 'sync'
    }
  )

  return activeWorkspaceRole
}
