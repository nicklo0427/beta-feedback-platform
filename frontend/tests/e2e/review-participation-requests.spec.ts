import { expect, test } from '@playwright/test'

import { formatParticipationRequestStatusLabel } from '~/features/participation-requests/types'

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

test.describe('participation review queue flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.removeItem('beta-feedback-platform.current-actor-id')
    })
  })

  test('developer can accept a participation request and tester sees the updated status', async ({
    page
  }) => {
    let reviewQueueResponse: {
      items: Array<{
        id: string
        campaign_id: string
        campaign_name: string
        tester_account_id: string
        device_profile_id: string
        device_profile_name: string
        status: string
        note: string | null
        decision_note: string | null
        created_at: string
        updated_at: string
        decided_at: string | null
      }>
      total: number
    } = {
      items: [
        {
          id: 'pr_123',
          campaign_id: 'camp_123',
          campaign_name: 'Closed Beta Round 1',
          tester_account_id: testerAccount.id,
          device_profile_id: 'dp_123',
          device_profile_name: 'QA iPhone 15',
          status: 'pending',
          note: 'I can help cover onboarding and retention flows.',
          decision_note: null,
          created_at: '2026-04-09T09:30:00Z',
          updated_at: '2026-04-09T09:30:00Z',
          decided_at: null
        }
      ],
      total: 1
    }

    let myRequestsResponse: typeof reviewQueueResponse = {
      items: reviewQueueResponse.items.map((item) => ({ ...item })),
      total: 1
    }

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
        body: JSON.stringify(reviewQueueResponse)
      })
    })

    await page.route(/\/api\/v1\/participation-requests\?mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(testerAccount.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(myRequestsResponse)
      })
    })

    await page.route(/\/api\/v1\/participation-requests\/pr_123$/, async (route) => {
      if (route.request().method() !== 'PATCH') {
        await route.fallback()
        return
      }

      expect(route.request().headers()['x-actor-id']).toBe(developerAccount.id)
      expect(JSON.parse(route.request().postData() ?? '{}')).toEqual({
        status: 'accepted',
        decision_note: '你的裝置與目前 beta 目標相符。'
      })

      const updatedRequest = {
        ...reviewQueueResponse.items[0],
        status: 'accepted',
        decision_note: '你的裝置與目前 beta 目標相符。',
        updated_at: '2026-04-09T10:00:00Z',
        decided_at: '2026-04-09T10:00:00Z'
      }

      reviewQueueResponse = {
        items: [],
        total: 0
      }
      myRequestsResponse = {
        items: [updatedRequest],
        total: 1
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(updatedRequest)
      })
    })

    await page.goto('/review/participation-requests')
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)

    const card = page.getByTestId('review-participation-request-card-pr_123')
    await expect(card).toContainText('Closed Beta Round 1')
    await page
      .getByTestId('review-participation-decision-note-pr_123')
      .fill('你的裝置與目前 beta 目標相符。')
    await page.getByTestId('review-participation-accept-pr_123').click()

    await expect(page.getByTestId('participation-review-empty')).toBeVisible()

    await page.goto('/my/participation-requests')
    await page.getByTestId('current-actor-select').selectOption(testerAccount.id)

    const testerCard = page.getByTestId('participation-request-card-pr_123')
    await expect(testerCard).toContainText(
      formatParticipationRequestStatusLabel('accepted')
    )
    await expect(testerCard).toContainText('處理備註 你的裝置與目前 beta 目標相符。')
    await expect(testerCard).toContainText('處理時間 2026-04-09T10:00:00Z')
  })

  test('shows role mismatch when a tester opens the participation review queue', async ({
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

    await page.goto('/review/participation-requests')
    await page.getByTestId('current-actor-select').selectOption(testerAccount.id)

    await expect(page.getByTestId('participation-review-role-mismatch')).toBeVisible()
  })
})
