import { expect, test } from '@playwright/test'

import { formatParticipationRequestStatusLabel } from '~/features/participation-requests/types'

const testerAccount = {
  id: 'acct_tester_123',
  display_name: 'QA Tester',
  role: 'tester',
  updated_at: '2026-04-09T09:30:00Z'
}

const developerAccount = {
  id: 'acct_dev_123',
  display_name: 'Release Owner',
  role: 'developer',
  updated_at: '2026-04-09T09:30:00Z'
}

test.describe('participation requests flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.removeItem('beta-feedback-platform.current-actor-id')
    })
  })

  test('lists my participation requests and allows withdrawing a pending request', async ({
    page
  }) => {
    let participationRequestsResponse = {
      items: [
        {
          id: 'pr_123',
          campaign_id: 'camp_123',
          campaign_name: 'Closed Beta Round 1',
          tester_account_id: testerAccount.id,
          device_profile_id: 'dp_123',
          device_profile_name: 'QA iPhone 15',
          status: 'pending',
          note: 'Please consider me for the onboarding beta.',
          decision_note: null,
          created_at: '2026-04-09T09:30:00Z',
          updated_at: '2026-04-09T09:30:00Z',
          decided_at: null
        }
      ],
      total: 1
    }

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
    await page.route(/\/api\/v1\/participation-requests\?mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(testerAccount.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(participationRequestsResponse)
      })
    })
    await page.route(/\/api\/v1\/participation-requests\/pr_123$/, async (route) => {
      if (route.request().method() !== 'PATCH') {
        await route.fallback()
        return
      }

      expect(route.request().headers()['x-actor-id']).toBe(testerAccount.id)
      expect(JSON.parse(route.request().postData() ?? '{}')).toEqual({
        status: 'withdrawn'
      })

      participationRequestsResponse = {
        items: [
          {
            ...participationRequestsResponse.items[0],
            status: 'withdrawn',
            updated_at: '2026-04-09T09:45:00Z'
          }
        ],
        total: 1
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(participationRequestsResponse.items[0])
      })
    })

    await page.goto('/my/participation-requests')
    await page.getByTestId('current-actor-select').selectOption(testerAccount.id)

    const card = page.getByTestId('participation-request-card-pr_123')
    await expect(card).toContainText('Closed Beta Round 1')
    await expect(card).toContainText(formatParticipationRequestStatusLabel('pending'))
    await page.getByTestId('participation-request-withdraw-pr_123').click()

    await expect(card).toContainText(formatParticipationRequestStatusLabel('withdrawn'))
    await expect(page.getByTestId('participation-request-withdraw-pr_123')).toHaveCount(0)
  })

  test('shows role mismatch when a developer opens my participation requests', async ({
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

    await page.goto('/my/participation-requests')
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)

    await expect(page.getByTestId('my-participation-requests-role-mismatch')).toBeVisible()
  })
})
