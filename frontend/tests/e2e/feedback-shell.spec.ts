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

interface FeedbackDetailFixture {
  id: string
  task_id: string
  campaign_id: string
  device_profile_id: string
  summary: string
  rating: number
  severity: string
  category: string
  reproduction_steps: string
  expected_result: string
  actual_result: string
  note: string | null
  review_status: 'submitted' | 'needs_more_info' | 'reviewed'
  developer_note: string | null
  submitted_at: string
  updated_at: string
}

const feedbackDetail: FeedbackDetailFixture = {
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
  review_status: 'submitted',
  developer_note: null,
  submitted_at: '2026-04-03T11:31:00Z',
  updated_at: '2026-04-03T11:31:00Z'
}

test.describe('feedback shell flows', () => {
  test('supports creating feedback from the task detail flow', async ({ page }) => {
    const createdFeedback = {
      ...feedbackDetail,
      id: 'fb_456',
      summary: 'Onboarding copy is unclear',
      severity: 'medium',
      category: 'usability',
      rating: 3,
      reproduction_steps: 'Open the sign-up screen and read the helper copy.',
      expected_result: 'The copy should clearly explain what happens next.',
      actual_result: 'The copy is ambiguous for first-time users.',
      note: 'Observed on a fresh account.'
    }

    await mockApiJson(page, '/tasks/task_123', taskDetail)
    await mockApiJson(page, '/tasks/task_123/feedback', {
      items: [],
      total: 0
    })

    await page.route(/\/api\/v1\/tasks\/task_123\/feedback$/, async (route) => {
      if (route.request().method() !== 'POST') {
        await route.fallback()
        return
      }

      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(createdFeedback)
      })
    })

    await page.route(/\/api\/v1\/feedback\/fb_456$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(createdFeedback)
      })
    })

    await page.goto('/tasks/task_123')
    await page.getByTestId('task-feedback-create-link').click()

    await expect(page).toHaveURL(/\/tasks\/task_123\/feedback\/new$/)
    await expect(page.getByTestId('feedback-create-panel')).toBeVisible()

    await page.getByTestId('feedback-summary-input').fill('Onboarding copy is unclear')
    await page.getByTestId('feedback-severity-field').selectOption('medium')
    await page.getByTestId('feedback-category-field').selectOption('usability')
    await page.getByTestId('feedback-rating-field').selectOption('3')
    await page.getByTestId('feedback-note-input').fill('Observed on a fresh account.')
    await page.getByTestId('feedback-submit').click()

    await expect(page).toHaveURL(/\/tasks\/task_123\/feedback\/fb_456$/)

    const detailPanel = page.getByTestId('feedback-detail-panel')
    await expect(detailPanel).toBeVisible()
    await expect(detailPanel).toContainText(createdFeedback.summary)
    await expect(detailPanel).toContainText(createdFeedback.category)
    await expect(page.getByTestId('feedback-review-panel')).toContainText('Submitted')
  })

  test('shows feedback create validation and backend errors', async ({ page }) => {
    await mockApiJson(page, '/tasks/task_123', taskDetail)

    await page.route(/\/api\/v1\/tasks\/task_123\/feedback$/, async (route) => {
      if (route.request().method() !== 'POST') {
        await route.fallback()
        return
      }

      await route.fulfill({
        status: 422,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 'validation_error',
          message: 'Request validation failed.',
          details: {
            fields: [
              {
                field: 'rating',
                message: 'Input should be less than or equal to 5'
              }
            ]
          }
        })
      })
    })

    await page.goto('/tasks/task_123/feedback/new')

    await page.getByTestId('feedback-submit').click()
    await expect(page.getByTestId('feedback-form-error')).toContainText('Summary is required.')

    await page.getByTestId('feedback-summary-input').fill('Animation stutters')
    await page.getByTestId('feedback-severity-field').selectOption('low')
    await page.getByTestId('feedback-category-field').selectOption('performance')
    await page.getByTestId('feedback-submit').click()

    await expect(page.getByTestId('feedback-form-error')).toContainText(
      'Request validation failed.'
    )
  })

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
    await expect(detailPanel).toContainText('Submitted')
  })

  test('supports marking feedback as reviewed from the detail page', async ({ page }) => {
    let currentFeedback: FeedbackDetailFixture = { ...feedbackDetail }

    await page.route(/\/api\/v1\/feedback\/fb_123$/, async (route) => {
      if (route.request().method() === 'PATCH') {
        const payload = route.request().postDataJSON() as {
          review_status?: FeedbackDetailFixture['review_status']
          developer_note?: string | null
        }

        currentFeedback = {
          ...currentFeedback,
          review_status: payload.review_status ?? currentFeedback.review_status,
          developer_note: payload.developer_note ?? currentFeedback.developer_note,
          updated_at: '2026-04-03T12:05:00Z'
        }
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(currentFeedback)
      })
    })

    await page.goto('/tasks/task_123/feedback/fb_123')

    await page.getByTestId('feedback-review-status-field').selectOption('reviewed')
    await page
      .getByTestId('feedback-developer-note-field')
      .fill('Confirmed by the developer after reviewing the crash logs.')
    await page.getByTestId('feedback-review-submit').click()

    await expect(page.getByTestId('feedback-review-success')).toContainText(
      'Review changes saved.'
    )
    await expect(page.getByTestId('feedback-detail-panel')).toContainText('Reviewed')
    await expect(page.getByTestId('feedback-detail-panel')).toContainText(
      'Confirmed by the developer after reviewing the crash logs.'
    )
  })

  test('supports the needs-more-info review path from the detail page', async ({ page }) => {
    let currentFeedback: FeedbackDetailFixture = { ...feedbackDetail }
    let reviewRequestBody: unknown = null

    await page.route(/\/api\/v1\/feedback\/fb_123$/, async (route) => {
      if (route.request().method() === 'PATCH') {
        const payload = route.request().postDataJSON() as {
          review_status?: string
          developer_note?: string | null
        }

        reviewRequestBody = payload

        currentFeedback = {
          ...currentFeedback,
          review_status: 'needs_more_info',
          developer_note: payload.developer_note ?? currentFeedback.developer_note,
          updated_at: '2026-04-03T12:07:00Z'
        }
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(currentFeedback)
      })
    })

    await page.goto('/tasks/task_123/feedback/fb_123')

    await page.getByTestId('feedback-review-status-field').selectOption('needs_more_info')
    await page
      .getByTestId('feedback-developer-note-field')
      .fill('Please include the exact time between launch and crash.')
    await page.getByTestId('feedback-review-submit').click()

    expect(reviewRequestBody).toEqual({
      review_status: 'needs_more_info',
      developer_note: 'Please include the exact time between launch and crash.'
    })

    await expect(page.getByTestId('feedback-review-success')).toContainText(
      'Review changes saved.'
    )
    await expect(page.getByTestId('feedback-detail-panel')).toContainText(
      'Needs More Info'
    )
    await expect(page.getByTestId('feedback-detail-panel')).toContainText(
      'Please include the exact time between launch and crash.'
    )
  })

  test('supports editing feedback from the detail page', async ({ page }) => {
    let currentFeedback = { ...feedbackDetail }

    await mockApiJson(page, '/tasks/task_123', taskDetail)
    await mockApiJson(page, '/tasks/task_123/feedback', {
      items: [feedbackListItem],
      total: 1
    })

    await page.route(/\/api\/v1\/feedback\/fb_123$/, async (route) => {
      if (route.request().method() === 'PATCH') {
        const payload = route.request().postDataJSON() as {
          summary?: string
          note?: string | null
        }

        currentFeedback = {
          ...currentFeedback,
          summary: payload.summary ?? currentFeedback.summary,
          note: payload.note ?? currentFeedback.note,
          updated_at: '2026-04-03T12:00:00Z'
        }
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(currentFeedback)
      })
    })

    await page.goto('/tasks/task_123')
    await page.getByTestId('feedback-card-fb_123').click()
    await page.getByTestId('feedback-edit-link').click()

    await expect(page).toHaveURL(/\/tasks\/task_123\/feedback\/fb_123\/edit$/)
    await expect(page.getByTestId('feedback-edit-panel')).toBeVisible()

    await page.getByTestId('feedback-summary-input').fill('App crashes on launch after splash')
    await page.getByTestId('feedback-note-input').fill('Still reproducible after reinstall.')
    await page.getByTestId('feedback-submit').click()

    await expect(page).toHaveURL(/\/tasks\/task_123\/feedback\/fb_123$/)

    const detailPanel = page.getByTestId('feedback-detail-panel')
    await expect(detailPanel).toContainText('App crashes on launch after splash')
    await expect(detailPanel).toContainText('Still reproducible after reinstall.')
  })

  test('shows backend errors when a feedback update is rejected', async ({ page }) => {
    await page.route(/\/api\/v1\/feedback\/fb_123$/, async (route) => {
      if (route.request().method() === 'PATCH') {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 'internal_error',
            message: 'Unable to update feedback right now.',
            details: null
          })
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(feedbackDetail)
      })
    })

    await page.goto('/tasks/task_123/feedback/fb_123/edit')

    await page.getByTestId('feedback-summary-input').fill('Crash remains after reinstall')
    await page.getByTestId('feedback-submit').click()

    await expect(page.getByTestId('feedback-form-error')).toContainText(
      'Unable to update feedback right now.'
    )
  })

  test('shows backend validation errors when a feedback review update is rejected', async ({
    page
  }) => {
    await page.route(/\/api\/v1\/feedback\/fb_123$/, async (route) => {
      if (route.request().method() === 'PATCH') {
        await route.fulfill({
          status: 422,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 'validation_error',
            message: 'Request validation failed.',
            details: {
              fields: [
                {
                  field: 'review_status',
                  message: "Input should be 'submitted', 'needs_more_info' or 'reviewed'"
                }
              ]
            }
          })
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(feedbackDetail)
      })
    })

    await page.goto('/tasks/task_123/feedback/fb_123')

    await page.getByTestId('feedback-review-status-field').selectOption('reviewed')
    await page.getByTestId('feedback-review-submit').click()

    await expect(page.getByTestId('feedback-review-error')).toContainText(
      'Request validation failed.'
    )
  })

  test('renders the feedback edit error state when the record cannot be loaded', async ({
    page
  }) => {
    await mockApiError(
      page,
      '/feedback/fb_missing',
      {
        code: 'resource_not_found',
        message: 'Feedback not found.',
        details: {
          resource: 'feedback',
          id: 'fb_missing'
        }
      },
      {
        status: 404
      }
    )

    await page.goto('/tasks/task_123/feedback/fb_missing/edit')

    const errorState = page.getByTestId('feedback-edit-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Feedback not found.')
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
