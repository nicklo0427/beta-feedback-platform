import { expect, test, type Page } from '@playwright/test'

import { mockApiJson } from './support/api-mocks'

const developerSession = {
  account: {
    id: 'acct_auth_dev_123',
    display_name: 'Session Dev',
    role: 'developer',
    roles: ['developer', 'tester'],
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
    roles: ['tester'],
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
        roles: developerSession.account.roles,
        updated_at: '2026-04-10T09:00:00Z'
      },
      {
        id: testerSession.account.id,
        display_name: testerSession.account.display_name,
        role: testerSession.account.role,
        roles: testerSession.account.roles,
        updated_at: '2026-04-10T09:00:00Z'
      }
    ],
    total: 2
  })
}

async function mockDeveloperDashboardData(page: Page) {
  await mockApiJson(page, '/projects?mine=true', {
    items: [
      {
        id: 'proj_session_123',
        name: 'Launch Prep',
        description: 'Prepare the release candidate beta workspace.',
        owner_account_id: developerSession.account.id,
        updated_at: '2026-04-11T09:00:00Z'
      }
    ],
    total: 1
  })

  await mockApiJson(page, '/campaigns?mine=true', {
    items: [
      {
        id: 'camp_session_123',
        project_id: 'proj_session_123',
        name: 'RC Candidate',
        target_platforms: ['ios'],
        version_label: '1.0.0-rc1',
        status: 'active',
        updated_at: '2026-04-11T09:05:00Z'
      }
    ],
    total: 1
  })

  await mockApiJson(page, '/feedback?mine=true&review_status=submitted', {
    items: [
      {
        id: 'feedback_session_123',
        task_id: 'task_session_123',
        campaign_id: 'camp_session_123',
        summary: 'Launch blocker',
        severity: 'high',
        category: 'bug',
        review_status: 'submitted',
        submitted_at: '2026-04-11T09:10:00Z'
      }
    ],
    total: 1
  })

  await mockApiJson(page, '/participation-requests?review_mine=true', {
    items: [
      {
        id: 'request_session_123',
        campaign_id: 'camp_session_123',
        campaign_name: 'RC Candidate',
        tester_account_id: testerSession.account.id,
        device_profile_id: 'dp_session_123',
        device_profile_name: 'iPhone 15 Pro',
        status: 'pending',
        note: null,
        decision_note: null,
        created_at: '2026-04-11T09:10:00Z',
        updated_at: '2026-04-11T09:10:00Z',
        decided_at: null,
        linked_task_id: null,
        assignment_created_at: null,
        assignment_status: 'not_assigned'
      }
    ],
    total: 1
  })
}

async function mockTesterDashboardData(page: Page) {
  await mockApiJson(page, '/tasks?status=assigned&mine=true', {
    items: [
      {
        id: 'task_assigned_123',
        campaign_id: 'camp_tester_123',
        device_profile_id: 'dp_tester_123',
        title: 'Assigned checkout pass',
        status: 'assigned',
        updated_at: '2026-04-11T09:00:00Z'
      }
    ],
    total: 1
  })

  await mockApiJson(page, '/tasks?status=in_progress&mine=true', {
    items: [
      {
        id: 'task_progress_123',
        campaign_id: 'camp_tester_123',
        device_profile_id: 'dp_tester_123',
        title: 'In-progress sign-in pass',
        status: 'in_progress',
        updated_at: '2026-04-11T09:10:00Z'
      }
    ],
    total: 1
  })

  await mockApiJson(page, '/campaigns?qualified_for_me=true', {
    items: [
      {
        id: 'camp_tester_123',
        project_id: 'proj_tester_123',
        name: 'Tester Campaign',
        target_platforms: ['android'],
        version_label: '2026.04',
        status: 'active',
        updated_at: '2026-04-11T09:15:00Z',
        qualification_summary: 'Matches the current Android install channel.'
      }
    ],
    total: 1
  })

  await mockApiJson(page, '/participation-requests?mine=true', {
    items: [
      {
        id: 'request_tester_123',
        campaign_id: 'camp_tester_123',
        campaign_name: 'Tester Campaign',
        tester_account_id: testerSession.account.id,
        device_profile_id: 'dp_tester_123',
        device_profile_name: 'Pixel 9',
        status: 'accepted',
        note: null,
        decision_note: 'Looks good.',
        created_at: '2026-04-11T09:05:00Z',
        updated_at: '2026-04-11T09:20:00Z',
        decided_at: '2026-04-11T09:20:00Z',
        linked_task_id: 'task_progress_123',
        assignment_created_at: '2026-04-11T09:21:00Z',
        assignment_status: 'task_created'
      }
    ],
    total: 1
  })
}

