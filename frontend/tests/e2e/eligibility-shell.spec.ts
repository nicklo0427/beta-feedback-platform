import { expect, test, type Page } from '@playwright/test'

import { formatPlatformLabel } from '~/features/platform-display'

import { mockApiError, mockApiJson } from './support/api-mocks'

const campaignDetail = {
  id: 'camp_123',
  project_id: 'proj_123',
  name: 'Closed Beta Round 1',
  description: 'Collect early usability feedback for the onboarding flow.',
  target_platforms: ['ios', 'android'],
  version_label: '0.9.0-beta.1',
  status: 'active',
  created_at: '2026-04-02T09:00:00Z',
  updated_at: '2026-04-03T10:00:00Z'
}

const eligibilityRuleListItem = {
  id: 'er_123',
  campaign_id: 'camp_123',
  platform: 'ios',
  os_name: 'iOS',
  install_channel: 'testflight',
  is_active: true,
  updated_at: '2026-04-03T10:00:00Z'
}

const eligibilityRuleDetail = {
  id: 'er_123',
  campaign_id: 'camp_123',
  platform: 'ios',
  os_name: 'iOS',
  os_version_min: '17.0',
  os_version_max: '18.2',
  install_channel: 'testflight',
  is_active: true,
  created_at: '2026-04-02T10:00:00Z',
  updated_at: '2026-04-03T10:00:00Z'
}

const developerAccount = {
  id: 'acct_dev_123',
  display_name: 'Alice Developer',
  role: 'developer',
  updated_at: '2026-04-03T10:00:00Z'
}

const testerAccount = {
  id: 'acct_tester_123',
  display_name: 'Tim Tester',
  role: 'tester',
  updated_at: '2026-04-03T10:00:00Z'
}

async function mockAccounts(page: Page): Promise<void> {
  await mockApiJson(page, '/accounts', {
    items: [developerAccount, testerAccount],
    total: 2
  })
}

