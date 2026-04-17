import { expect, test } from '@playwright/test'

const developerAccount = {
  id: 'acct_dev_123',
  display_name: 'Release Owner',
  role: 'developer',
  updated_at: '2026-04-09T09:30:00Z'
}

const testerAccount = {
  id: 'acct_tester_123',
  display_name: 'QA Tester',
  role: 'tester',
  updated_at: '2026-04-09T09:30:00Z'
}

const enrichedRequestDetail = {
  id: 'pr_123',
  campaign_id: 'camp_123',
  campaign_name: 'Closed Beta Round 1',
  tester_account_id: testerAccount.id,
  device_profile_id: 'dp_123',
  device_profile_name: 'QA iPhone 15',
  status: 'accepted',
  note: 'I can help cover onboarding and retention flows.',
  decision_note: null,
  created_at: '2026-04-09T09:30:00Z',
  updated_at: '2026-04-09T09:30:00Z',
  decided_at: '2026-04-09T10:00:00Z',
  linked_task_id: null,
  assignment_created_at: null,
  assignment_status: 'not_assigned',
  tester_account: {
    id: testerAccount.id,
    display_name: testerAccount.display_name,
    role: testerAccount.role,
    bio: 'Experienced iOS beta tester.',
    locale: 'zh-TW',
    created_at: '2026-04-08T09:30:00Z',
    updated_at: '2026-04-09T09:30:00Z'
  },
  tester_account_summary: {
    account_id: testerAccount.id,
    role: 'tester',
    developer_summary: null,
    tester_summary: {
      owned_device_profiles_count: 2,
      assigned_tasks_count: 4,
      submitted_feedback_count: 3,
      recent_device_profiles: [],
      recent_tasks: [],
      recent_feedback: []
    },
    updated_at: '2026-04-09T09:30:00Z'
  },
  device_profile: {
    id: 'dp_123',
    name: 'QA iPhone 15',
    platform: 'ios',
    device_model: 'iPhone 15 Pro',
    os_name: 'iOS',
    install_channel: 'testflight',
    os_version: '17.4',
    browser_name: null,
    browser_version: null,
    locale: 'zh-TW',
    notes: 'Primary iOS beta device.',
    owner_account_id: testerAccount.id,
    created_at: '2026-04-08T09:30:00Z',
    updated_at: '2026-04-09T09:30:00Z'
  },
  device_profile_reputation: {
    device_profile_id: 'dp_123',
    tasks_assigned_count: 4,
    tasks_submitted_count: 3,
    feedback_submitted_count: 3,
    submission_rate: 0.75,
    last_feedback_at: '2026-04-09T08:00:00Z',
    updated_at: '2026-04-09T09:30:00Z'
  },
  qualification_snapshot: {
    device_profile_id: 'dp_123',
    device_profile_name: 'QA iPhone 15',
    qualification_status: 'qualified',
    matched_rule_id: 'er_123',
    reason_codes: [],
    reason_summary: '符合目前活動的資格條件。'
  },
  campaign: {
    id: 'camp_123',
    project_id: 'proj_123',
    name: 'Closed Beta Round 1',
    description: 'Collect early usability feedback for the onboarding flow.',
    target_platforms: ['ios'],
    version_label: '0.9.0-beta.1',
    status: 'active',
    created_at: '2026-04-08T09:30:00Z',
    updated_at: '2026-04-09T09:30:00Z'
  },
  campaign_reputation: {
    campaign_id: 'camp_123',
    tasks_total_count: 4,
    tasks_closed_count: 2,
    feedback_received_count: 3,
    closure_rate: 0.5,
    last_feedback_at: '2026-04-09T08:00:00Z',
    updated_at: '2026-04-09T09:30:00Z'
  }
}

