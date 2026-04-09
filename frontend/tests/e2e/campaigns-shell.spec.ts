import { expect, test, type Page } from '@playwright/test'

import { formatCampaignStatusLabel } from '~/features/campaigns/types'
import {
  formatQualificationStatusLabel,
  type CampaignQualificationResultItem
} from '~/features/eligibility/types'
import { formatPlatformLabel } from '~/features/platform-display'
import {
  type DistributionChannel,
  formatDistributionChannelLabel,
  type ReviewStatus,
  formatReviewStatusLabel,
  formatRiskLevelLabel,
  type RiskLevel
} from '~/features/safety/types'
import { formatTaskStatusLabel, type TaskStatus } from '~/features/tasks/types'

import { mockApiError, mockApiJson } from './support/api-mocks'

const campaignListItem = {
  id: 'camp_123',
  project_id: 'proj_123',
  name: 'Closed Beta Round 1',
  target_platforms: ['ios', 'android'],
  version_label: '0.9.0-beta.1',
  status: 'active',
  updated_at: '2026-04-03T10:00:00Z'
}

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

const campaignSafety = {
  id: 'safe_123',
  campaign_id: 'camp_123',
  distribution_channel: 'testflight',
  source_label: 'TestFlight',
  source_url: 'https://testflight.apple.com/join/example',
  risk_level: 'low',
  review_status: 'approved',
  official_channel_only: true,
  risk_note: 'Install only from the official invite link.',
  created_at: '2026-04-02T09:00:00Z',
  updated_at: '2026-04-03T10:00:00Z'
}

