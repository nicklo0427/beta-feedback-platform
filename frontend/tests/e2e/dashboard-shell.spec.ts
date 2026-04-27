import { expect, test, type Page } from '@playwright/test'

import { mockApiJson } from './support/api-mocks'

const developerSession = {
  account: {
    id: 'acct_dashboard_dev',
    display_name: 'Dashboard Dev',
    role: 'developer',
    roles: ['developer'],
    email: 'dashboard-dev@example.com',
    is_active: true
  },
  expires_at: '2026-04-17T09:00:00Z'
} as const

const testerSession = {
  account: {
    id: 'acct_dashboard_tester',
    display_name: 'Dashboard Tester',
    role: 'tester',
    roles: ['tester'],
    email: 'dashboard-tester@example.com',
    is_active: true
  },
  expires_at: '2026-04-17T09:00:00Z'
} as const

const dualRoleSession = {
  account: {
    id: 'acct_dashboard_dual',
    display_name: 'Dashboard Dual',
    role: 'developer',
    roles: ['developer', 'tester'],
    email: 'dashboard-dual@example.com',
    is_active: true
  },
  expires_at: '2026-04-17T09:00:00Z'
} as const

async function bootstrapSession(
  page: Page,
  session: typeof developerSession | typeof testerSession | typeof dualRoleSession
) {
  await page.addInitScript(() => {
    window.localStorage.setItem('beta-feedback-platform.auth-session-enabled', '1')
  })

  await mockApiJson(page, '/auth/me', session)
  await mockApiJson(page, '/accounts', {
    items: [
      {
        id: developerSession.account.id,
        display_name: developerSession.account.display_name,
        role: developerSession.account.role,
        roles: developerSession.account.roles,
        updated_at: '2026-04-17T09:00:00Z'
      },
      {
        id: testerSession.account.id,
        display_name: testerSession.account.display_name,
        role: testerSession.account.role,
        roles: testerSession.account.roles,
        updated_at: '2026-04-17T09:00:00Z'
      },
      {
        id: dualRoleSession.account.id,
        display_name: dualRoleSession.account.display_name,
        role: dualRoleSession.account.role,
        roles: dualRoleSession.account.roles,
        updated_at: '2026-04-17T09:00:00Z'
      }
    ],
    total: 3
  })
}

async function mockDeveloperDashboardData(page: Page, actorId: string): Promise<void> {
  await mockApiJson(page, '/projects?mine=true', {
    items: [
      {
        id: 'proj_dashboard_launch',
        name: 'Launch Control',
        description: 'Coordinate the public beta launch workflow.',
        owner_account_id: actorId,
        updated_at: '2026-04-17T09:00:00Z'
      },
      {
        id: 'proj_dashboard_review',
        name: 'Review Ops',
        description: 'Handle review operations for launch week.',
        owner_account_id: actorId,
        updated_at: '2026-04-16T09:00:00Z'
      }
    ],
    total: 2
  })

  await mockApiJson(page, '/campaigns?mine=true', {
    items: [
      {
        id: 'camp_dashboard_ios',
        project_id: 'proj_dashboard_launch',
        name: 'iOS RC Beta',
        target_platforms: ['ios'],
        version_label: '1.4.0-rc1',
        status: 'active',
        updated_at: '2026-04-17T09:30:00Z'
      },
      {
        id: 'camp_dashboard_web',
        project_id: 'proj_dashboard_review',
        name: 'Web Checkout QA',
        target_platforms: ['web'],
        version_label: '2026.04',
        status: 'draft',
        updated_at: '2026-04-16T08:00:00Z'
      }
    ],
    total: 2
  })

  await mockApiJson(page, '/feedback?mine=true&review_status=submitted', {
    items: [
      {
        id: 'fb_dashboard_1',
        task_id: 'task_dashboard_1',
        campaign_id: 'camp_dashboard_ios',
        summary: 'Sign-in spinner never resolves',
        severity: 'high',
        category: 'bug',
        review_status: 'submitted',
        submitted_at: '2026-04-17T09:20:00Z'
      }
    ],
    total: 1
  })

  await mockApiJson(page, '/participation-requests?review_mine=true', {
    items: [
      {
        id: 'pr_dashboard_1',
        campaign_id: 'camp_dashboard_ios',
        campaign_name: 'iOS RC Beta',
        tester_account_id: 'acct_tester_1',
        device_profile_id: 'dp_1',
        device_profile_name: 'iPhone 15 Pro',
        status: 'pending',
        note: null,
        decision_note: null,
        created_at: '2026-04-17T09:00:00Z',
        updated_at: '2026-04-17T09:00:00Z',
        decided_at: null,
        linked_task_id: null,
        assignment_created_at: null,
        assignment_status: 'not_assigned'
      }
    ],
    total: 1
  })
}

