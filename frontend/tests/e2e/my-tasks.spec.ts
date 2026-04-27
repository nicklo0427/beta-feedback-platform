import { expect, test } from '@playwright/test'

import {
  formatTaskResolutionOutcomeLabel,
  formatTaskStatusLabel,
  type TaskStatus
} from '~/features/tasks/types'

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

const dualRoleDeveloperPrimaryAccount = {
  id: 'acct_dual_123',
  display_name: 'Dual Role Maker',
  role: 'developer',
  roles: ['developer', 'tester'],
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

const resolvedClosedTask = {
  ...assignedTask,
  status: 'closed',
  resolution_context: {
    resolution_outcome: 'confirmed_issue',
    resolution_note: '已確認 onboarding 首次開啟會 crash。',
    resolved_at: '2026-04-03T12:10:00Z',
    resolved_by_account_id: 'acct_dev_123',
    resolved_by_account_display_name: 'Dev Lead'
  }
}

test.describe('my tasks inbox flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.removeItem('beta-feedback-platform.current-actor-id')
    })

    await page.route(/\/api\/v1\/tasks\/[^/]+\/timeline$/, async (route) => {
      const taskId = route.request().url().match(/\/tasks\/([^/]+)\/timeline$/)?.[1] ?? 'task_unknown'
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: `evt_${taskId}`,
              entity_type: 'task',
              entity_id: taskId,
              event_type: 'task_created',
              actor_account_id: developerAccount.id,
              actor_account_display_name: developerAccount.display_name,
              summary: '建立任務。',
              created_at: '2026-04-03T09:00:00Z'
            }
          ],
          total: 1
        })
      })
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
    await page.getByTestId('current-actor-select').first().selectOption(testerAccount.id)

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
    await page.getByTestId('current-actor-select').first().selectOption(testerAccount.id)

    await expect(page.getByTestId('my-tasks-empty')).toBeVisible()
  })

  test('allows a dual-role account into tester inbox even when primary role is developer', async ({
    page
  }) => {
    await page.route(/\/api\/v1\/accounts$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [dualRoleDeveloperPrimaryAccount],
          total: 1
        })
      })
    })
    await page.route(/\/api\/v1\/tasks\?status=assigned&mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(dualRoleDeveloperPrimaryAccount.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [assignedTask],
          total: 1
        })
      })
    })

    await page.goto('/my/tasks')
    await page.getByTestId('current-actor-select').first().selectOption(dualRoleDeveloperPrimaryAccount.id)

    await expect(page.getByTestId('my-tasks-list')).toBeVisible()
    await expect(page.getByTestId('my-tasks-role-mismatch')).toHaveCount(0)
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
    await page.getByTestId('current-actor-select').first().selectOption(testerAccount.id)
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
    await page.getByTestId('current-actor-select').first().selectOption(testerAccount.id)

    await expect(page.getByTestId('my-task-drift-chip-task_123')).toBeVisible()
    await expect(page.getByTestId('my-task-drift-warning-task_123')).toContainText(
      '已不再符合這次活動'
    )
  })

  test('shows task resolution summary in the tester inbox', async ({ page }) => {
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
    await page.route(/\/api\/v1\/tasks\?status=closed&mine=true$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [resolvedClosedTask],
          total: 1
        })
      })
    })

    await page.goto('/my/tasks')
    await page.getByTestId('current-actor-select').first().selectOption(testerAccount.id)
    await page.getByTestId('my-tasks-filter-closed').click()

    await expect(page.getByTestId('my-task-resolution-chip-task_123')).toContainText(
      formatTaskResolutionOutcomeLabel('confirmed_issue')
    )
    await expect(page.getByTestId('my-task-resolution-summary-task_123')).toContainText(
      resolvedClosedTask.resolution_context.resolved_at
    )
    await expect(page.getByTestId('my-task-resolution-note-task_123')).toContainText(
      resolvedClosedTask.resolution_context.resolution_note
    )
  })
})
