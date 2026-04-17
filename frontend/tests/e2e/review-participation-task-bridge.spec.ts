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

const acceptedRequest = {
  id: 'pr_accepted',
  campaign_id: 'camp_123',
  campaign_name: 'Closed Beta Round 1',
  tester_account_id: testerAccount.id,
  device_profile_id: 'dp_123',
  device_profile_name: 'QA iPhone 15',
  status: 'accepted',
  note: 'I can help cover onboarding and retention flows.',
  decision_note: '目前很適合轉進任務執行。',
  created_at: '2026-04-09T09:30:00Z',
  updated_at: '2026-04-09T10:00:00Z',
  decided_at: '2026-04-09T10:00:00Z',
  linked_task_id: null,
  assignment_created_at: null,
  assignment_status: 'not_assigned'
}

const acceptedRequestDetail = {
  ...acceptedRequest,
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

test.describe('participation request to task bridge', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.removeItem('beta-feedback-platform.current-actor-id')
    })

    await page.route(/\/api\/v1\/participation-requests\/[^/]+\/timeline$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: 'evt_request',
              entity_type: 'participation_request',
              entity_id: 'pr_accepted',
              event_type: 'participation_request_accepted',
              actor_account_id: developerAccount.id,
              actor_account_display_name: developerAccount.display_name,
              summary: '接受參與意圖。',
              created_at: '2026-04-09T10:00:00Z'
            }
          ],
          total: 1
        })
      })
    })

    await page.route(/\/api\/v1\/tasks\/[^/]+\/timeline$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: 'evt_task',
              entity_type: 'task',
              entity_id: 'task_900',
              event_type: 'task_created_from_participation_request',
              actor_account_id: developerAccount.id,
              actor_account_display_name: developerAccount.display_name,
              summary: '從參與意圖建立任務。',
              created_at: '2026-04-09T10:30:00Z'
            }
          ],
          total: 1
        })
      })
    })
  })

  test('developer can create a task from an accepted participation request', async ({
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
          items: [acceptedRequest],
          total: 1
        })
      })
    })

    await page.route(/\/api\/v1\/participation-requests\/pr_accepted$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(developerAccount.id)

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(acceptedRequestDetail)
      })
    })

    await page.route(/\/api\/v1\/participation-requests\/pr_accepted\/tasks$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(developerAccount.id)
      expect(JSON.parse(route.request().postData() ?? '{}')).toEqual({
        title: 'Validate accepted request bridge',
        instruction_summary: 'Focus on onboarding and first-run polish.',
        status: 'assigned'
      })
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'task_900',
          campaign_id: 'camp_123',
          device_profile_id: 'dp_123',
          title: 'Validate accepted request bridge',
          instruction_summary: 'Focus on onboarding and first-run polish.',
          status: 'assigned',
          submitted_at: null,
          created_at: '2026-04-09T10:30:00Z',
          updated_at: '2026-04-09T10:30:00Z',
          qualification_context: {
            device_profile_id: 'dp_123',
            device_profile_name: 'QA iPhone 15',
            qualification_status: 'qualified',
            matched_rule_id: 'er_123',
            reason_summary: '符合目前活動的資格條件。',
            qualification_drift: false
          }
        })
      })
    })

    await page.route(/\/api\/v1\/campaigns\/camp_123\/qualification-check\?device_profile_id=dp_123$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(developerAccount.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          device_profile_id: 'dp_123',
          device_profile_name: 'QA iPhone 15',
          qualification_status: 'qualified',
          matched_rule_id: 'er_123',
          reason_codes: [],
          reason_summary: '符合目前活動的資格條件。'
        })
      })
    })

    await page.route(/\/api\/v1\/tasks\/task_900$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'task_900',
          campaign_id: 'camp_123',
          device_profile_id: 'dp_123',
          title: 'Validate accepted request bridge',
          instruction_summary: 'Focus on onboarding and first-run polish.',
          status: 'assigned',
          submitted_at: null,
          created_at: '2026-04-09T10:30:00Z',
          updated_at: '2026-04-09T10:30:00Z',
          qualification_context: {
            device_profile_id: 'dp_123',
            device_profile_name: 'QA iPhone 15',
            qualification_status: 'qualified',
            matched_rule_id: 'er_123',
            reason_summary: '符合目前活動的資格條件。',
            qualification_drift: false
          }
        })
      })
    })

    await page.route(/\/api\/v1\/tasks\/task_900\/feedback$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0
        })
      })
    })

    await page.goto('/review/participation-requests')
    await page.getByTestId('current-actor-select').first().selectOption(developerAccount.id)
    await page.getByTestId('review-participation-create-task-pr_accepted').click()

    await expect(page).toHaveURL(/\/review\/participation-requests\/pr_accepted\/tasks\/new$/)
    await expect(page.getByTestId('participation-request-task-create-panel')).toBeVisible()
    await expect(page.getByTestId('task-device-profile-field')).toBeDisabled()

    await page.getByTestId('task-title-input').fill('Validate accepted request bridge')
    await page
      .getByTestId('task-instruction-summary-input')
      .fill('Focus on onboarding and first-run polish.')
    await page.getByTestId('task-submit').click()

    await expect(page).toHaveURL(/\/tasks\/task_900$/)
    await expect(page.getByTestId('task-detail-panel')).toContainText(
      'Validate accepted request bridge'
    )
    await expect(page.getByTestId('task-qualification-context')).toContainText('符合資格')
  })
})
