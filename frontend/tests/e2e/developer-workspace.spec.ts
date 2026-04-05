import { expect, test, type Page } from '@playwright/test'

import { formatCampaignStatusLabel, type CampaignStatus } from '~/features/campaigns/types'

import { mockApiJson } from './support/api-mocks'

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

const projectListItem = {
  id: 'proj_123',
  name: 'HabitQuest',
  description: 'Cross-platform habit tracking app beta program.',
  owner_account_id: developerAccount.id,
  updated_at: '2026-04-03T10:00:00Z'
}

const projectDetail = {
  id: 'proj_123',
  name: 'HabitQuest',
  description: 'Cross-platform habit tracking app beta program.',
  owner_account_id: developerAccount.id,
  created_at: '2026-04-01T09:00:00Z',
  updated_at: '2026-04-03T10:00:00Z'
}

const campaignListItem = {
  id: 'camp_123',
  project_id: 'proj_123',
  name: 'Closed Beta Round 1',
  target_platforms: ['ios', 'android'],
  version_label: '0.9.0-beta.1',
  status: 'active',
  updated_at: '2026-04-03T10:00:00Z'
}

async function mockAccounts(
  page: Page,
  accounts: Array<typeof developerAccount | typeof testerAccount>
): Promise<void> {
  await mockApiJson(page, '/accounts', {
    items: accounts,
    total: accounts.length
  })
}

test.describe('developer workspace flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.removeItem('beta-feedback-platform.current-actor-id')
    })
  })

  test('shows the my projects workspace for a developer and opens project detail', async ({
    page
  }) => {
    await mockAccounts(page, [developerAccount, testerAccount])
    await page.route(/\/api\/v1\/projects\?mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(developerAccount.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [projectListItem],
          total: 1
        })
      })
    })
    await mockApiJson(page, '/projects/proj_123', projectDetail)
    await mockApiJson(page, '/campaigns?project_id=proj_123', {
      items: [campaignListItem],
      total: 1
    })

    await page.goto('/my/projects')
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)

    await expect(page.getByTestId('my-projects-list')).toBeVisible()
    const projectCard = page.getByTestId('my-project-card-proj_123')
    await expect(projectCard).toContainText(projectListItem.name)
    await expect(projectCard).toContainText(projectListItem.owner_account_id)

    await page.getByTestId('my-project-detail-link-proj_123').click()
    await expect(page).toHaveURL(/\/projects\/proj_123$/)
    await expect(page.getByTestId('project-detail-panel')).toContainText(projectDetail.name)
  })

  test('shows the my projects empty state for a developer without owned projects', async ({
    page
  }) => {
    await mockAccounts(page, [developerAccount])
    await page.route(/\/api\/v1\/projects\?mine=true$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0
        })
      })
    })

    await page.goto('/my/projects')
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)

    await expect(page.getByTestId('my-projects-empty')).toBeVisible()
  })

  test('shows role mismatch when a tester opens the my projects workspace', async ({
    page
  }) => {
    await mockAccounts(page, [testerAccount])

    await page.goto('/my/projects')
    await page.getByTestId('current-actor-select').selectOption(testerAccount.id)

    await expect(page.getByTestId('my-projects-role-mismatch')).toBeVisible()
  })

  test('shows the my campaigns workspace for a developer and opens upstream project detail', async ({
    page
  }) => {
    await mockAccounts(page, [developerAccount])
    await page.route(/\/api\/v1\/campaigns\?mine=true$/, async (route) => {
      expect(route.request().headers()['x-actor-id']).toBe(developerAccount.id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [campaignListItem],
          total: 1
        })
      })
    })
    await mockApiJson(page, '/projects/proj_123', projectDetail)
    await mockApiJson(page, '/campaigns?project_id=proj_123', {
      items: [campaignListItem],
      total: 1
    })

    await page.goto('/my/campaigns')
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)

    await expect(page.getByTestId('my-campaigns-list')).toBeVisible()
    const campaignCard = page.getByTestId('my-campaign-card-camp_123')
    await expect(campaignCard).toContainText(campaignListItem.name)
    await expect(campaignCard).toContainText(
      formatCampaignStatusLabel(campaignListItem.status as CampaignStatus)
    )

    await page.getByTestId('my-campaign-project-link-camp_123').click()
    await expect(page).toHaveURL(/\/projects\/proj_123$/)
    await expect(page.getByTestId('project-detail-panel')).toContainText(projectDetail.name)
  })

  test('shows role mismatch when a tester opens the my campaigns workspace', async ({
    page
  }) => {
    await mockAccounts(page, [testerAccount])

    await page.goto('/my/campaigns')
    await page.getByTestId('current-actor-select').selectOption(testerAccount.id)

    await expect(page.getByTestId('my-campaigns-role-mismatch')).toBeVisible()
  })
})
