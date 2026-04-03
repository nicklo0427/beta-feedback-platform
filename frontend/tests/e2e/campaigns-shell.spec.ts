import { expect, test } from '@playwright/test'

import { formatPlatformLabel } from '~/features/platform-display'

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
    await expect(safetyPanel).toContainText(campaignSafety.risk_level)
    await expect(safetyPanel).toContainText(campaignSafety.review_status)

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
    await expect(tasksList).toContainText(taskListItem.status)

    await detailPanel.getByRole('link', { name: campaignDetail.project_id }).click()

    await expect(page).toHaveURL(/\/projects\/proj_123$/)
    await expect(page.getByTestId('project-detail-panel')).toBeVisible()
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

  test('renders the campaign safety error state when the safety request fails', async ({
    page
  }) => {
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

  test('renders the campaign reputation error state when the summary request fails', async ({
    page
  }) => {
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