test.describe('participation request detail flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.removeItem('beta-feedback-platform.current-actor-id')
    })

    await page.route(/\/api\/v1\/participation-requests\/[^/]+\/timeline$/, async (route) => {
      const url = route.request().url()
      const body = url.includes('/pr_123/timeline')
        ? {
            items: [
              {
                id: 'evt_003',
                entity_type: 'participation_request',
                entity_id: 'pr_123',
                event_type: 'task_created_from_participation_request',
                actor_account_id: developerAccount.id,
                actor_account_display_name: developerAccount.display_name,
                summary: '從參與意圖建立任務。',
                created_at: '2026-04-09T10:10:00Z'
              },
              {
                id: 'evt_002',
                entity_type: 'participation_request',
                entity_id: 'pr_123',
                event_type: 'participation_request_accepted',
                actor_account_id: developerAccount.id,
                actor_account_display_name: developerAccount.display_name,
                summary: '接受參與意圖。',
                created_at: '2026-04-09T10:00:00Z'
              },
              {
                id: 'evt_001',
                entity_type: 'participation_request',
                entity_id: 'pr_123',
                event_type: 'participation_request_created',
                actor_account_id: testerAccount.id,
                actor_account_display_name: testerAccount.display_name,
                summary: '送出參與意圖。',
                created_at: '2026-04-09T09:30:00Z'
              }
            ],
            total: 3
          }
        : {
            items: [],
            total: 0
          }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(body)
      })
    })
  })

  test('navigates from the review queue to the detail page and renders candidate snapshots', async ({
    page
  }) => {
    await page.route(/\/api\/v1\/accounts$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [developerAccount, testerAccount],
          total: 2
        })
      })
    })

    await page.route(/\/api\/v1\/participation-requests\?review_mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(developerAccount.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: 'pr_123',
              campaign_id: 'camp_123',
              campaign_name: 'Closed Beta Round 1',
              tester_account_id: testerAccount.id,
              device_profile_id: 'dp_123',
              device_profile_name: 'QA iPhone 15',
  status: 'accepted',
              note: 'I can help cover onboarding and retention flows.',
              decision_note: null,
              created_at: '2026-04-09T09:30:00Z',
              updated_at: '2026-04-09T09:30:00Z',
              decided_at: '2026-04-09T10:00:00Z',
              linked_task_id: null,
              assignment_created_at: null,
              assignment_status: 'not_assigned'
            }
          ],
          total: 1
        })
      })
    })

    await page.route(/\/api\/v1\/participation-requests\/pr_123$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(developerAccount.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(enrichedRequestDetail)
      })
    })

    await page.goto('/review/participation-requests')
    await page.getByTestId('current-actor-select').first().selectOption(developerAccount.id)
    await page.getByTestId('review-participation-detail-link-pr_123').click()

    await expect(page).toHaveURL(/\/review\/participation-requests\/pr_123$/)
    await expect(page.getByTestId('participation-request-detail-panel')).toContainText(
      'Closed Beta Round 1'
    )
    await expect(page.getByTestId('participation-request-tester-panel')).toContainText(
      'QA Tester'
    )
    await expect(page.getByTestId('participation-request-device-profile-panel')).toContainText(
      'testflight'
    )
    await expect(page.getByTestId('participation-request-qualification-panel')).toContainText(
      '符合資格'
    )
    await expect(page.getByTestId('participation-request-create-task-link')).toBeVisible()
    await expect(page.getByTestId('participation-request-detail-panel')).toContainText(
      '任務橋接 尚未建立任務'
    )
    await expect(page.getByTestId('participation-request-timeline-panel')).toContainText(
      '從參與意圖建立任務。'
    )
    await expect(page.getByTestId('participation-request-timeline-panel')).toContainText(
      'Release Owner'
    )
    await expect(page.getByTestId('participation-request-campaign-panel')).toContainText(
      '0.50'
    )
  })

  test('renders the detail error state when the request detail cannot be loaded', async ({
    page
  }) => {
    await page.route(/\/api\/v1\/accounts$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [developerAccount],
          total: 1
        })
      })
    })

    await page.route(/\/api\/v1\/participation-requests\/pr_missing$/, async (route) => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 'resource_not_found',
          message: 'Participation request not found.',
          details: {
            resource: 'participation_request',
            id: 'pr_missing'
          }
        })
      })
    })

    await page.goto('/review/participation-requests/pr_missing')
    await page.getByTestId('current-actor-select').first().selectOption(developerAccount.id)

    await expect(page.getByTestId('participation-request-detail-error')).toBeVisible()
  })

  test('shows a clear ownership mismatch message when the selected developer cannot access the request', async ({
    page
  }) => {
    await page.route(/\/api\/v1\/accounts$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [developerAccount],
          total: 1
        })
      })
    })

    await page.route(/\/api\/v1\/participation-requests\/pr_123$/, async (route) => {
      await route.fulfill({
        status: 409,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 'ownership_mismatch',
          message: 'Current actor does not own the target resource.',
          details: {
            actor_id: developerAccount.id,
            resource: 'participation_request',
            ownership_anchor: {
              resource: 'project',
              id: 'proj_other',
              owner_account_id: 'acct_other_dev'
            }
          }
        })
      })
    })

    await page.goto('/review/participation-requests/pr_123')
    await page.getByTestId('current-actor-select').first().selectOption(developerAccount.id)

    await expect(page.getByTestId('participation-request-detail-error')).toContainText(
      '你不能查看不屬於自己工作範圍的資料。'
    )
  })
})
