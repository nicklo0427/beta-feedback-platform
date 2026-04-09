import { expect, test } from '@playwright/test'

import { formatTaskStatusLabel, type TaskStatus } from '~/features/tasks/types'

const testerAccount = {
  id: 'acct_tester_123',
  display_name: 'QA Tester',
  role: 'tester',
  updated_at: '2026-04-03T09:30:00Z'
}

const developerAccount = {
  id: 'acct_dev_123',
  display_name: 'Dev Lead',
  role: 'developer',
  updated_at: '2026-04-03T09:30:00Z'
}

const assignedTask = {
  id: 'task_123',
  campaign_id: 'camp_123',
  device_profile_id: 'dp_123',
  title: 'Validate onboarding flow',
  status: 'assigned',
  updated_at: '2026-04-03T10:00:00Z',
  qualification_context: {
    device_profile_id: 'dp_123',
    device_profile_name: 'QA iPhone 15',
    qualification_status: 'qualified',
    matched_rule_id: 'er_123',
    reason_summary: '符合目前活動的資格條件。',
    qualification_drift: false
  }
}

const inProgressTaskDetail = {
  id: 'task_123',
  campaign_id: 'camp_123',
  device_profile_id: 'dp_123',
  title: 'Validate onboarding flow',
  instruction_summary: 'Verify the welcome experience and account creation handoff.',
  status: 'in_progress',
  submitted_at: null,
  created_at: '2026-04-03T09:00:00Z',
  updated_at: '2026-04-03T10:20:00Z',
  qualification_context: {
    device_profile_id: 'dp_123',
    device_profile_name: 'QA iPhone 15',
    qualification_status: 'qualified',
    matched_rule_id: 'er_123',
    reason_summary: '符合目前活動的資格條件。',
    qualification_drift: false
  }
}

test.describe('my tasks inbox flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.removeItem('beta-feedback-platform.current-actor-id')
    })
  })

  test('shows the tester inbox and navigates to task detail', async ({ page }) => {
    await page.route(/\/api\/v1\/accounts$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [testerAccount, developerAccount],
          total: 2
        })
      })
    })
    await page.route(/\/api\/v1\/tasks\?status=assigned&mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(testerAccount.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [assignedTask],
          total: 1
        })
      })
    })
    await page.route(/\/api\/v1\/tasks\/task_123$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...inProgressTaskDetail,
          status: 'assigned',
          updated_at: assignedTask.updated_at
        })
      })
    })
    await page.route(/\/api\/v1\/tasks\/task_123\/feedback$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0
        })
      })
    })

    await page.goto('/my/tasks')
    await page.getByTestId('current-actor-select').selectOption(testerAccount.id)

    await expect(page.getByTestId('my-tasks-list')).toBeVisible()
    const taskCard = page.getByTestId('my-task-card-task_123')
    await expect(taskCard).toContainText(assignedTask.title)
    await expect(taskCard).toContainText(formatTaskStatusLabel(assignedTask.status as TaskStatus))
    await expect(page.getByTestId('my-task-qualification-summary-task_123')).toContainText(
      assignedTask.qualification_context.reason_summary
    )

    await page.getByTestId('my-task-detail-link-task_123').click()

    await expect(page).toHaveURL(/\/tasks\/task_123$/)
    await expect(page.getByTestId('task-detail-panel')).toContainText(
      assignedTask.title
    )
    await expect(page.getByTestId('task-feedback-empty')).toBeVisible()
  })

  test('renders the tester inbox empty state when no tasks match the active status', async ({
    page
  }) => {
    await page.route(/\/api\/v1\/accounts$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [testerAccount],
          total: 1
        })
      })
    })
    await page.route(/\/api\/v1\/tasks\?status=assigned&mine=true$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0
        })
      })
    })

    await page.goto('/my/tasks')
    await page.getByTestId('current-actor-select').selectOption(testerAccount.id)

    await expect(page.getByTestId('my-tasks-empty')).toBeVisible()
  })

  test('supports the assigned to in-progress quick action from the tester inbox', async ({
    page
  }) => {
    let hasStartedTask = false

    await page.route(/\/api\/v1\/accounts$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [testerAccount],
          total: 1
        })
      })
    })
    await page.route(/\/api\/v1\/tasks\?status=assigned&mine=true$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: hasStartedTask ? [] : [assignedTask],
          total: hasStartedTask ? 0 : 1
        })
      })
    })
    await page.route(/\/api\/v1\/tasks\?status=in_progress&mine=true$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: hasStartedTask
            ? [
                {
                  id: inProgressTaskDetail.id,
                  campaign_id: inProgressTaskDetail.campaign_id,
                  device_profile_id: inProgressTaskDetail.device_profile_id,
                  title: inProgressTaskDetail.title,
                  status: inProgressTaskDetail.status,
                  updated_at: inProgressTaskDetail.updated_at
                }
              ]
            : [],
          total: hasStartedTask ? 1 : 0
        })
      })
    })
    await page.route(/\/api\/v1\/tasks\/task_123$/, async (route) => {
      if (route.request().method() !== 'PATCH') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(inProgressTaskDetail)
        })
        return
      }

      expect(route.request().headers()['x-actor-id']).toBe(testerAccount.id)
      hasStartedTask = true

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(inProgressTaskDetail)
      })
    })

    await page.goto('/my/tasks')
    await page.getByTestId('current-actor-select').selectOption(testerAccount.id)
    const updateRequestPromise = page.waitForRequest((request) => {
      return /\/api\/v1\/tasks\/task_123$/.test(request.url()) && request.method() === 'PATCH'
    })
    await page.getByTestId('my-task-start-task_123').click()

    const updateRequest = await updateRequestPromise
    expect(updateRequest.postDataJSON()).toEqual({
      status: 'in_progress'
    })

    await expect(page.getByTestId('my-tasks-empty')).toBeVisible()
    await page.getByTestId('my-tasks-filter-in_progress').click()
    await expect(page.getByTestId('my-tasks-list')).toBeVisible()
    await expect(page.getByTestId('my-task-card-task_123')).toContainText(
      formatTaskStatusLabel('in_progress')
    )
  })

  test('shows qualification drift warning in the tester inbox', async ({ page }) => {
    await page.route(/\/api\/v1\/accounts$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [testerAccount],
          total: 1
        })
      })
    })
    await page.route(/\/api\/v1\/tasks\?status=assigned&mine=true$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              ...assignedTask,
              qualification_context: {
                ...assignedTask.qualification_context,
                qualification_status: 'not_qualified',
                matched_rule_id: null,
                reason_summary:
                  '主要未符合條件：平台不符合目前活動條件；作業系統不符合目前活動條件。',
                qualification_drift: true
              }
            }
          ],
          total: 1
        })
      })
    })

    await page.goto('/my/tasks')
    await page.getByTestId('current-actor-select').selectOption(testerAccount.id)

    await expect(page.getByTestId('my-task-drift-chip-task_123')).toBeVisible()
    await expect(page.getByTestId('my-task-drift-warning-task_123')).toContainText(
      '已不再符合活動條件'
    )
  })
})