test.describe('eligibility shell flows', () => {
  test('renders campaign eligibility list and navigates to the rule detail page', async ({
    page
  }) => {
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiError(
      page,
      '/campaigns/camp_123/safety',
      {
        code: 'resource_not_found',
        message: 'Campaign safety not found.',
        details: {
          resource: 'campaign_safety',
          campaign_id: 'camp_123'
        }
      },
      {
        status: 404
      }
    )
    await mockApiJson(page, '/campaigns/camp_123/eligibility-rules', {
      items: [eligibilityRuleListItem],
      total: 1
    })
    await mockApiJson(page, '/tasks?campaign_id=camp_123', {
      items: [],
      total: 0
    })
    await mockApiJson(page, '/eligibility-rules/er_123', eligibilityRuleDetail)

    await page.goto('/campaigns/camp_123')

    const eligibilityList = page.getByTestId('campaign-eligibility-list')
    await expect(eligibilityList).toBeVisible()

    const eligibilityCard = page.getByTestId('eligibility-rule-card-er_123')
    await expect(eligibilityCard).toBeVisible()
    await expect(eligibilityCard).toContainText(
      formatPlatformLabel(eligibilityRuleListItem.platform)
    )
    await expect(eligibilityCard).toContainText(eligibilityRuleListItem.install_channel)

    await eligibilityCard.click()

    await expect(page).toHaveURL(/\/campaigns\/camp_123\/eligibility-rules\/er_123$/)

    const detailPanel = page.getByTestId('eligibility-rule-detail-panel')
    await expect(detailPanel).toBeVisible()
    await expect(detailPanel).toContainText(
      formatPlatformLabel(eligibilityRuleDetail.platform)
    )
    await expect(detailPanel).toContainText(eligibilityRuleDetail.os_version_min)
    await expect(detailPanel).toContainText(eligibilityRuleDetail.os_version_max)
  })

  test('supports creating an eligibility rule from the frontend form and returns to campaign detail', async ({
    page
  }) => {
    const createdEligibilityRule = {
      id: 'er_456',
      campaign_id: 'camp_123',
      platform: 'android',
      os_name: 'Android',
      os_version_min: '14',
      os_version_max: '15',
      install_channel: 'google-play-testing',
      is_active: true,
      created_at: '2026-04-03T11:00:00Z',
      updated_at: '2026-04-03T11:00:00Z'
    }

    let createRequestBody: unknown = null
    let createRequestActorId: string | undefined
    let hasCreatedRule = false

    await mockAccounts(page)
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiError(
      page,
      '/campaigns/camp_123/safety',
      {
        code: 'resource_not_found',
        message: 'Campaign safety not found.',
        details: {
          resource: 'campaign_safety',
          campaign_id: 'camp_123'
        }
      },
      {
        status: 404
      }
    )
    await mockApiJson(page, '/tasks?campaign_id=camp_123', {
      items: [],
      total: 0
    })

    await page.route(/\/api\/v1\/campaigns\/camp_123\/eligibility-rules$/, async (route) => {
      const method = route.request().method()

      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: hasCreatedRule
              ? [
                  {
                    id: createdEligibilityRule.id,
                    campaign_id: createdEligibilityRule.campaign_id,
                    platform: createdEligibilityRule.platform,
                    os_name: createdEligibilityRule.os_name,
                    install_channel: createdEligibilityRule.install_channel,
                    is_active: createdEligibilityRule.is_active,
                    updated_at: createdEligibilityRule.updated_at
                  }
                ]
              : [],
            total: hasCreatedRule ? 1 : 0
          })
        })
        return
      }

      if (method === 'POST') {
        createRequestActorId = route.request().headers()['x-actor-id']
        createRequestBody = JSON.parse(route.request().postData() ?? '{}')
        hasCreatedRule = true
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify(createdEligibilityRule)
        })
        return
      }

      await route.fallback()
    })

    await page.goto('/campaigns/camp_123')
    await page.getByTestId('eligibility-rule-create-link').click()

    await expect(page).toHaveURL(/\/campaigns\/camp_123\/eligibility-rules\/new$/)
    await expect(page.getByTestId('eligibility-rule-form')).toBeVisible()

    await page.getByTestId('eligibility-rule-platform-select').selectOption('android')
    await page.getByTestId('eligibility-rule-os-name-input').fill('Android')
    await page.getByTestId('eligibility-rule-os-version-min-input').fill('14')
    await page.getByTestId('eligibility-rule-os-version-max-input').fill('15')
    await page
      .getByTestId('eligibility-rule-install-channel-input')
      .fill('google-play-testing')
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)
    await page.getByTestId('eligibility-rule-submit').click()

    expect(createRequestActorId).toBe(developerAccount.id)
    expect(createRequestBody).toEqual({
      platform: 'android',
      os_name: 'Android',
      os_version_min: '14',
      os_version_max: '15',
      install_channel: 'google-play-testing',
      is_active: true
    })

    await expect(page).toHaveURL(/\/campaigns\/camp_123$/)
    await expect(page.getByTestId('campaign-eligibility-list')).toBeVisible()
    await expect(page.getByTestId('eligibility-rule-card-er_456')).toContainText(
      formatPlatformLabel('android')
    )
  })

  test('shows create eligibility form validation and backend errors', async ({ page }) => {
    await mockAccounts(page)
    await page.route(/\/api\/v1\/campaigns\/camp_123\/eligibility-rules$/, async (route) => {
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
                field: 'platform',
                message: 'This field is required.'
              }
            ]
          }
        })
      })
    })

    await page.goto('/campaigns/camp_123/eligibility-rules/new')
    await expect(page.getByTestId('eligibility-rule-form')).toBeVisible()
    await page.waitForLoadState('networkidle')
    await page.getByTestId('eligibility-rule-submit').click()

    await expect(page.getByTestId('eligibility-rule-form-error')).toContainText(
      '平台為必填。'
    )

    await page.getByTestId('eligibility-rule-platform-select').selectOption('ios')
    await page.getByTestId('eligibility-rule-submit').click()

    await expect(page.getByTestId('eligibility-rule-form-error')).toContainText(
      '建立資格條件規則前，請先選擇目前操作帳號。'
    )

    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)
    await page.getByTestId('eligibility-rule-submit').click()

    await expect(page.getByTestId('eligibility-rule-form-error')).toContainText(
      'Request validation failed.'
    )
  })

  test('supports editing an eligibility rule from the frontend form', async ({ page }) => {
    const originalEligibilityRule = {
      ...eligibilityRuleDetail
    }
    const updatedEligibilityRule = {
      ...eligibilityRuleDetail,
      os_version_max: '18.4',
      install_channel: 'manual-invite',
      is_active: false
    }

    let detailResponse = originalEligibilityRule
    let updateRequestBody: unknown = null
    let updateRequestActorId: string | undefined

    await mockAccounts(page)
    await page.route(/\/api\/v1\/eligibility-rules\/er_123$/, async (route) => {
      const method = route.request().method()

      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(detailResponse)
        })
        return
      }

      if (method === 'PATCH') {
        updateRequestActorId = route.request().headers()['x-actor-id']
        updateRequestBody = JSON.parse(route.request().postData() ?? '{}')
        detailResponse = updatedEligibilityRule
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(updatedEligibilityRule)
        })
        return
      }

      await route.fallback()
    })

    await page.goto('/campaigns/camp_123/eligibility-rules/er_123')
    await page.getByTestId('eligibility-rule-edit-link').click()

    await expect(page).toHaveURL(/\/campaigns\/camp_123\/eligibility-rules\/er_123\/edit$/)
    await expect(page.getByTestId('eligibility-rule-edit-panel')).toBeVisible()
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)

    await page.getByTestId('eligibility-rule-os-version-max-input').fill('18.4')
    await page
      .getByTestId('eligibility-rule-install-channel-input')
      .fill('manual-invite')
    await page.getByTestId('eligibility-rule-is-active-input').uncheck()
    await page.getByTestId('eligibility-rule-submit').click()

    expect(updateRequestActorId).toBe(developerAccount.id)
    expect(updateRequestBody).toEqual({
      os_version_max: '18.4',
      install_channel: 'manual-invite',
      is_active: false
    })

    await expect(page).toHaveURL(/\/campaigns\/camp_123\/eligibility-rules\/er_123$/)
    await expect(page.getByTestId('eligibility-rule-detail-panel')).toContainText('18.4')
    await expect(page.getByTestId('eligibility-rule-detail-panel')).toContainText(
      'manual-invite'
    )
  })

  test('shows ownership mismatch errors when editing an eligibility rule outside the actor scope', async ({
    page
  }) => {
    await mockAccounts(page)
    await page.route(/\/api\/v1\/eligibility-rules\/er_123$/, async (route) => {
      const method = route.request().method()

      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(eligibilityRuleDetail)
        })
        return
      }

      if (method === 'PATCH') {
        await route.fulfill({
          status: 409,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 'ownership_mismatch',
            message: 'Current actor does not own the target resource.',
            details: {
              actor_id: developerAccount.id,
              resource: 'eligibility_rule',
              ownership_anchor: {
                resource: 'project',
                id: 'proj_other',
                owner_account_id: 'acct_other_123'
              }
            }
          })
        })
        return
      }

      await route.fallback()
    })

    await page.goto('/campaigns/camp_123/eligibility-rules/er_123/edit')
    await expect(page.getByTestId('eligibility-rule-edit-panel')).toBeVisible()
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)
    await page.getByTestId('eligibility-rule-os-version-max-input').fill('18.4')
    await page.getByTestId('eligibility-rule-submit').click()

    await expect(page.getByTestId('eligibility-rule-form-error')).toContainText(
      '你不能操作不屬於自己的資源。'
    )
  })

  test('renders the eligibility rule edit error state when the record cannot be loaded', async ({
    page
  }) => {
    await mockApiError(
      page,
      '/eligibility-rules/er_missing',
      {
        code: 'resource_not_found',
        message: 'Eligibility rule not found.',
        details: {
          resource: 'eligibility_rule',
          id: 'er_missing'
        }
      },
      {
        status: 404
      }
    )

    await page.goto('/campaigns/camp_123/eligibility-rules/er_missing/edit')

    const errorState = page.getByTestId('eligibility-rule-edit-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Eligibility rule not found.')
  })

  test('renders the campaign eligibility empty state when the API returns no items', async ({
    page
  }) => {
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiError(
      page,
      '/campaigns/camp_123/safety',
      {
        code: 'resource_not_found',
        message: 'Campaign safety not found.',
        details: {
          resource: 'campaign_safety',
          campaign_id: 'camp_123'
        }
      },
      {
        status: 404
      }
    )
    await mockApiJson(page, '/campaigns/camp_123/eligibility-rules', {
      items: [],
      total: 0
    })
    await mockApiJson(page, '/tasks?campaign_id=camp_123', {
      items: [],
      total: 0
    })

    await page.goto('/campaigns/camp_123')

    await expect(page.getByTestId('campaign-eligibility-empty')).toBeVisible()
    await expect(page.getByTestId('campaign-eligibility-list')).toHaveCount(0)
  })

  test('renders the campaign eligibility error state when the nested request fails', async ({
    page
  }) => {
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiError(
      page,
      '/campaigns/camp_123/safety',
      {
        code: 'resource_not_found',
        message: 'Campaign safety not found.',
        details: {
          resource: 'campaign_safety',
          campaign_id: 'camp_123'
        }
      },
      {
        status: 404
      }
    )
    await mockApiError(
      page,
      '/campaigns/camp_123/eligibility-rules',
      {
        code: 'internal_error',
        message: 'Eligibility rules unavailable.',
        details: null
      },
      {
        status: 500
      }
    )
    await mockApiJson(page, '/tasks?campaign_id=camp_123', {
      items: [],
      total: 0
    })

    await page.goto('/campaigns/camp_123')

    const errorState = page.getByTestId('campaign-eligibility-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Eligibility rules unavailable.')
  })
})
