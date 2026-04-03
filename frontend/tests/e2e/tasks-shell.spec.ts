import { expect, test } from '@playwright/test'

import { mockApiError, mockApiJson } from './support/api-mocks'

const taskListItem = {
  id: 'task_123',
  campaign_id: 'camp_123',
  device_profile_id: 'dp_123',
  title: 'Validate onboarding flow',
  status: 'assigned',
  updated_at: '2026-04-03T10:00:00Z'
}

const taskDetail = {
  id: 'task_123',
  campaign_id: 'camp_123',
  device_profile_id: 'dp_123',
  title: 'Validate onboarding flow',
  instruction_summary: 'Verify the welcome experience and account creation handoff.',
  status: 'submitted',
  submitted_at: '2026-04-03T11:30:00Z',
  created_at: '2026-04-03T09:00:00Z',
  updated_at: '2026-04-03T11:30:00Z'
}

test.describe('tasks shell flows', () => {
  test('navigates from home to tasks list and detail', async ({ page }) => {
    await mockApiJson(page, '/tasks', {
      items: [taskListItem],
      total: 1
    })
    await mockApiJson(page, '/tasks/task_123', taskDetail)
    await mockApiJson(page, '/tasks/task_123/feedback', {
      items: [],
      total: 0
    })

    await page.goto('/')
    await page.getByTestId('home-tasks-link').click()

    await expect(page).toHaveURL(/\/tasks$/)
    await expect(page.getByTestId('tasks-list')).toBeVisible()

    const taskCard = page.getByTestId('task-card-task_123')
    await expect(taskCard).toBeVisible()
    await expect(taskCard).toContainText(taskListItem.title)
    await expect(taskCard).toContainText(taskListItem.status)

    await taskCard.click()

    await expect(page).toHaveURL(/\/tasks\/task_123$/)

    const detailPanel = page.getByTestId('task-detail-panel')
    await expect(detailPanel).toBeVisible()
    await expect(detailPanel).toContainText(taskDetail.title)
    await expect(detailPanel).toContainText(taskDetail.status)
    await expect(detailPanel).toContainText(taskDetail.submitted_at)
    await expect(page.getByTestId('task-feedback-empty')).toBeVisible()
  })

  test('renders the tasks empty state when the API returns no items', async ({
    page
  }) => {
    await mockApiJson(page, '/tasks', {
      items: [],
      total: 0
    })

    await page.goto('/tasks')

    await expect(page.getByTestId('tasks-empty')).toBeVisible()
    await expect(page.getByTestId('tasks-list')).toHaveCount(0)
  })

  test('renders the task detail error state when the detail request fails', async ({
    page
  }) => {
    await mockApiError(
      page,
      '/tasks/task_missing',
      {
        code: 'resource_not_found',
        message: 'Task not found.',
        details: {
          resource: 'task',
          id: 'task_missing'
        }
      },
      {
        status: 404
      }
    )

    await page.goto('/tasks/task_missing')

    const errorState = page.getByTestId('task-detail-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Task not found.')
    await expect(page.getByTestId('task-detail-panel')).toHaveCount(0)
  })
})
