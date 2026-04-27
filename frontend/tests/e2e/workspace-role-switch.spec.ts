import { expect, test, type Page } from '@playwright/test'

import { mockApiJson } from './support/api-mocks'

const ACTIVE_WORKSPACE_ROLE_STORAGE_KEY =
  'beta-feedback-platform.active-workspace-role'

const dualRoleSession = {
  account: {
    id: 'acct_workspace_dual',
    display_name: 'Dual Role Maker',
    role: 'developer',
    roles: ['developer', 'tester'],
    email: 'dual@example.com',
    is_active: true
  },
  expires_at: '2026-04-27T09:00:00Z'
} as const

const testerOnlySession = {
  account: {
    id: 'acct_workspace_tester',
    display_name: 'Tester Only',
    role: 'tester',
    roles: ['tester'],
    email: 'tester-only@example.com',
    is_active: true
  },
  expires_at: '2026-04-27T09:00:00Z'
} as const

async function bootstrapWorkspaceShell(
  page: Page,
  session: typeof dualRoleSession | typeof testerOnlySession,
  storedWorkspaceRole?: string
): Promise<void> {
  await page.addInitScript(
    ({ activeWorkspaceRoleStorageKey, storedRole }) => {
      window.localStorage.setItem('beta-feedback-platform.auth-session-enabled', '1')

      if (storedRole) {
        window.localStorage.setItem(activeWorkspaceRoleStorageKey, storedRole)
      }
    },
    {
      activeWorkspaceRoleStorageKey: ACTIVE_WORKSPACE_ROLE_STORAGE_KEY,
      storedRole: storedWorkspaceRole
    }
  )

  await mockApiJson(page, '/auth/me', session)
  await mockApiJson(page, '/accounts', {
    items: [
      {
        id: session.account.id,
        display_name: session.account.display_name,
        role: session.account.role,
        roles: session.account.roles,
        updated_at: '2026-04-27T09:00:00Z'
      }
    ],
    total: 1
  })
  await mockApiJson(page, '/projects', {
    items: [],
    total: 0
  })
}

test.describe('active workspace role switch', () => {
  test('lets a dual-role account switch and persist the frontend workspace view', async ({
    page
  }) => {
    await bootstrapWorkspaceShell(page, dualRoleSession)

    await page.goto('/projects')
    await page.waitForLoadState('networkidle')

    await expect(page.getByTestId('active-workspace-role-switch')).toBeVisible()
    await expect(page.getByTestId('active-workspace-role-option-developer')).toHaveAttribute(
      'aria-pressed',
      'true'
    )

    const mutationRequests: string[] = []
    page.on('request', (request) => {
      if (request.url().includes('/api/v1/') && request.method() !== 'GET') {
        mutationRequests.push(`${request.method()} ${request.url()}`)
      }
    })

    await page.getByTestId('active-workspace-role-option-tester').click()

    await expect(page.getByTestId('active-workspace-role-option-tester')).toHaveAttribute(
      'aria-pressed',
      'true'
    )
    await expect(page.getByTestId('active-workspace-role-chip')).toContainText('測試者')
    await expect
      .poll(() =>
        page.evaluate((storageKey) => window.localStorage.getItem(storageKey), ACTIVE_WORKSPACE_ROLE_STORAGE_KEY)
      )
      .toBe('tester')
    expect(mutationRequests).toEqual([])

    await page.reload()
    await expect(page.getByTestId('active-workspace-role-option-tester')).toHaveAttribute(
      'aria-pressed',
      'true'
    )
  })

  test('hides the switch for a single-role account and falls back from an unavailable stored role', async ({
    page
  }) => {
    await bootstrapWorkspaceShell(page, testerOnlySession, 'developer')

    await page.goto('/projects')
    await page.waitForLoadState('networkidle')

    await expect(page.getByTestId('active-workspace-role-switch')).toHaveCount(0)
    await expect(page.getByTestId('active-workspace-role-single')).toContainText('測試者')
    await expect(page.getByTestId('active-workspace-role-chip')).toContainText('測試者')
    await expect
      .poll(() =>
        page.evaluate((storageKey) => window.localStorage.getItem(storageKey), ACTIVE_WORKSPACE_ROLE_STORAGE_KEY)
      )
      .toBe('tester')
  })
})
