import { expect, test, type Page } from '@playwright/test'

import { mockApiJson } from './support/api-mocks'

const developerSession = {
  account: {
    id: 'acct_auth_dev_123',
    display_name: 'Session Dev',
    role: 'developer',
    email: 'dev@example.com',
    is_active: true
  },
  expires_at: '2026-04-11T09:00:00Z'
} as const

const testerSession = {
  account: {
    id: 'acct_auth_tester_123',
    display_name: 'Session Tester',
    role: 'tester',
    email: 'tester@example.com',
    is_active: true
  },
  expires_at: '2026-04-11T09:00:00Z'
} as const

async function mockAccountsForSessions(page: Page) {
  await mockApiJson(page, '/accounts', {
    items: [
      {
        id: developerSession.account.id,
        display_name: developerSession.account.display_name,
        role: developerSession.account.role,
        updated_at: '2026-04-10T09:00:00Z'
      },
      {
        id: testerSession.account.id,
        display_name: testerSession.account.display_name,
        role: testerSession.account.role,
        updated_at: '2026-04-10T09:00:00Z'
      }
    ],
    total: 2
  })
}

test.describe('auth session shell flows', () => {
  test('registers an account and uses session-backed developer home state', async ({
    page
  }) => {
    await page.route(/\/api\/v1\/auth\/register$/, async (route) => {
      expect(route.request().method()).toBe('POST')
      const payload = route.request().postDataJSON()
      expect(payload.display_name).toBe('Session Dev')
      expect(payload.role).toBe('developer')
      expect(payload.email).toBe('dev@example.com')
      expect(payload.password).toBe('supersecret')

      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(developerSession)
      })
    })

    await mockAccountsForSessions(page)

    await page.route(/\/api\/v1\/projects\?mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(developerSession.account.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 2
        })
      })
    })

    await page.route(/\/api\/v1\/campaigns\?mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(developerSession.account.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 3
        })
      })
    })

    await page.route(/\/api\/v1\/feedback\?mine=true&review_status=submitted$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(developerSession.account.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 1
        })
      })
    })

    await page.goto('/register')
    await expect(page.getByTestId('register-panel')).toBeVisible()
    await page.waitForLoadState('networkidle')

    await page.getByTestId('register-display-name-input').fill('Session Dev')
    await page.getByTestId('register-role-select').selectOption('developer')
    await page.getByTestId('register-email-input').fill('dev@example.com')
    await page.getByTestId('register-password-input').fill('supersecret')
    await page.getByTestId('register-submit').click()

    await expect(page).toHaveURL(/\/$/)
    await expect(page.getByTestId('current-session-ready')).toBeVisible()
    await expect(page.getByTestId('current-session-summary')).toContainText('Session Dev')
    await expect(page.getByTestId('home-role-developer')).toBeVisible()
    await expect(page.getByTestId('home-role-card-projects')).toContainText('2')
    await expect(page.getByTestId('home-role-card-campaigns')).toContainText('3')
    await expect(page.getByTestId('home-role-card-review-queue')).toContainText('1')
    await expect(page.getByTestId('current-actor-ready')).toHaveCount(0)
  })

  test('logs in as tester and can log out back to the login page', async ({ page }) => {
    await page.route(/\/api\/v1\/auth\/login$/, async (route) => {
      expect(route.request().method()).toBe('POST')
      expect(route.request().postDataJSON()).toEqual({
        email: 'tester@example.com',
        password: 'supersecret'
      })

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(testerSession)
      })
    })

    await page.route(/\/api\/v1\/auth\/logout$/, async (route) => {
      await route.fulfill({
        status: 204,
        body: ''
      })
    })

    await mockAccountsForSessions(page)

    await page.route(/\/api\/v1\/device-profiles\?mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(testerSession.account.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 4
        })
      })
    })

    await page.route(/\/api\/v1\/tasks\?status=assigned&mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(testerSession.account.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 2
        })
      })
    })

    await page.route(/\/api\/v1\/tasks\?status=in_progress&mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(testerSession.account.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 1
        })
      })
    })

    await page.goto('/login')
    await expect(page.getByTestId('login-panel')).toBeVisible()
    await page.waitForLoadState('networkidle')
    await page.getByTestId('login-email-input').fill('tester@example.com')
    await page.getByTestId('login-password-input').fill('supersecret')
    await page.getByTestId('login-submit').click()

    await expect(page).toHaveURL(/\/$/)
    await expect(page.getByTestId('current-session-ready')).toBeVisible()
    await expect(page.getByTestId('home-role-tester')).toBeVisible()
    await expect(page.getByTestId('home-role-card-device-profiles')).toContainText('4')
    await expect(page.getByTestId('home-role-card-assigned-tasks')).toContainText('2')
    await expect(page.getByTestId('home-role-card-in-progress-tasks')).toContainText('1')

    await page.getByTestId('current-session-logout').click()

    await expect(page).toHaveURL(/\/login$/)
    await expect(page.getByTestId('login-panel')).toBeVisible()
  })

  test('bootstraps an existing auth session from /auth/me on reload', async ({ page }) => {
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

    await mockAccountsForSessions(page)

    await page.route(/\/api\/v1\/projects\?mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(developerSession.account.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 1
        })
      })
    })

    await page.route(/\/api\/v1\/campaigns\?mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(developerSession.account.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 2
        })
      })
    })

    await page.route(/\/api\/v1\/feedback\?mine=true&review_status=submitted$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(developerSession.account.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 5
        })
      })
    })

    await page.goto('/')

    await expect(page.getByTestId('current-session-ready')).toBeVisible()
    await expect(page.getByTestId('home-role-developer')).toBeVisible()
    await expect(page.getByTestId('home-role-card-projects')).toContainText('1')
    await expect(page.getByTestId('home-role-card-campaigns')).toContainText('2')
    await expect(page.getByTestId('home-role-card-review-queue')).toContainText('5')
  })
})
