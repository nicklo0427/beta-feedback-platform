import { expect, test } from '@playwright/test'

import { formatCampaignStatusLabel } from '~/features/campaigns/types'

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

const eligibleCampaign = {
  id: 'camp_123',
  project_id: 'proj_123',
  name: 'iOS Closed Beta',
  target_platforms: ['ios'],
  version_label: '0.9.0-beta.1',
  status: 'active',
  updated_at: '2026-04-03T10:00:00Z',
  qualifying_device_profiles: [
    {
      id: 'dp_123',
      name: 'QA iPhone 15'
    }
  ],
  qualification_summary: '目前有 1 個裝置設定檔符合這個活動資格。'
} as const

test.describe('eligible campaigns workspace flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.removeItem('beta-feedback-platform.current-actor-id')
    })
  })

  test('opens the tester eligible campaigns workspace and navigates to campaign detail', async ({
    page
  }) => {
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
    await page.route(/\/api\/v1\/device-profiles\?mine=true$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
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
    await page.route(/\/api\/v1\/tasks\?status=in_progress&mine=true$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0
        })
      })
    })
    await page.route(/\/api\/v1\/campaigns\?qualified_for_me=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(testerAccount.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [eligibleCampaign],
          total: 1
        })
      })
    })
    await page.route(/\/api\/v1\/campaigns\/camp_123$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'camp_123',
          project_id: 'proj_123',
          name: 'iOS Closed Beta',
          description: 'Collect onboarding feedback from current iOS testers.',
          target_platforms: ['ios'],
          version_label: '0.9.0-beta.1',
          status: 'active',
          created_at: '2026-04-02T09:00:00Z',
          updated_at: '2026-04-03T10:00:00Z'
        })
      })
    })
    await page.route(/\/api\/v1\/campaigns\/camp_123\/safety$/, async (route) => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 'resource_not_found',
          message: 'Campaign safety not found.',
          details: {
            resource: 'campaign_safety',
            campaign_id: 'camp_123'
          }
        })
      })
    })
    await page.route(/\/api\/v1\/campaigns\/camp_123\/eligibility-rules$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0
        })
      })
    })
    await page.route(/\/api\/v1\/campaigns\/camp_123\/qualification-results\?mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(testerAccount.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              device_profile_id: 'dp_123',
              device_profile_name: 'QA iPhone 15',
              qualification_status: 'qualified',
              matched_rule_id: null,
              reason_codes: [],
              reason_summary: '目前沒有啟用中的資格限制。'
            }
          ],
          total: 1
        })
      })
    })

    await page.goto('/my/eligible-campaigns')
    await page.getByTestId('current-actor-select').first().selectOption(testerAccount.id)
    await page.waitForLoadState('networkidle')

    await expect(page).toHaveURL(/\/my\/eligible-campaigns$/)
    await expect(page.getByTestId('my-eligible-campaigns-list')).toBeVisible()
    const campaignCard = page.getByTestId('my-eligible-campaign-card-camp_123')
    await expect(campaignCard).toContainText(eligibleCampaign.name)
    await expect(campaignCard).toContainText(
      formatCampaignStatusLabel(eligibleCampaign.status)
    )
    await expect(campaignCard).toContainText(eligibleCampaign.qualification_summary)
    await expect(page.getByTestId('my-eligible-campaign-chips-camp_123')).toContainText(
      'QA iPhone 15'
    )

    await page.getByTestId('my-eligible-campaign-detail-link-camp_123').click()
    await expect(page).toHaveURL(/\/campaigns\/camp_123$/)
    await expect(page.getByTestId('campaign-detail-panel')).toContainText(eligibleCampaign.name)
  })

  test('renders the tester eligible campaigns empty state when no campaigns qualify', async ({
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
    await page.route(/\/api\/v1\/campaigns\?qualified_for_me=true$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0
        })
      })
    })

    await page.goto('/my/eligible-campaigns')
    await page.getByTestId('current-actor-select').first().selectOption(testerAccount.id)

    await expect(page.getByTestId('my-eligible-campaigns-empty')).toBeVisible()
  })

  test('shows role mismatch when a developer opens the eligible campaigns workspace', async ({
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

    await page.goto('/my/eligible-campaigns')
    await page.getByTestId('current-actor-select').first().selectOption(developerAccount.id)

    await expect(page.getByTestId('my-eligible-campaigns-role-mismatch')).toBeVisible()
  })

  test('supports creating a participation request from the eligible campaigns workspace', async ({
    page
  }) => {
    let createRequestActorId: string | undefined
    let createRequestBody: unknown = null

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
    await page.route(/\/api\/v1\/campaigns\?qualified_for_me=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(testerAccount.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [eligibleCampaign],
          total: 1
        })
      })
    })
    await page.route(
      /\/api\/v1\/campaigns\/camp_123\/participation-requests$/,
      async (route) => {
        if (route.request().method() !== 'POST') {
          await route.fallback()
          return
        }

        createRequestActorId = route.request().headers()['x-actor-id']
        createRequestBody = JSON.parse(route.request().postData() ?? '{}')
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'pr_123',
            campaign_id: eligibleCampaign.id,
            campaign_name: eligibleCampaign.name,
            tester_account_id: testerAccount.id,
            device_profile_id: 'dp_123',
            device_profile_name: 'QA iPhone 15',
            status: 'pending',
            note: 'Please include me in this beta round.',
            decision_note: null,
            created_at: '2026-04-09T09:35:00Z',
            updated_at: '2026-04-09T09:35:00Z',
            decided_at: null
          })
        })
      }
    )

    await page.goto('/my/eligible-campaigns')
    await page.getByTestId('current-actor-select').first().selectOption(testerAccount.id)

    await page
      .getByTestId('eligible-campaign-participation-camp_123-note-input')
      .fill('Please include me in this beta round.')
    await page.getByTestId('eligible-campaign-participation-camp_123-submit').click()

    expect(createRequestActorId).toBe(testerAccount.id)
    expect(createRequestBody).toEqual({
      device_profile_id: 'dp_123',
      note: 'Please include me in this beta round.'
    })

    await expect(
      page.getByTestId('eligible-campaign-participation-camp_123-success')
    ).toContainText('已送出參與意圖')
  })
})