async function mockTesterDashboardData(page: Page, actorId: string): Promise<void> {
  await mockApiJson(page, '/tasks?status=assigned&mine=true', {
    items: [
      {
        id: 'task_dashboard_assigned',
        campaign_id: 'camp_dashboard_android',
        device_profile_id: 'dp_dashboard_android',
        title: 'Android onboarding pass',
        status: 'assigned',
        updated_at: '2026-04-17T09:10:00Z'
      }
    ],
    total: 1
  })

  await mockApiJson(page, '/tasks?status=in_progress&mine=true', {
    items: [
      {
        id: 'task_dashboard_progress',
        campaign_id: 'camp_dashboard_ios',
        device_profile_id: 'dp_dashboard_ios',
        title: 'iOS payment regression',
        status: 'in_progress',
        updated_at: '2026-04-17T09:15:00Z',
        resolution_context: {
          resolution_outcome: 'confirmed_issue',
          resolution_note: null,
          resolved_at: '2026-04-17T09:15:00Z',
          resolved_by_account_id: actorId,
          resolved_by_account_display_name: 'Dashboard Dev'
        }
      }
    ],
    total: 1
  })

  await mockApiJson(page, '/campaigns?qualified_for_me=true', {
    items: [
      {
        id: 'camp_dashboard_ios',
        project_id: 'proj_dashboard_launch',
        name: 'iOS RC Beta',
        target_platforms: ['ios', 'pwa'],
        version_label: '1.4.0-rc1',
        status: 'active',
        updated_at: '2026-04-17T09:30:00Z',
        qualification_summary: 'Matches the active iOS install-channel rule.'
      }
    ],
    total: 1
  })

  await mockApiJson(page, '/participation-requests?mine=true', {
    items: [
      {
        id: 'pr_dashboard_tester_1',
        campaign_id: 'camp_dashboard_ios',
        campaign_name: 'iOS RC Beta',
        tester_account_id: actorId,
        device_profile_id: 'dp_dashboard_ios',
        device_profile_name: 'iPhone 15 Pro',
        status: 'accepted',
        note: 'Ready to cover payment and onboarding flows.',
        decision_note: 'Looks good for this sprint.',
        created_at: '2026-04-17T08:30:00Z',
        updated_at: '2026-04-17T09:00:00Z',
        decided_at: '2026-04-17T09:00:00Z',
        linked_task_id: 'task_dashboard_progress',
        assignment_created_at: '2026-04-17T09:05:00Z',
        assignment_status: 'task_created'
      }
    ],
    total: 1
  })
}

test.describe('dashboard home', () => {
  test('renders a developer dashboard with summary cards and review queues', async ({ page }) => {
    await bootstrapSession(page, developerSession)
    await mockDeveloperDashboardData(page, developerSession.account.id)

    await page.goto('/dashboard')

    await expect(page.getByTestId('dashboard-shell')).toBeVisible()
    await expect(page.getByTestId('dashboard-developer-handoff')).toBeVisible()
    await expect(page.getByTestId('dashboard-developer-projects-card')).toContainText('2')
    await expect(page.getByTestId('dashboard-developer-campaigns-card')).toContainText('2')
    await expect(page.getByTestId('dashboard-developer-participation-card')).toContainText('1')
    await expect(page.getByTestId('dashboard-developer-feedback-card')).toContainText('1')
    await expect(page.getByTestId('dashboard-developer-queue-participation')).toContainText(
      'iOS RC Beta'
    )
    await expect(page.getByTestId('dashboard-developer-queue-feedback')).toContainText(
      'Sign-in spinner never resolves'
    )
    await expect(page.getByTestId('dashboard-developer-queue-campaigns')).toContainText(
      'iOS RC Beta'
    )
  })

  test('renders a tester dashboard with task, qualification, and participation context', async ({
    page
  }) => {
    await bootstrapSession(page, testerSession)
    await mockTesterDashboardData(page, testerSession.account.id)

    await page.goto('/dashboard')

    await expect(page.getByTestId('dashboard-shell')).toBeVisible()
    await expect(page.getByTestId('dashboard-tester-handoff')).toBeVisible()
    await expect(page.getByTestId('dashboard-tester-assigned-card')).toContainText('1')
    await expect(page.getByTestId('dashboard-tester-in-progress-card')).toContainText('1')
    await expect(page.getByTestId('dashboard-tester-eligible-card')).toContainText('1')
    await expect(page.getByTestId('dashboard-tester-participation-card')).toContainText('1')
    await expect(page.getByTestId('dashboard-tester-queue-tasks')).toContainText(
      'Android onboarding pass'
    )
    await expect(page.getByTestId('dashboard-tester-queue-eligible')).toContainText(
      'iOS RC Beta'
    )
    await expect(page.getByTestId('dashboard-tester-queue-participation')).toContainText(
      'iPhone 15 Pro'
    )
  })

  test('lets a dual-role account switch dashboard views without changing accounts', async ({
    page
  }) => {
    await bootstrapSession(page, dualRoleSession)
    await mockDeveloperDashboardData(page, dualRoleSession.account.id)
    await mockTesterDashboardData(page, dualRoleSession.account.id)

    await page.goto('/dashboard')

    await expect(page.getByTestId('dashboard-shell')).toBeVisible()
    await expect(page.getByTestId('dashboard-developer-handoff')).toBeVisible()
    await expect(page.getByTestId('dashboard-active-workspace-role')).toContainText('開發者')
    await expect(page.getByTestId('dashboard-developer-projects-card')).toContainText('2')

    await page.getByTestId('active-workspace-role-option-tester').click()

    await expect(page.getByTestId('dashboard-tester-handoff')).toBeVisible()
    await expect(page.getByTestId('dashboard-active-workspace-role')).toContainText('測試者')
    await expect(page.getByTestId('dashboard-tester-assigned-card')).toContainText('1')
    await expect(page.getByTestId('dashboard-developer-handoff')).toHaveCount(0)
  })
})
