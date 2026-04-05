import { expect, test } from '@playwright/test'

import {
  formatFeedbackReviewStatusLabel
} from '~/features/feedback/types'

const developerAccount = {
  id: 'acct_dev_123',
  display_name: 'Release Owner',
  role: 'developer',
  updated_at: '2026-04-05T09:30:00Z'
}

const testerAccount = {
  id: 'acct_tester_123',
  display_name: 'QA Tester',
  role: 'tester',
  updated_at: '2026-04-05T09:30:00Z'
}

const submittedFeedback = {
  id: 'fb_123',
  task_id: 'task_123',
  campaign_id: 'camp_123',
  summary: 'App crashes on launch',
  severity: 'high',
  category: 'bug',
  review_status: 'submitted',
  submitted_at: '2026-04-03T11:31:00Z'
}

const needsMoreInfoFeedback = {
  id: 'fb_456',
  task_id: 'task_456',
  campaign_id: 'camp_456',
  summary: 'More launch timing data needed',
  severity: 'medium',
  category: 'usability',
  review_status: 'needs_more_info',
  submitted_at: '2026-04-04T09:20:00Z'
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
  review_status: 'submitted',
  developer_note: null,
  submitted_at: '2026-04-03T11:31:00Z',
  resubmitted_at: null,
  updated_at: '2026-04-03T11:31:00Z'
}

test.describe('feedback review queue flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.removeItem('beta-feedback-platform.current-actor-id')
    })
  })

  test('shows the developer review queue and navigates to feedback detail', async ({
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
    await page.route(/\/api\/v1\/feedback\?mine=true&review_status=submitted$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(developerAccount.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [submittedFeedback],
          total: 1
        })
      })
    })
    await page.route(/\/api\/v1\/feedback\/fb_123$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(feedbackDetail)
      })
    })

    await page.goto('/review/feedback')
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)

    await expect(page.getByTestId('feedback-review-list')).toBeVisible()
    const feedbackCard = page.getByTestId('review-feedback-card-fb_123')
    await expect(feedbackCard).toContainText(submittedFeedback.summary)
    await expect(feedbackCard).toContainText(submittedFeedback.campaign_id)

    await page.getByTestId('review-feedback-link-fb_123').click()

    await expect(page).toHaveURL(/\/tasks\/task_123\/feedback\/fb_123$/)
    await expect(page.getByTestId('feedback-detail-panel')).toContainText(
      feedbackDetail.summary
    )
  })

  test('supports review status filters in the developer queue', async ({ page }) => {
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
    await page.route(/\/api\/v1\/feedback\?mine=true&review_status=submitted$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [submittedFeedback],
          total: 1
        })
      })
    })
    await page.route(
      /\/api\/v1\/feedback\?mine=true&review_status=needs_more_info$/,
      async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [needsMoreInfoFeedback],
            total: 1
          })
        })
      }
    )

    await page.goto('/review/feedback')
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)

    await expect(page.getByTestId('review-feedback-card-fb_123')).toBeVisible()

    await page.getByTestId('feedback-review-filter-needs_more_info').click()

    await expect(page.getByTestId('feedback-review-list')).toBeVisible()
    await expect(page.getByTestId('review-feedback-card-fb_456')).toContainText(
      needsMoreInfoFeedback.summary
    )
    await expect(page.getByTestId('review-feedback-card-fb_456')).toContainText(
      formatFeedbackReviewStatusLabel('needs_more_info')
    )
  })

  test('shows role mismatch when the selected actor is not a developer', async ({
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

    await page.goto('/review/feedback')
    await page.getByTestId('current-actor-select').selectOption(testerAccount.id)

    await expect(page.getByTestId('feedback-review-role-mismatch')).toBeVisible()
  })
})
