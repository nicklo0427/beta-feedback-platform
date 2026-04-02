import { expect, test } from '@playwright/test'

import { mockApiError, mockApiJson } from './support/api-mocks'

const projectListItem = {
  id: 'proj_123',
  name: 'HabitQuest',
  description: 'Cross-platform habit tracking app beta program.',
  updated_at: '2026-04-03T10:00:00Z'
}

const projectDetail = {
  id: 'proj_123',
  name: 'HabitQuest',
  description: 'Cross-platform habit tracking app beta program.',
  created_at: '2026-04-01T09:00:00Z',
  updated_at: '2026-04-03T10:00:00Z'
}

const relatedCampaign = {
  id: 'camp_123',
  project_id: 'proj_123',
  name: 'Closed Beta Round 1',
  target_platforms: ['ios', 'android'],
  version_label: '0.9.0-beta.1',
  status: 'active',
  updated_at: '2026-04-03T10:00:00Z'
}

test.describe('projects shell flows', () => {
  test('navigates from home to projects list and project detail with related campaigns', async ({
    page
  }) => {
    await mockApiJson(page, '/projects', {
      items: [projectListItem],
      total: 1
    })
    await mockApiJson(page, '/projects/proj_123', projectDetail)
    await mockApiJson(page, '/campaigns?project_id=proj_123', {
      items: [relatedCampaign],
      total: 1
    })

    await page.goto('/')
    await page.getByTestId('home-projects-link').click()

    await expect(page).toHaveURL(/\/projects$/)
    await expect(page.getByTestId('projects-list')).toBeVisible()

    const projectCard = page.getByTestId('project-card-proj_123')
    await expect(projectCard).toBeVisible()
    await expect(projectCard).toContainText(projectListItem.name)
    await expect(projectCard).toContainText(projectListItem.updated_at)

    await projectCard.click()

    await expect(page).toHaveURL(/\/projects\/proj_123$/)

    const detailPanel = page.getByTestId('project-detail-panel')
    await expect(detailPanel).toBeVisible()
    await expect(detailPanel).toContainText(projectDetail.name)
    await expect(detailPanel).toContainText(projectDetail.id)
    await expect(detailPanel).toContainText(projectDetail.created_at)

    const relatedCampaignsList = page.getByTestId('project-campaigns-list')
    await expect(relatedCampaignsList).toBeVisible()

    const relatedCampaignCard = page.getByTestId('project-campaign-card-camp_123')
    await expect(relatedCampaignCard).toBeVisible()
    await expect(relatedCampaignCard).toContainText(relatedCampaign.name)
    await expect(relatedCampaignCard).toContainText(relatedCampaign.status)
  })

  test('renders the projects empty state when the API returns no items', async ({
    page
  }) => {
    await mockApiJson(page, '/projects', {
      items: [],
      total: 0
    })

    await page.goto('/projects')

    await expect(page.getByTestId('projects-empty')).toBeVisible()
    await expect(page.getByTestId('projects-list')).toHaveCount(0)
  })

  test('renders the project detail error state when the detail request fails', async ({
    page
  }) => {
    await mockApiError(
      page,
      '/projects/proj_missing',
      {
        code: 'resource_not_found',
        message: 'Project not found.',
        details: {
          resource: 'project',
          id: 'proj_missing'
        }
      },
      {
        status: 404
      }
    )
    await mockApiJson(page, '/campaigns?project_id=proj_missing', {
      items: [],
      total: 0
    })

    await page.goto('/projects/proj_missing')

    const errorState = page.getByTestId('project-detail-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Project not found.')
    await expect(page.getByTestId('project-detail-panel')).toHaveCount(0)
  })
})
