import { expect, test } from '@playwright/test'

import { mockApiJson } from './support/api-mocks'

const developerSession = {
  account: {
    id: 'acct_session_only_dev',
    display_name: 'Session Only Dev',
    role: 'developer',
    email: 'session-only@example.com',
    is_active: true
  },
  expires_at: '2026-04-11T09:00:00Z'
} as const

const isSessionOnlyRun =
  process.env.NUXT_PUBLIC_AUTH_MODE === 'session_only' ||
  process.env.BFP_AUTH_MODE === 'session_only'

test.describe('session-only auth mode', () => {
  test.skip(!isSessionOnlyRun, 'Only runs when frontend auth mode is session_only.')

  test('shows login-first guidance instead of actor fallback when unauthenticated', async ({
    page
  }) => {
    const response = await page.goto('/')

    expect(response?.ok()).toBeTruthy()
    await expect(page.getByTestId('public-shell-root')).toBeVisible()
    await expect(page.getByTestId('public-shell-header')).toBeVisible()
    await expect(page.getByTestId('public-shell-login-link')).toBeVisible()
    await expect(page.getByTestId('public-shell-register-link')).toBeVisible()
    await expect(page.getByTestId('current-actor-compact')).toHaveCount(0)
  })

  test('uses session-backed mine views without X-Actor-Id headers', async ({ page }) => {
    await page.route(/\/api\/v1\/auth\/login$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(developerSession)
      })
    })

    await mockApiJson(page, '/projects?mine=true', {
      items: [
        {
          id: 'proj_session_only_123',
          name: 'Session Only Project',
          description: 'Session-only mine view verification.',
          owner_account_id: developerSession.account.id,
          updated_at: '2026-04-11T09:00:00Z'
        }
      ],
      total: 1
    })

    await mockApiJson(page, '/campaigns?mine=true', {
      items: [
        {
          id: 'camp_session_only_123',
          project_id: 'proj_session_only_123',
          name: 'Session Only Campaign',
          target_platforms: ['ios'],
          version_label: '1.0.0-rc1',
          status: 'active',
          updated_at: '2026-04-11T09:05:00Z'
        }
      ],
      total: 1
    })

    await mockApiJson(page, '/feedback?mine=true&review_status=submitted', {
      items: [],
      total: 0
    })

    await mockApiJson(page, '/participation-requests?review_mine=true', {
      items: [],
      total: 0
    })

    await page.goto('/login')
    await expect(page.getByTestId('login-panel')).toBeVisible()
    await page.waitForLoadState('networkidle')
    await page.getByTestId('login-email-input').fill('session-only@example.com')
    await page.getByTestId('login-password-input').fill('supersecret')
    await page.getByTestId('login-submit').click()

    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByTestId('dashboard-shell')).toBeVisible()
    await expect(page.getByTestId('dashboard-developer-handoff')).toBeVisible()

    await page.goto('/')
    await expect(page.getByTestId('public-shell-dashboard-link')).toBeVisible()

    await page.goto('/my/projects')
    await expect(page.getByTestId('current-actor-compact-label')).toContainText(
      'Session Only Dev'
    )
    await expect(page.getByTestId('current-session-account-link')).toBeVisible()
    await expect(page.getByTestId('my-projects-summary')).toContainText('我的專案 1')
  })

  test('redirects already signed-in users away from auth pages', async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.setItem('beta-feedback-platform.auth-session-enabled', '1')
    })

    await page.route(/\/api\/v1\/auth\/me$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(developerSession)
      })
    })

    await mockApiJson(page, '/campaigns?mine=true', {
      items: [],
      total: 0
    })

    await mockApiJson(page, '/projects?mine=true', {
      items: [],
      total: 0
    })

    await mockApiJson(page, '/feedback?mine=true&review_status=submitted', {
      items: [],
      total: 0
    })

    await mockApiJson(page, '/participation-requests?review_mine=true', {
      items: [],
      total: 0
    })

    await page.goto('/login')
    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByTestId('dashboard-shell')).toBeVisible()

    await page.goto('/register')
    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByTestId('dashboard-shell')).toBeVisible()
  })
})