const campaignReputation = {
  campaign_id: 'camp_123',
  tasks_total_count: 4,
  tasks_closed_count: 2,
  feedback_received_count: 3,
  closure_rate: 0.5,
  last_feedback_at: '2026-04-03T11:31:00Z',
  updated_at: '2026-04-03T11:31:00Z'
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

const taskListItem = {
  id: 'task_123',
  campaign_id: 'camp_123',
  device_profile_id: 'dp_123',
  title: 'Validate onboarding flow',
  status: 'assigned',
  updated_at: '2026-04-03T10:00:00Z'
}

const projectDetail = {
  id: 'proj_123',
  name: 'HabitQuest',
  description: 'Cross-platform habit tracking app beta program.',
  created_at: '2026-04-01T09:00:00Z',
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

const qualificationMatchResult = {
  device_profile_id: 'dp_123',
  device_profile_name: 'iPhone 15 Pro',
  qualification_status: 'qualified',
  matched_rule_id: 'er_123',
  reason_codes: [],
  reason_summary: '符合目前活動的資格條件。'
} satisfies CampaignQualificationResultItem

const qualificationFailResult = {
  device_profile_id: 'dp_456',
  device_profile_name: 'Android Pixel',
  qualification_status: 'not_qualified',
  matched_rule_id: null,
  reason_codes: ['platform_mismatch', 'os_name_mismatch'],
  reason_summary: '主要未符合條件：平台不符合目前活動條件；作業系統不符合目前活動條件。'
} satisfies CampaignQualificationResultItem

async function mockAccounts(page: Page): Promise<void> {
  await mockApiJson(page, '/accounts', {
    items: [developerAccount, testerAccount],
    total: 2
  })
}

test.describe('campaigns shell flows', () => {
  test('navigates from home to campaigns list and campaign detail, then links back to project detail', async ({
    page
  }) => {
    await mockApiJson(page, '/campaigns', {
      items: [campaignListItem],
      total: 1
    })
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiJson(page, '/projects/proj_123', projectDetail)
    await mockApiJson(page, '/campaigns?project_id=proj_123', {
      items: [campaignListItem],
      total: 1
    })
    await mockApiJson(page, '/campaigns/camp_123/safety', campaignSafety)
    await mockApiJson(page, '/campaigns/camp_123/reputation', campaignReputation)
    await mockApiJson(page, '/campaigns/camp_123/eligibility-rules', {
      items: [eligibilityRuleListItem],
      total: 1
    })
    await mockApiJson(page, '/tasks?campaign_id=camp_123', {
      items: [taskListItem],
      total: 1
    })

    await page.goto('/')
    await page.getByTestId('home-campaigns-link').click()

    await expect(page).toHaveURL(/\/campaigns$/)
    await expect(page.getByTestId('campaigns-list')).toBeVisible()

    const campaignCard = page.getByTestId('campaign-card-camp_123')
    await expect(campaignCard).toBeVisible()
    await expect(campaignCard).toContainText(campaignListItem.name)
    await expect(campaignCard).toContainText(campaignListItem.project_id)

    await campaignCard.click()

    await expect(page).toHaveURL(/\/campaigns\/camp_123$/)

    const detailPanel = page.getByTestId('campaign-detail-panel')
    await expect(detailPanel).toBeVisible()
    await expect(detailPanel).toContainText(campaignDetail.name)
    await expect(detailPanel).toContainText(campaignDetail.id)
    await expect(detailPanel).toContainText(campaignDetail.version_label)

    const safetyPanel = page.getByTestId('campaign-safety-panel')
    await expect(safetyPanel).toBeVisible()
    await expect(safetyPanel).toContainText(campaignSafety.source_label)
    await expect(safetyPanel).toContainText(
      formatRiskLevelLabel(campaignSafety.risk_level as RiskLevel)
    )
    await expect(safetyPanel).toContainText(
      formatReviewStatusLabel(campaignSafety.review_status as ReviewStatus)
    )

    const reputationPanel = page.getByTestId('campaign-reputation-panel')
    await expect(reputationPanel).toBeVisible()
    await expect(reputationPanel).toContainText('0.50')
    await expect(reputationPanel).toContainText('4')
    await expect(reputationPanel).toContainText(campaignReputation.last_feedback_at)

    const eligibilityList = page.getByTestId('campaign-eligibility-list')
    await expect(eligibilityList).toBeVisible()
    await expect(eligibilityList).toContainText(
      formatPlatformLabel(eligibilityRuleListItem.platform)
    )

    const tasksList = page.getByTestId('campaign-tasks-list')
    await expect(tasksList).toBeVisible()
    await expect(tasksList).toContainText(taskListItem.title)
    await expect(tasksList).toContainText(formatTaskStatusLabel(taskListItem.status as TaskStatus))

    await detailPanel.getByRole('link', { name: campaignDetail.project_id }).click()

    await expect(page).toHaveURL(/\/projects\/proj_123$/)
    await expect(page.getByTestId('project-detail-panel')).toBeVisible()
  })

  test('shows current tester qualification results on campaign detail', async ({
    page
  }) => {
    let qualificationRequestActorId: string | undefined
    let resolveQualificationRequestActorId: ((value: string | undefined) => void) | null = null
    const qualificationRequestActorIdPromise = new Promise<string | undefined>((resolve) => {
      resolveQualificationRequestActorId = resolve
    })

    await mockAccounts(page)
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiJson(page, '/campaigns/camp_123/safety', campaignSafety)
    await mockApiJson(page, '/campaigns/camp_123/reputation', campaignReputation)
    await mockApiJson(page, '/campaigns/camp_123/eligibility-rules', {
      items: [eligibilityRuleListItem],
      total: 1
    })
    await mockApiJson(page, '/tasks?campaign_id=camp_123', {
      items: [taskListItem],
      total: 1
    })
    await page.route(
      /\/api\/v1\/campaigns\/camp_123\/qualification-results\?mine=true$/,
      async (route) => {
        qualificationRequestActorId = route.request().headers()['x-actor-id']
        resolveQualificationRequestActorId?.(qualificationRequestActorId)
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [qualificationMatchResult, qualificationFailResult],
            total: 2
          })
        })
      }
    )

    await page.goto('/campaigns/camp_123')

    await expect(page.getByTestId('campaign-qualification-select-actor')).toBeVisible()
    await page.getByTestId('current-actor-select').selectOption(testerAccount.id)

    expect(await qualificationRequestActorIdPromise).toBe(testerAccount.id)

    const qualificationList = page.getByTestId('campaign-qualification-list')
    await expect(qualificationList).toBeVisible()

    const matchCard = page.getByTestId(
      `campaign-qualification-result-${qualificationMatchResult.device_profile_id}`
    )
    await expect(matchCard).toContainText(qualificationMatchResult.device_profile_name)
    await expect(matchCard).toContainText(
      formatQualificationStatusLabel(qualificationMatchResult.qualification_status)
    )
    await expect(matchCard).toContainText(qualificationMatchResult.matched_rule_id!)

    const failCard = page.getByTestId(
      `campaign-qualification-result-${qualificationFailResult.device_profile_id}`
    )
    await expect(failCard).toContainText(qualificationFailResult.device_profile_name)
    await expect(failCard).toContainText(
      formatQualificationStatusLabel(qualificationFailResult.qualification_status)
    )
    await expect(failCard).toContainText(qualificationFailResult.reason_summary)
  })

  test('shows qualification empty state when current tester has no owned device profiles', async ({
    page
  }) => {
    await mockAccounts(page)
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiJson(page, '/campaigns/camp_123/safety', campaignSafety)
    await mockApiJson(page, '/campaigns/camp_123/reputation', campaignReputation)
    await mockApiJson(page, '/campaigns/camp_123/eligibility-rules', {
      items: [eligibilityRuleListItem],
      total: 1
    })
    await mockApiJson(page, '/tasks?campaign_id=camp_123', {
      items: [taskListItem],
      total: 1
    })
    await mockApiJson(page, '/campaigns/camp_123/qualification-results?mine=true', {
      items: [],
      total: 0
    })

    await page.goto('/campaigns/camp_123')
    await page.getByTestId('current-actor-select').selectOption(testerAccount.id)

    const emptyState = page.getByTestId('campaign-qualification-empty')
    await expect(emptyState).toBeVisible()
    await expect(emptyState).toContainText('目前沒有可檢查的裝置設定檔')
  })

  test('shows qualification role mismatch when current actor is not a tester', async ({
    page
  }) => {
    await mockAccounts(page)
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiJson(page, '/campaigns/camp_123/safety', campaignSafety)
    await mockApiJson(page, '/campaigns/camp_123/reputation', campaignReputation)
    await mockApiJson(page, '/campaigns/camp_123/eligibility-rules', {
      items: [eligibilityRuleListItem],
      total: 1
    })
    await mockApiJson(page, '/tasks?campaign_id=camp_123', {
      items: [taskListItem],
      total: 1
    })

    await page.goto('/campaigns/camp_123')
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)

    const roleMismatch = page.getByTestId('campaign-qualification-role-mismatch')
    await expect(roleMismatch).toBeVisible()
    await expect(roleMismatch).toContainText('資格檢查需要測試者帳號')
    await expect(roleMismatch).toContainText('開發者')
  })

  test('supports creating a campaign from the project context', async ({ page }) => {
    const createdCampaign = {
      id: 'camp_456',
      project_id: 'proj_123',
      name: 'Closed Beta Round 2',
      description: 'Validate pricing copy on the Mobile Web beta experience.',
      target_platforms: ['h5', 'ios'],
      version_label: '0.9.1-beta.2',
      status: 'draft',
      created_at: '2026-04-03T12:00:00Z',
      updated_at: '2026-04-03T12:00:00Z'
    }

    let createRequestBody: unknown = null
    let createRequestActorId: string | undefined

    await mockAccounts(page)
    await mockApiJson(page, '/projects/proj_123', projectDetail)
    await mockApiJson(page, '/campaigns?project_id=proj_123', {
      items: [],
      total: 0
    })
    await page.route(/\/api\/v1\/campaigns$/, async (route) => {
      const method = route.request().method()

      if (method !== 'POST') {
        await route.fallback()
        return
      }

      createRequestActorId = route.request().headers()['x-actor-id']
      createRequestBody = JSON.parse(route.request().postData() ?? '{}')
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(createdCampaign)
      })
    })
    await mockApiJson(page, '/campaigns/camp_456', createdCampaign)
    await mockApiError(
      page,
      '/campaigns/camp_456/safety',
      {
        code: 'resource_not_found',
        message: 'Campaign safety not found.',
        details: {
          resource: 'campaign_safety',
          campaign_id: 'camp_456'
        }
      },
      {
        status: 404
      }
    )
    await mockApiJson(page, '/campaigns/camp_456/reputation', {
      campaign_id: 'camp_456',
      tasks_total_count: 0,
      tasks_closed_count: 0,
      feedback_received_count: 0,
      closure_rate: 0,
      last_feedback_at: null,
      updated_at: '2026-04-03T12:00:00Z'
    })
    await mockApiJson(page, '/campaigns/camp_456/eligibility-rules', {
      items: [],
      total: 0
    })
    await mockApiJson(page, '/tasks?campaign_id=camp_456', {
      items: [],
      total: 0
    })

    await page.goto('/projects/proj_123')
    await page.getByTestId('campaign-create-link').click()

    await expect(page).toHaveURL(/\/projects\/proj_123\/campaigns\/new$/)
    await expect(page.getByTestId('campaign-form')).toBeVisible()
    await expect(page.getByTestId('campaign-status-default-note')).toContainText(
      '草稿'
    )

    await page.getByTestId('campaign-name-input').fill('Closed Beta Round 2')
    await page
      .getByTestId('campaign-description-input')
      .fill('Validate pricing copy on the Mobile Web beta experience.')
    await page.getByTestId('campaign-version-label-input').fill('0.9.1-beta.2')
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)
    await page.getByTestId('campaign-platform-checkbox-h5').check()
    await page.getByTestId('campaign-platform-checkbox-ios').check()
    await page.getByTestId('campaign-submit').click()

    expect(createRequestActorId).toBe(developerAccount.id)
    expect(createRequestBody).toEqual({
      project_id: 'proj_123',
      name: 'Closed Beta Round 2',
      description: 'Validate pricing copy on the Mobile Web beta experience.',
      target_platforms: ['h5', 'ios'],
      version_label: '0.9.1-beta.2'
    })

    await expect(page).toHaveURL(/\/campaigns\/camp_456$/)
    await expect(page.getByTestId('campaign-detail-panel')).toContainText(
      createdCampaign.name
    )
    await expect(page.getByTestId('campaign-detail-panel')).toContainText('行動網頁')
  })

  test('shows campaign create validation and backend errors', async ({ page }) => {
    await mockAccounts(page)
    await mockApiJson(page, '/projects/proj_123', projectDetail)
    await page.route(/\/api\/v1\/campaigns$/, async (route) => {
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
                field: 'target_platforms',
                message: 'Select at least one platform.'
              }
            ]
          }
        })
      })
    })

    await page.goto('/projects/proj_123/campaigns/new')
    await expect(page.getByTestId('campaign-form')).toBeVisible()
    await page.getByTestId('campaign-submit').click()

    await expect(page.getByTestId('campaign-form-error')).toContainText(
      '名稱為必填。'
    )

    await page.getByTestId('campaign-name-input').fill('Closed Beta Round 2')
    await page.getByTestId('campaign-platform-checkbox-ios').check()
    await page.getByTestId('campaign-submit').click()

    await expect(page.getByTestId('campaign-form-error')).toContainText(
      '建立活動前，請先選擇目前操作帳號。'
    )

    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)
    await page.getByTestId('campaign-submit').click()

    await expect(page.getByTestId('campaign-form-error')).toContainText(
      'Request validation failed.'
    )
  })

  test('supports editing a campaign from the frontend form', async ({ page }) => {
    const originalCampaign = {
      ...campaignDetail
    }
    const updatedCampaign = {
      ...campaignDetail,
      description: 'Updated campaign summary for the Mobile Web rollout.',
      target_platforms: ['h5', 'ios', 'android'],
      version_label: '0.9.1-beta.2',
      status: 'closed'
    }

    let detailResponse = originalCampaign
    let updateRequestBody: unknown = null
    let updateRequestActorId: string | undefined

    await mockAccounts(page)
    await page.route(/\/api\/v1\/campaigns\/camp_123$/, async (route) => {
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
        detailResponse = updatedCampaign
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(updatedCampaign)
        })
        return
      }

      await route.fallback()
    })
    await mockApiJson(page, '/campaigns/camp_123/safety', campaignSafety)
    await mockApiJson(page, '/campaigns/camp_123/reputation', campaignReputation)
    await mockApiJson(page, '/campaigns/camp_123/eligibility-rules', {
      items: [eligibilityRuleListItem],
      total: 1
    })
    await mockApiJson(page, '/tasks?campaign_id=camp_123', {
      items: [taskListItem],
      total: 1
    })

    await page.goto('/campaigns/camp_123')
    await page.getByTestId('campaign-edit-link').click()

    await expect(page).toHaveURL(/\/campaigns\/camp_123\/edit$/)
    await expect(page.getByTestId('campaign-edit-panel')).toBeVisible()
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)

    await page
      .getByTestId('campaign-description-input')
      .fill('Updated campaign summary for the Mobile Web rollout.')
    await page.getByTestId('campaign-platform-checkbox-h5').check()
    await page.getByTestId('campaign-version-label-input').fill('0.9.1-beta.2')
    await page.getByTestId('campaign-status-field').selectOption('closed')
    await page.getByTestId('campaign-submit').click()

    expect(updateRequestActorId).toBe(developerAccount.id)
    expect(updateRequestBody).toEqual({
      description: 'Updated campaign summary for the Mobile Web rollout.',
      target_platforms: ['h5', 'ios', 'android'],
      version_label: '0.9.1-beta.2',
      status: 'closed'
    })

    await expect(page).toHaveURL(/\/campaigns\/camp_123$/)
    await expect(page.getByTestId('campaign-detail-panel')).toContainText(
      updatedCampaign.description
    )
    await expect(page.getByTestId('campaign-detail-panel')).toContainText('Mobile Web')
    await expect(page.getByTestId('campaign-detail-panel')).toContainText(
      formatCampaignStatusLabel('closed')
    )
  })

  test('renders the campaign edit error state when the record cannot be loaded', async ({
    page
  }) => {
    await mockAccounts(page)
    await mockApiError(
      page,
      '/campaigns/camp_missing',
      {
        code: 'resource_not_found',
        message: 'Campaign not found.',
        details: {
          resource: 'campaign',
          id: 'camp_missing'
        }
      },
      {
        status: 404
      }
    )

    await page.goto('/campaigns/camp_missing/edit')

    const errorState = page.getByTestId('campaign-edit-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Campaign not found.')
  })

  test('renders the campaigns empty state when the API returns no items', async ({
    page
  }) => {
    await mockApiJson(page, '/campaigns', {
      items: [],
      total: 0
    })

    await page.goto('/campaigns')

    await expect(page.getByTestId('campaigns-empty')).toBeVisible()
    await expect(page.getByTestId('campaigns-list')).toHaveCount(0)
  })

  test('renders the campaign detail error state when the detail request fails', async ({
    page
  }) => {
    await mockAccounts(page)
    await mockApiError(
      page,
      '/campaigns/camp_missing',
      {
        code: 'resource_not_found',
        message: 'Campaign not found.',
        details: {
          resource: 'campaign',
          id: 'camp_missing'
        }
      },
      {
        status: 404
      }
    )

    await page.goto('/campaigns/camp_missing')

    const errorState = page.getByTestId('campaign-detail-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Campaign not found.')
    await expect(page.getByTestId('campaign-detail-panel')).toHaveCount(0)
  })

  test('renders the campaign safety empty state when no safety profile exists', async ({
    page
  }) => {
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
    await mockApiJson(page, '/campaigns/camp_123/reputation', {
      campaign_id: 'camp_123',
      tasks_total_count: 0,
      tasks_closed_count: 0,
      feedback_received_count: 0,
      closure_rate: 0,
      last_feedback_at: null,
      updated_at: '2026-04-03T10:00:00Z'
    })
    await mockApiJson(page, '/campaigns/camp_123/eligibility-rules', {
      items: [],
      total: 0
    })
    await mockApiJson(page, '/tasks?campaign_id=camp_123', {
      items: [],
      total: 0
    })

    await page.goto('/campaigns/camp_123')

    await expect(page.getByTestId('campaign-safety-empty')).toBeVisible()
    await expect(page.getByTestId('campaign-safety-panel')).toHaveCount(0)
    await expect(page.getByTestId('campaign-reputation-zero')).toBeVisible()
  })

  test('supports creating a campaign safety profile from the campaign detail empty state', async ({
    page
  }) => {
    const createdSafety = {
      ...campaignSafety,
      distribution_channel: 'google_play_testing',
      source_label: 'Google Play Internal Testing',
      source_url:
        'https://play.google.com/apps/testing/com.example.closed-beta',
      risk_level: 'medium',
      review_status: 'approved',
      official_channel_only: false,
      risk_note: 'Share only with invited testers.'
    }

    let currentSafety: typeof createdSafety | null = null
    let createRequestBody: unknown = null
    let createRequestActorId: string | undefined

    await mockAccounts(page)
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiJson(page, '/campaigns/camp_123/reputation', campaignReputation)
    await mockApiJson(page, '/campaigns/camp_123/eligibility-rules', {
      items: [],
      total: 0
    })
    await mockApiJson(page, '/tasks?campaign_id=camp_123', {
      items: [],
      total: 0
    })
    await page.route(/\/api\/v1\/campaigns\/camp_123\/safety$/, async (route) => {
      const method = route.request().method()

      if (method === 'GET') {
        if (currentSafety) {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(currentSafety)
          })
          return
        }

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
        return
      }

      if (method === 'POST') {
        createRequestActorId = route.request().headers()['x-actor-id']
        createRequestBody = JSON.parse(route.request().postData() ?? '{}')
        currentSafety = createdSafety
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify(createdSafety)
        })
        return
      }

      await route.fallback()
    })

    await page.goto('/campaigns/camp_123')

    await expect(page.getByTestId('campaign-safety-empty')).toBeVisible()
    await page.getByTestId('campaign-safety-create-link').click()

    await expect(page).toHaveURL(/\/campaigns\/camp_123\/safety\/new$/)
    await expect(page.getByTestId('campaign-safety-create-panel')).toBeVisible()

    await page
      .getByTestId('campaign-safety-distribution-channel-field')
      .selectOption('google_play_testing')
    await page
      .getByTestId('campaign-safety-source-label-input')
      .fill('Google Play Internal Testing')
    await page
      .getByTestId('campaign-safety-source-url-input')
      .fill('https://play.google.com/apps/testing/com.example.closed-beta')
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)
    await page.getByTestId('campaign-safety-risk-level-field').selectOption('medium')
    await page.getByTestId('campaign-safety-review-status-field').selectOption('approved')
    await page.getByTestId('campaign-safety-risk-note-input').fill(
      'Share only with invited testers.'
    )
    await page.getByTestId('campaign-safety-submit').click()

    expect(createRequestActorId).toBe(developerAccount.id)
    expect(createRequestBody).toEqual({
      distribution_channel: 'google_play_testing',
      source_label: 'Google Play Internal Testing',
      source_url: 'https://play.google.com/apps/testing/com.example.closed-beta',
      risk_level: 'medium',
      review_status: 'approved',
      official_channel_only: false,
      risk_note: 'Share only with invited testers.'
    })

    await expect(page).toHaveURL(/\/campaigns\/camp_123$/)
    const safetyPanel = page.getByTestId('campaign-safety-panel')
    await expect(safetyPanel).toContainText(createdSafety.source_label)
    await expect(safetyPanel).toContainText(
      formatDistributionChannelLabel(createdSafety.distribution_channel as DistributionChannel)
    )
    await expect(safetyPanel).toContainText(
      formatRiskLevelLabel(createdSafety.risk_level as RiskLevel)
    )
  })

  test('shows campaign safety create conflict errors without leaving the form', async ({
    page
  }) => {
    await mockAccounts(page)
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await page.route(/\/api\/v1\/campaigns\/camp_123\/safety$/, async (route) => {
      const method = route.request().method()

      if (method === 'POST') {
        await route.fulfill({
          status: 409,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 'conflict',
            message: 'Campaign safety already exists.',
            details: {
              resource: 'campaign_safety',
              campaign_id: 'camp_123'
            }
          })
        })
        return
      }

      await route.fallback()
    })

    await page.goto('/campaigns/camp_123/safety/new')
    await expect(page.getByTestId('campaign-safety-form')).toBeVisible()
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)

    await page
      .getByTestId('campaign-safety-distribution-channel-field')
      .selectOption('testflight')
    await page.getByTestId('campaign-safety-source-label-input').fill('TestFlight')
    await page.getByTestId('campaign-safety-risk-level-field').selectOption('low')
    await page.getByTestId('campaign-safety-submit').click()

    await expect(page.getByTestId('campaign-safety-form-error')).toContainText(
      'Campaign safety already exists.'
    )
    await expect(page).toHaveURL(/\/campaigns\/camp_123\/safety\/new$/)
  })

  test('shows role mismatch errors when a tester tries to create campaign safety', async ({
    page
  }) => {
    await mockAccounts(page)
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await page.route(/\/api\/v1\/campaigns\/camp_123\/safety$/, async (route) => {
      if (route.request().method() !== 'POST') {
        await route.fallback()
        return
      }

      await route.fulfill({
        status: 409,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 'forbidden_actor_role',
          message: 'Developer role is required for this operation.',
          details: {
            actor_id: testerAccount.id,
            actor_role: 'tester',
            required_role: 'developer'
          }
        })
      })
    })

    await page.goto('/campaigns/camp_123/safety/new')
    await expect(page.getByTestId('campaign-safety-form')).toBeVisible()
    await page.getByTestId('current-actor-select').selectOption(testerAccount.id)
    await page
      .getByTestId('campaign-safety-distribution-channel-field')
      .selectOption('testflight')
    await page.getByTestId('campaign-safety-source-label-input').fill('TestFlight')
    await page.getByTestId('campaign-safety-risk-level-field').selectOption('low')
    await page.getByTestId('campaign-safety-submit').click()

    await expect(page.getByTestId('campaign-safety-form-error')).toContainText(
      '目前操作帳號角色不符合這項操作。'
    )
  })

  test('renders the campaign safety error state when the safety request fails', async ({
    page
  }) => {
    await mockAccounts(page)
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiJson(page, '/campaigns/camp_123/reputation', campaignReputation)
    await mockApiError(
      page,
      '/campaigns/camp_123/safety',
      {
        code: 'internal_error',
        message: 'Campaign safety service unavailable.',
        details: null
      },
      {
        status: 500
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

    const errorState = page.getByTestId('campaign-safety-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Campaign safety service unavailable.')
    await expect(page.getByTestId('campaign-safety-panel')).toHaveCount(0)
  })

  test('supports editing a campaign safety profile from the frontend form', async ({
    page
  }) => {
    const updatedSafety = {
      ...campaignSafety,
      source_label: 'Official Web Beta Portal',
      distribution_channel: 'web_url',
      source_url: 'https://beta.example.com/download',
      risk_level: 'medium',
      review_status: 'rejected',
      official_channel_only: false,
      risk_note: 'Review again after updating the landing page copy.'
    }

    let currentSafety = {
      ...campaignSafety
    }
    let updateRequestBody: unknown = null
    let updateRequestActorId: string | undefined

    await mockAccounts(page)
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiJson(page, '/campaigns/camp_123/reputation', campaignReputation)
    await mockApiJson(page, '/campaigns/camp_123/eligibility-rules', {
      items: [],
      total: 0
    })
    await mockApiJson(page, '/tasks?campaign_id=camp_123', {
      items: [],
      total: 0
    })
    await page.route(/\/api\/v1\/campaigns\/camp_123\/safety$/, async (route) => {
      const method = route.request().method()

      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(currentSafety)
        })
        return
      }

      if (method === 'PATCH') {
        updateRequestActorId = route.request().headers()['x-actor-id']
        updateRequestBody = JSON.parse(route.request().postData() ?? '{}')
        currentSafety = updatedSafety
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(updatedSafety)
        })
        return
      }

      await route.fallback()
    })

    await page.goto('/campaigns/camp_123')
    await page.getByTestId('campaign-safety-edit-link').click()

    await expect(page).toHaveURL(/\/campaigns\/camp_123\/safety\/edit$/)
    await expect(page.getByTestId('campaign-safety-edit-panel')).toBeVisible()
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)

    await page
      .getByTestId('campaign-safety-distribution-channel-field')
      .selectOption('web_url')
    await page
      .getByTestId('campaign-safety-source-label-input')
      .fill('Official Web Beta Portal')
    await page
      .getByTestId('campaign-safety-source-url-input')
      .fill('https://beta.example.com/download')
    await page.getByTestId('campaign-safety-risk-level-field').selectOption('medium')
    await page.getByTestId('campaign-safety-review-status-field').selectOption('rejected')
    await page.getByTestId('campaign-safety-risk-note-input').fill(
      'Review again after updating the landing page copy.'
    )
    await page.getByTestId('campaign-safety-official-channel-only-input').uncheck()
    await page.getByTestId('campaign-safety-submit').click()

    expect(updateRequestActorId).toBe(developerAccount.id)
    expect(updateRequestBody).toEqual({
      distribution_channel: 'web_url',
      source_label: 'Official Web Beta Portal',
      source_url: 'https://beta.example.com/download',
      risk_level: 'medium',
      review_status: 'rejected',
      official_channel_only: false,
      risk_note: 'Review again after updating the landing page copy.'
    })

    await expect(page).toHaveURL(/\/campaigns\/camp_123$/)
    const safetyPanel = page.getByTestId('campaign-safety-panel')
    await expect(safetyPanel).toContainText(updatedSafety.source_label)
    await expect(safetyPanel).toContainText(
      formatDistributionChannelLabel(updatedSafety.distribution_channel as DistributionChannel)
    )
    await expect(safetyPanel).toContainText(
      formatReviewStatusLabel(updatedSafety.review_status as ReviewStatus)
    )
  })

  test('renders the campaign safety edit error state when the safety record cannot be loaded', async ({
    page
  }) => {
    await mockAccounts(page)
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

    await page.goto('/campaigns/camp_123/safety/edit')

    const errorState = page.getByTestId('campaign-safety-edit-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Campaign safety not found.')
  })

  test('renders the campaign reputation error state when the summary request fails', async ({
    page
  }) => {
    await mockAccounts(page)
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiJson(page, '/campaigns/camp_123/safety', campaignSafety)
    await mockApiError(
      page,
      '/campaigns/camp_123/reputation',
      {
        code: 'internal_error',
        message: 'Collaboration summary unavailable.',
        details: null
      },
      {
        status: 500
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

    const errorState = page.getByTestId('campaign-reputation-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Collaboration summary unavailable.')
    await expect(page.getByTestId('campaign-reputation-panel')).toHaveCount(0)
  })
})
