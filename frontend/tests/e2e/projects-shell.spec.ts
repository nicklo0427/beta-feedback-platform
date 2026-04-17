import { expect, test } from '@playwright/test'

import { formatCampaignStatusLabel, type CampaignStatus } from '~/features/campaigns/types'

import { mockApiError, mockApiJson } from './support/api-mocks'

const developerAccount = {
  id: 'acct_dev_123',
  display_name: 'Dev Lead',
  role: 'developer',
  updated_at: '2026-04-03T09:30:00Z'
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
  test('navigates from the projects list to project detail with related campaigns', async ({
    page
  }) => {
    await mockApiJson(page, '/accounts', {
      items: [developerAccount],
      total: 1
    })
    await mockApiJson(page, '/projects', {
      items: [projectListItem],
      total: 1
    })
    await mockApiJson(page, '/projects/proj_123', projectDetail)
    await mockApiJson(page, '/campaigns?project_id=proj_123', {
      items: [relatedCampaign],
      total: 1
    })

    await page.goto('/projects')

    await expect(page).toHaveURL(/\/projects$/)
    await expect(page.getByTestId('projects-list')).toBeVisible()

    const projectCard = page.getByTestId('project-card-proj_123')
    await expect(projectCard).toBeVisible()
    await expect(projectCard).toContainText(projectListItem.name)
    await expect(projectCard).toContainText(projectListItem.owner_account_id)
    await expect(projectCard).toContainText(projectListItem.updated_at)

    await projectCard.click()

    await expect(page).toHaveURL(/\/projects\/proj_123$/)

    const detailPanel = page.getByTestId('project-detail-panel')
    await expect(detailPanel).toBeVisible()
    await expect(detailPanel).toContainText(projectDetail.name)
    await expect(detailPanel).toContainText(projectDetail.id)
    await expect(detailPanel).toContainText(projectDetail.created_at)
    await expect(detailPanel).toContainText(projectDetail.owner_account_id)

    const relatedCampaignsList = page.getByTestId('project-campaigns-list')
    await expect(relatedCampaignsList).toBeVisible()

    const relatedCampaignCard = page.getByTestId('project-campaign-card-camp_123')
    await expect(relatedCampaignCard).toBeVisible()
    await expect(relatedCampaignCard).toContainText(relatedCampaign.name)
    await expect(relatedCampaignCard).toContainText(
      formatCampaignStatusLabel(relatedCampaign.status as CampaignStatus)
    )
  })

  test('supports creating a project from the frontend form', async ({ page }) => {
    const createdProject = {
      id: 'proj_456',
      name: 'FocusFlow',
      description: 'A focused productivity beta workspace.',
      owner_account_id: developerAccount.id,
      created_at: '2026-04-03T12:00:00Z',
      updated_at: '2026-04-03T12:00:00Z'
    }

    let createRequestBody: unknown = null
    let actorHeader: string | undefined

    await page.route(/\/api\/v1\/projects$/, async (route) => {
      const method = route.request().method()

      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [],
            total: 0
          })
        })
        return
      }

      if (method === 'POST') {
        createRequestBody = JSON.parse(route.request().postData() ?? '{}')
        actorHeader = route.request().headers()['x-actor-id']
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify(createdProject)
        })
        return
      }

      await route.fallback()
    })

    await mockApiJson(page, '/accounts', {
      items: [developerAccount],
      total: 1
    })
    await mockApiJson(page, '/projects/proj_456', createdProject)
    await mockApiJson(page, '/campaigns?project_id=proj_456', {
      items: [],
      total: 0
    })

    await page.goto('/projects')
    await page.getByTestId('project-create-link').click()

    await expect(page).toHaveURL(/\/projects\/new$/)
    await page.waitForLoadState('networkidle')
    const actorSelect = page.getByTestId('current-actor-select').first()
    await actorSelect.selectOption(developerAccount.id)
    await expect(actorSelect).toHaveValue(developerAccount.id)
    await expect(page.getByTestId('project-form')).toBeVisible()

    await page.getByTestId('project-name-input').fill('FocusFlow')
    await page
      .getByTestId('project-description-input')
      .fill('A focused productivity beta workspace.')
    await page.getByTestId('project-submit').click()

    expect(createRequestBody).toEqual({
      name: 'FocusFlow',
      description: 'A focused productivity beta workspace.'
    })
    expect(actorHeader).toBe(developerAccount.id)

    await expect(page).toHaveURL(/\/projects\/proj_456$/)
    await expect(page.getByTestId('project-detail-panel')).toContainText(
      createdProject.name
    )
    await expect(page.getByTestId('project-detail-panel')).toContainText(
      createdProject.owner_account_id
    )
  })

  test('shows project create form validation and backend errors', async ({ page }) => {
    await mockApiJson(page, '/accounts', {
      items: [developerAccount],
      total: 1
    })

    await page.route(/\/api\/v1\/projects$/, async (route) => {
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
                field: 'name',
                message: 'This field is required.'
              }
            ]
          }
        })
      })
    })

    await page.goto('/projects/new')
    await page.getByTestId('current-actor-select').first().selectOption(developerAccount.id)
    await expect(page.getByTestId('project-form')).toBeVisible()
    await page.getByTestId('project-submit').click()

    await expect(page.getByTestId('project-form-error')).toContainText(
      '名稱為必填。'
    )

    await page.getByTestId('project-name-input').fill('FocusFlow')
    await page.getByTestId('project-submit').click()

    await expect(page.getByTestId('project-form-error')).toContainText(
      'Request validation failed.'
    )
  })

  test('supports mine-only filtering with the current actor header', async ({ page }) => {
    const mineProject = {
      ...projectListItem
    }

    let mineRequestHeader: string | undefined

    await page.route(/\/api\/v1\/projects(?:\?mine=true)?$/, async (route) => {
      const url = route.request().url()

      if (url.endsWith('/api/v1/projects?mine=true')) {
        mineRequestHeader = route.request().headers()['x-actor-id']
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [mineProject],
            total: 1
          })
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0
        })
      })
    })

    await mockApiJson(page, '/accounts', {
      items: [developerAccount],
      total: 1
    })

    await page.goto('/projects')

    await page.getByTestId('current-actor-select').first().selectOption(developerAccount.id)
    await page.getByTestId('projects-mine-toggle').click()

    await expect(page.getByTestId('projects-list')).toBeVisible()
    await expect(page.getByTestId('project-card-proj_123')).toBeVisible()
    expect(mineRequestHeader).toBe(developerAccount.id)
  })

  test('supports editing a project from the frontend form', async ({ page }) => {
    const originalProject = {
      ...projectDetail
    }
    const updatedProject = {
      ...projectDetail,
      name: 'HabitQuest Updated',
      description: 'Updated project summary for the beta program.'
    }

    let detailResponse = originalProject
    let updateRequestBody: unknown = null

    await page.route(/\/api\/v1\/projects\/proj_123$/, async (route) => {
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
        updateRequestBody = JSON.parse(route.request().postData() ?? '{}')
        detailResponse = updatedProject
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(updatedProject)
        })
        return
      }

      await route.fallback()
    })

    await mockApiJson(page, '/campaigns?project_id=proj_123', {
      items: [],
      total: 0
    })

    await page.goto('/projects/proj_123')
    await page.getByTestId('project-edit-link').click()

    await expect(page).toHaveURL(/\/projects\/proj_123\/edit$/)
    await expect(page.getByTestId('project-edit-panel')).toBeVisible()

    await page.getByTestId('project-name-input').fill('HabitQuest Updated')
    await page
      .getByTestId('project-description-input')
      .fill('Updated project summary for the beta program.')
    await page.getByTestId('project-submit').click()

    expect(updateRequestBody).toEqual({
      name: 'HabitQuest Updated',
      description: 'Updated project summary for the beta program.'
    })

    await expect(page).toHaveURL(/\/projects\/proj_123$/)
    await expect(page.getByTestId('project-detail-panel')).toContainText(
      updatedProject.name
    )
    await expect(page.getByTestId('project-detail-panel')).toContainText(
      updatedProject.description
    )
  })

  test('renders the project edit error state when the record cannot be loaded', async ({
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

    await page.goto('/projects/proj_missing/edit')

    const errorState = page.getByTestId('project-edit-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Project not found.')
  })

  test('renders the projects empty state when the API returns no items', async ({
    page
  }) => {
    await mockApiJson(page, '/accounts', {
      items: [developerAccount],
      total: 1
    })
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
    await mockApiJson(page, '/accounts', {
      items: [developerAccount],
      total: 1
    })
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
