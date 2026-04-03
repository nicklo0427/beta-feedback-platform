import { expect, test } from '@playwright/test'

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

test.describe('eligibility shell flows', () => {
  test('renders campaign eligibility list and navigates to the rule detail page', async ({
    page
  }) => {
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiJson(page, '/campaigns/camp_123/eligibility-rules', {
      items: [eligibilityRuleListItem],
      total: 1
    })
    await mockApiJson(page, '/eligibility-rules/er_123', eligibilityRuleDetail)

    await page.goto('/campaigns/camp_123')

    const eligibilityList = page.getByTestId('campaign-eligibility-list')
    await expect(eligibilityList).toBeVisible()

    const eligibilityCard = page.getByTestId('eligibility-rule-card-er_123')
    await expect(eligibilityCard).toBeVisible()
    await expect(eligibilityCard).toContainText(eligibilityRuleListItem.platform)
    await expect(eligibilityCard).toContainText(eligibilityRuleListItem.install_channel)

    await eligibilityCard.click()

    await expect(page).toHaveURL(/\/campaigns\/camp_123\/eligibility-rules\/er_123$/)

    const detailPanel = page.getByTestId('eligibility-rule-detail-panel')
    await expect(detailPanel).toBeVisible()
    await expect(detailPanel).toContainText(eligibilityRuleDetail.platform)
    await expect(detailPanel).toContainText(eligibilityRuleDetail.os_version_min)
    await expect(detailPanel).toContainText(eligibilityRuleDetail.os_version_max)
  })

  test('renders the campaign eligibility empty state when the API returns no items', async ({
    page
  }) => {
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiJson(page, '/campaigns/camp_123/eligibility-rules', {
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

    await page.goto('/campaigns/camp_123')

    const errorState = page.getByTestId('campaign-eligibility-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Eligibility rules unavailable.')
  })
})