test.describe('auth session shell flows', () => {
  test('redirects unauthenticated dashboard access to the login page', async ({ page }) => {
    await page.goto('/dashboard')

    await expect(page).toHaveURL(/\/login$/)
    await expect(page.getByTestId('login-panel')).toBeVisible()
  })

  test('registers an account and lands on the dashboard handoff', async ({
    page
  }) => {
    await page.route(/\/api\/v1\/auth\/register$/, async (route) => {
      expect(route.request().method()).toBe('POST')
      const payload = route.request().postDataJSON()
      expect(payload.display_name).toBe('Session Dev')
      expect(payload.role).toBe('developer')
      expect(payload.roles).toEqual(['developer', 'tester'])
      expect(payload.email).toBe('dev@example.com')
      expect(payload.password).toBe('supersecret')

      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(developerSession)
      })
    })

    await page.route(/\/api\/v1\/auth\/me$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(developerSession)
      })
    })

    await mockAccountsForSessions(page)

    await mockDeveloperDashboardData(page)

    await page.goto('/register')
    await expect(page.getByTestId('register-panel')).toBeVisible()
    await page.waitForLoadState('networkidle')

    await page.getByTestId('register-display-name-input').fill('Session Dev')
    await page.getByTestId('register-email-input').fill('dev@example.com')
    await page.getByTestId('register-password-input').fill('supersecret')
    await page.getByTestId('register-submit').click()

    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByTestId('dashboard-shell')).toBeVisible()
    await expect(page.getByTestId('dashboard-developer-handoff')).toBeVisible()

    await page.goto('/')
    await expect(page.getByTestId('public-shell-dashboard-link')).toBeVisible()

    await page.goto('/my/projects')
    await expect(page.getByTestId('current-actor-compact')).toBeVisible()
    await expect(page.getByTestId('current-session-account-link')).toBeVisible()
    await expect(page.getByTestId('my-projects-summary')).toContainText(/我的專案\s*1/)
    await expect(page.getByTestId('my-project-card-proj_session_123')).toContainText('Launch Prep')
  })

  test('preselects the register role from the query parameter', async ({ page }) => {
    await page.goto('/register?role=developer')
    await expect(page.getByTestId('register-panel')).toBeVisible()
    await expect(page.getByTestId('register-role-checkbox-developer')).toBeChecked()
    await expect(page.getByTestId('register-role-checkbox-tester')).not.toBeChecked()

    await page.goto('/register?role=tester')
    await expect(page.getByTestId('register-role-checkbox-developer')).not.toBeChecked()
    await expect(page.getByTestId('register-role-checkbox-tester')).toBeChecked()

    await page.goto('/register?role=not-a-real-role')
    await expect(page.getByTestId('register-role-checkbox-developer')).toBeChecked()
    await expect(page.getByTestId('register-role-checkbox-tester')).toBeChecked()
  })

  test('logs in as tester and lands on the dashboard before logging out', async ({ page }) => {
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

    await page.route(/\/api\/v1\/auth\/me$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(testerSession)
      })
    })

    await mockAccountsForSessions(page)

    await mockTesterDashboardData(page)

    await mockApiJson(page, '/device-profiles?mine=true', {
      items: [],
      total: 4
    })

    await page.goto('/login')
    await expect(page.getByTestId('login-panel')).toBeVisible()
    await page.waitForLoadState('networkidle')
    await page.getByTestId('login-email-input').fill('tester@example.com')
    await page.getByTestId('login-password-input').fill('supersecret')
    await page.getByTestId('login-submit').click()

    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByTestId('dashboard-shell')).toBeVisible()
    await expect(page.getByTestId('dashboard-tester-handoff')).toBeVisible()

    await page.goto('/')
    await expect(page.getByTestId('public-shell-dashboard-link')).toBeVisible()

    await page.goto('/projects')
    await expect(page.getByTestId('current-actor-compact')).toBeVisible()
    await page.getByTestId('current-session-logout').click()

    await expect(page).toHaveURL(/\/login$/)
    await expect(page.getByTestId('login-panel')).toBeVisible()
  })

  test('bootstraps an existing auth session from /auth/me on an app page', async ({ page }) => {
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

    await mockApiJson(page, '/projects?mine=true', {
      items: [
        {
          id: 'proj_reload_123',
          name: 'Reloaded Workspace',
          description: 'Session bootstrap verification project.',
          owner_account_id: developerSession.account.id,
          updated_at: '2026-04-11T09:00:00Z'
        }
      ],
      total: 1
    })

    await page.goto('/my/projects')

    await expect(page.getByTestId('current-actor-compact')).toBeVisible()
    await expect(page.getByTestId('current-session-account-link')).toBeVisible()
    await expect(page.getByTestId('my-projects-summary')).toContainText(/我的專案\s*1/)
  })

  test('redirects an already signed-in user away from auth pages and into the dashboard', async ({
    page
  }) => {
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
    await mockDeveloperDashboardData(page)

    await page.goto('/login')
    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByTestId('dashboard-developer-handoff')).toBeVisible()

    await page.goto('/register')
    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByTestId('dashboard-developer-handoff')).toBeVisible()
  })
})
