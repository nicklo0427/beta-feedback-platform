import { expect, test } from '@playwright/test'

import { mockApiError, mockApiJson } from './support/api-mocks'

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

const feedbackListItem = {
  id: 'fb_123',
  task_id: 'task_123',
  summary: 'App crashes on launch',
  severity: 'high',
  category: 'bug',
  submitted_at: '2026-04-03T11:31:00Z'
}

const feedbackDetail = {
  id: 'fb_123',
  task_id: 'task_123',
  campaign_id: 'camp_123',
  device_profile_id: 'dp_123',
  summary: 'App crashes on launch',
  rating: 4,
  severity: 'high',
  category: 'bug',
  reproduction_steps: 'Open the app and wait three seconds.',
  expected_result: 'The app should stay open.',
  actual_result: 'The app exits immediately.',
  note: 'Observed twice on the same device.',
  submitted_at: '2026-04-03T11:31:00Z',
  updated_at: '2026-04-03T11:31:00Z'
}

test.describe('feedback shell flows', () => {
  test('renders task feedback list and navigates to the feedback detail page', async ({
    page
  }) => {
    await mockApiJson(page, '/tasks/task_123', taskDetail)
    await mockApiJson(page, '/tasks/task_123/feedback', {
      items: [feedbackListItem],
      total: 1
    })
    await mockApiJson(page, '/feedback/fb_123', feedbackDetail)

    await page.goto('/tasks/task_123')

    const feedbackList = page.getByTestId('task-feedback-list')
    await expect(feedbackList).toBeVisible()

    const feedbackCard = page.getByTestId('feedback-card-fb_123')
    await expect(feedbackCard).toBeVisible()
    await expect(feedbackCard).toContainText(feedbackListItem.summary)
    await expect(feedbackCard).toContainText(feedbackListItem.category)

    await feedbackCard.click()

    await expect(page).toHaveURL(/\/tasks\/task_123\/feedback\/fb_123$/)

    const detailPanel = page.getByTestId('feedback-detail-panel')
    await expect(detailPanel).toBeVisible()
    await expect(detailPanel).toContainText(feedbackDetail.summary)
    await expect(detailPanel).toContainText(feedbackDetail.reproduction_steps)
    await expect(detailPanel).toContainText(String(feedbackDetail.rating))
  })

  test('renders the task feedback empty state when the API returns no items', async ({
    page
  }) => {
    await mockApiJson(page, '/tasks/task_123', taskDetail)
    await mockApiJson(page, '/tasks/task_123/feedback', {
      items: [],
      total: 0
    })

    await page.goto('/tasks/task_123')

    await expect(page.getByTestId('task-feedback-empty')).toBeVisible()
    await expect(page.getByTestId('task-feedback-list')).toHaveCount(0)
  })

  test('renders the task feedback error state when the nested request fails', async ({
    page
  }) => {
    await mockApiJson(page, '/tasks/task_123', taskDetail)
    await mockApiError(
      page,
      '/tasks/task_123/feedback',
      {
        code: 'internal_error',
        message: 'Feedback unavailable.',
        details: null
      },
      {
        status: 500
      }
    )

    await page.goto('/tasks/task_123')

    const errorState = page.getByTestId('task-feedback-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Feedback unavailable.')
  })
})
