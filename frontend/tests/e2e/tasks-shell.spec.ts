import { expect, test, type Page } from '@playwright/test'

import { formatQualificationStatusLabel } from '~/features/eligibility/types'
import { formatTaskStatusLabel, type TaskStatus } from '~/features/tasks/types'

import { mockApiError, mockApiJson } from './support/api-mocks'

const developerAccount = {
  id: 'acct_dev_123',
  display_name: 'Release Owner',
  role: 'developer',
  updated_at: '2026-04-05T09:30:00Z'
}

const taskListItem = {
  id: 'task_123',
  campaign_id: 'camp_123',
  device_profile_id: 'dp_123',
  title: 'Validate onboarding flow',
  status: 'assigned',
  updated_at: '2026-04-03T10:00:00Z',
  qualification_context: {
    device_profile_id: 'dp_123',
    device_profile_name: 'QA iPhone 15',
    qualification_status: 'qualified',
    matched_rule_id: 'er_123',
    reason_summary: '符合目前活動的資格條件。',
    qualification_drift: false
  }
}

const taskDetail = {
  id: 'task_123',
  campaign_id: 'camp_123',
  device_profile_id: 'dp_123',
  title: 'Validate onboarding flow',
  instruction_summary: 'Verify the welcome experience and account creation handoff.',
  status: 'submitted',
  submitted_at: '2026-04-03T11:30:00Z',
  created_at: '2026-04-03T09:00:00Z',
  updated_at: '2026-04-03T11:30:00Z',
  qualification_context: {
    device_profile_id: 'dp_123',
    device_profile_name: 'QA iPhone 15',
    qualification_status: 'qualified',
    matched_rule_id: 'er_123',
    reason_summary: '符合目前活動的資格條件。',
    qualification_drift: false
  }
}

const eligibleQualificationPreview = {
  device_profile_id: 'dp_123',
  device_profile_name: 'QA iPhone 15',
  qualification_status: 'qualified',
  matched_rule_id: 'er_123',
  reason_codes: [],
  reason_summary: '符合目前活動的資格條件。'
} as const

const ineligibleQualificationPreview = {
  device_profile_id: 'dp_456',
  device_profile_name: 'QA iPhone 15 (Alt Channel)',
  qualification_status: 'not_qualified',
  matched_rule_id: null,
  reason_codes: ['install_channel_mismatch'],
  reason_summary: '主要未符合條件：安裝渠道不符合目前活動條件。'
} as const

async function mockAccounts(page: Page): Promise<void> {
  await mockApiJson(page, '/accounts', {
    items: [developerAccount],
    total: 1
  })
}

test.describe('tasks shell flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.removeItem('beta-feedback-platform.current-actor-id')
    })
  })

  test('navigates from home to tasks list and detail', async ({ page }) => {
    await mockApiJson(page, '/tasks', {
      items: [taskListItem],
      total: 1
    })
    await mockApiJson(page, '/tasks/task_123', taskDetail)
    await mockApiJson(page, '/tasks/task_123/feedback', {
      items: [],
      total: 0
    })

    await page.goto('/')
    await page.getByTestId('home-tasks-link').click()

    await expect(page).toHaveURL(/\/tasks$/)
    await expect(page.getByTestId('tasks-list')).toBeVisible()

    const taskCard = page.getByTestId('task-card-task_123')
    await expect(taskCard).toBeVisible()
    await expect(taskCard).toContainText(taskListItem.title)
    await expect(taskCard).toContainText(formatTaskStatusLabel(taskListItem.status as TaskStatus))

    await taskCard.click()

    await expect(page).toHaveURL(/\/tasks\/task_123$/)

    const detailPanel = page.getByTestId('task-detail-panel')
    await expect(detailPanel).toBeVisible()
    await expect(detailPanel).toContainText(taskDetail.title)
    await expect(detailPanel).toContainText(formatTaskStatusLabel(taskDetail.status as TaskStatus))
    await expect(detailPanel).toContainText(taskDetail.submitted_at)
    await expect(page.getByTestId('task-qualification-context')).toContainText(
      taskDetail.qualification_context.reason_summary
    )
    await expect(page.getByTestId('task-qualification-context')).toContainText(
      formatQualificationStatusLabel(
        taskDetail.qualification_context.qualification_status as 'qualified' | 'not_qualified'
      )
    )
    await expect(page.getByTestId('task-feedback-empty')).toBeVisible()
  })

  test('shows qualification drift warning on task detail when eligibility changed', async ({
    page
  }) => {
    await mockApiJson(page, '/tasks/task_123', {
      ...taskDetail,
      qualification_context: {
        device_profile_id: 'dp_123',
        device_profile_name: 'QA iPhone 15',
        qualification_status: 'not_qualified',
        matched_rule_id: null,
        reason_summary: '主要未符合條件：安裝渠道不符合目前活動條件。',
        qualification_drift: true
      }
    })
    await mockApiJson(page, '/tasks/task_123/feedback', {
      items: [],
      total: 0
    })

    await page.goto('/tasks/task_123')

    await expect(page.getByTestId('task-qualification-context')).toBeVisible()
    await expect(page.getByTestId('task-qualification-drift-warning')).toBeVisible()
    await expect(page.getByTestId('task-qualification-context')).toContainText('資格已漂移')
    await expect(page.getByTestId('task-qualification-context')).toContainText(
      '主要未符合條件：安裝渠道不符合目前活動條件。'
    )
  })

  test('supports creating a task from the campaign context', async ({ page }) => {
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
    const deviceProfiles = {
      items: [
        {
          id: 'dp_123',
          name: 'QA iPhone 15',
          platform: 'ios',
          device_model: 'iPhone 15 Pro',
          os_name: 'iOS',
          updated_at: '2026-04-03T10:00:00Z'
        }
      ],
      total: 1
    }
    const createdTask = {
      id: 'task_456',
      campaign_id: 'camp_123',
      device_profile_id: 'dp_123',
      title: 'Validate paywall copy',
      instruction_summary: 'Check the paywall CTA and pricing copy.',
      status: 'assigned',
      submitted_at: null,
      created_at: '2026-04-03T12:00:00Z',
      updated_at: '2026-04-03T12:00:00Z'
    }

    let createRequestBody: unknown = null
    let hasCreatedTask = false

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
    await mockApiJson(page, '/campaigns/camp_123/eligibility-rules', {
      items: [],
      total: 0
    })
    await mockApiJson(page, '/device-profiles', deviceProfiles)
    await page.route(/\/api\/v1\/campaigns\/camp_123\/qualification-check/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(eligibleQualificationPreview)
      })
    })
    await mockApiJson(page, '/tasks/task_456/feedback', {
      items: [],
      total: 0
    })
    await page.route(/\/api\/v1\/tasks\?campaign_id=camp_123$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: hasCreatedTask
            ? [
                {
                  id: createdTask.id,
                  campaign_id: createdTask.campaign_id,
                  device_profile_id: createdTask.device_profile_id,
                  title: createdTask.title,
                  status: createdTask.status,
                  updated_at: createdTask.updated_at
                }
              ]
            : [],
          total: hasCreatedTask ? 1 : 0
        })
      })
    })
    await page.route(/\/api\/v1\/campaigns\/camp_123\/tasks$/, async (route) => {
      if (route.request().method() !== 'POST') {
        await route.fallback()
        return
      }

      expect(route.request().headers()['x-actor-id']).toBe(developerAccount.id)
      createRequestBody = JSON.parse(route.request().postData() ?? '{}')
      hasCreatedTask = true

      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(createdTask)
      })
    })
    await page.route(/\/api\/v1\/tasks\/task_456$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(createdTask)
      })
    })

    await page.goto('/campaigns/camp_123')
    await page.getByTestId('campaign-task-create-link').click()

    await expect(page).toHaveURL(/\/campaigns\/camp_123\/tasks\/new$/)
    await expect(page.getByTestId('task-form')).toBeVisible()
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)

    await page.getByTestId('task-title-input').fill('Validate paywall copy')
    await page
      .getByTestId('task-instruction-summary-input')
      .fill('Check the paywall CTA and pricing copy.')
    await page.getByTestId('task-device-profile-field').selectOption('dp_123')
    await expect(page.getByTestId('task-assignment-preview-panel')).toContainText(
      formatQualificationStatusLabel(eligibleQualificationPreview.qualification_status)
    )
    await expect(page.getByTestId('task-assignment-preview-panel')).toContainText(
      eligibleQualificationPreview.reason_summary
    )
    await page.getByTestId('task-status-field').selectOption('assigned')
    await page.getByTestId('task-submit').click()

    expect(createRequestBody).toEqual({
      title: 'Validate paywall copy',
      instruction_summary: 'Check the paywall CTA and pricing copy.',
      device_profile_id: 'dp_123',
      status: 'assigned'
    })

    await expect(page).toHaveURL(/\/tasks\/task_456$/)
    await expect(page.getByTestId('task-detail-panel')).toContainText(createdTask.title)
    await expect(page.getByTestId('task-detail-panel')).toContainText(
      formatTaskStatusLabel(createdTask.status as TaskStatus)
    )
  })

  test('shows task create validation and backend status-transition errors', async ({ page }) => {
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

    await mockAccounts(page)
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiJson(page, '/device-profiles', {
      items: [],
      total: 0
    })
    await page.route(/\/api\/v1\/campaigns\/camp_123\/tasks$/, async (route) => {
      if (route.request().method() !== 'POST') {
        await route.fallback()
        return
      }

      await route.fulfill({
        status: 409,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 'conflict',
          message: 'Task requires a device profile before entering this status.',
          details: {
            resource: 'task',
            status: 'assigned'
          }
        })
      })
    })

    await page.goto('/campaigns/camp_123/tasks/new')
    await page.getByTestId('task-submit').click()

    await expect(page.getByTestId('task-form-error')).toContainText('標題為必填。')

    await page.getByTestId('task-title-input').fill('Validate paywall copy')
    await page.getByTestId('task-submit').click()

    await expect(page.getByTestId('task-form-error')).toContainText(
      '建立任務前，請先選擇目前操作帳號。'
    )

    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)
    await page.getByTestId('task-status-field').selectOption('assigned')
    await page.getByTestId('task-submit').click()

    await expect(page.getByTestId('task-form-error')).toContainText(
      'Task requires a device profile before entering this status.'
    )
  })

  test('blocks task create when the selected device profile is not eligible', async ({
    page
  }) => {
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
    let createRequestReceived = false

    await mockAccounts(page)
    await mockApiJson(page, '/campaigns/camp_123', campaignDetail)
    await mockApiJson(page, '/device-profiles', {
      items: [
        {
          id: 'dp_456',
          name: 'QA Pixel 9',
          platform: 'android',
          device_model: 'Pixel 9',
          os_name: 'Android',
          updated_at: '2026-04-03T10:00:00Z'
        }
      ],
      total: 1
    })
    await page.route(/\/api\/v1\/campaigns\/camp_123\/qualification-check/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(ineligibleQualificationPreview)
      })
    })
    await page.route(/\/api\/v1\/campaigns\/camp_123\/tasks$/, async (route) => {
      createRequestReceived = true
      await route.fallback()
    })

    await page.goto('/campaigns/camp_123/tasks/new')
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)
    await page.getByTestId('task-title-input').fill('Validate Android onboarding flow')
    await page.getByTestId('task-device-profile-field').selectOption('dp_456')

    const previewPanel = page.getByTestId('task-assignment-preview-panel')
    await expect(previewPanel).toContainText(
      formatQualificationStatusLabel(ineligibleQualificationPreview.qualification_status)
    )
    await expect(previewPanel).toContainText(ineligibleQualificationPreview.reason_summary)
    await expect(page.getByTestId('task-submit')).toBeDisabled()
    expect(createRequestReceived).toBe(false)
  })

  test('supports editing a task from the detail page', async ({ page }) => {
    const editableTask = {
      ...taskDetail,
      status: 'assigned',
      submitted_at: null
    }
    const updatedTask = {
      ...editableTask,
      title: 'Validate onboarding flow v2',
      instruction_summary: 'Check the revised onboarding copy.',
      status: 'in_progress'
    }

    let taskResponse = editableTask
    let updateRequestBody: unknown = null

    await mockAccounts(page)
    await page.route(/\/api\/v1\/tasks\/task_123$/, async (route) => {
      const method = route.request().method()

      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(taskResponse)
        })
        return
      }

      if (method === 'PATCH') {
        expect(route.request().headers()['x-actor-id']).toBe(developerAccount.id)
        updateRequestBody = JSON.parse(route.request().postData() ?? '{}')
        taskResponse = updatedTask
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(updatedTask)
        })
        return
      }

      await route.fallback()
    })
    await mockApiJson(page, '/device-profiles', {
      items: [
        {
          id: 'dp_123',
          name: 'QA iPhone 15',
          platform: 'ios',
          device_model: 'iPhone 15 Pro',
          os_name: 'iOS',
          updated_at: '2026-04-03T10:00:00Z'
        }
      ],
      total: 1
    })
    await page.route(/\/api\/v1\/campaigns\/camp_123\/qualification-check/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(eligibleQualificationPreview)
      })
    })
    await mockApiJson(page, '/tasks/task_123/feedback', {
      items: [],
      total: 0
    })

    await page.goto('/tasks/task_123')
    await page.getByTestId('task-edit-link').click()

    await expect(page).toHaveURL(/\/tasks\/task_123\/edit$/)
    await expect(page.getByTestId('task-edit-panel')).toBeVisible()
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)
    await expect(page.getByTestId('task-assignment-preview-panel')).toContainText(
      eligibleQualificationPreview.reason_summary
    )

    await page.getByTestId('task-title-input').fill('Validate onboarding flow v2')
    await page
      .getByTestId('task-instruction-summary-input')
      .fill('Check the revised onboarding copy.')
    await page.getByTestId('task-status-field').selectOption('in_progress')
    await page.getByTestId('task-submit').click()

    expect(updateRequestBody).toEqual({
      title: 'Validate onboarding flow v2',
      instruction_summary: 'Check the revised onboarding copy.',
      status: 'in_progress'
    })

    await expect(page).toHaveURL(/\/tasks\/task_123$/)
    await expect(page.getByTestId('task-detail-panel')).toContainText(updatedTask.title)
    await expect(page.getByTestId('task-detail-panel')).toContainText(
      formatTaskStatusLabel(updatedTask.status as TaskStatus)
    )
  })

  test('blocks task edit when reassigned device profile is not eligible', async ({ page }) => {
    const editableTask = {
      ...taskDetail,
      status: 'assigned',
      submitted_at: null
    }

    let updateRequestReceived = false

    await mockAccounts(page)
    await page.route(/\/api\/v1\/tasks\/task_123$/, async (route) => {
      const method = route.request().method()

      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(editableTask)
        })
        return
      }

      if (method === 'PATCH') {
        updateRequestReceived = true
      }

      await route.fallback()
    })
    await mockApiJson(page, '/device-profiles', {
      items: [
        {
          id: 'dp_123',
          name: 'QA iPhone 15',
          platform: 'ios',
          device_model: 'iPhone 15 Pro',
          os_name: 'iOS',
          updated_at: '2026-04-03T10:00:00Z'
        },
        {
          id: 'dp_456',
          name: 'QA Pixel 9',
          platform: 'android',
          device_model: 'Pixel 9',
          os_name: 'Android',
          updated_at: '2026-04-03T10:00:00Z'
        }
      ],
      total: 2
    })
    await page.route(/\/api\/v1\/campaigns\/camp_123\/qualification-check\?device_profile_id=.*/, async (route) => {
      const requestUrl = route.request().url()
      const payload =
        requestUrl.includes('device_profile_id=dp_456')
          ? ineligibleQualificationPreview
          : eligibleQualificationPreview

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(payload)
      })
    })

    await page.goto('/tasks/task_123/edit')
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)
    await page.getByTestId('task-device-profile-field').selectOption('dp_456')

    const previewPanel = page.getByTestId('task-assignment-preview-panel')
    await expect(previewPanel).toContainText(
      formatQualificationStatusLabel(ineligibleQualificationPreview.qualification_status)
    )
    await expect(previewPanel).toContainText(ineligibleQualificationPreview.reason_summary)
    await expect(page.getByTestId('task-submit')).toBeDisabled()
    expect(updateRequestReceived).toBe(false)
  })

  test('shows backend conflict when a task status transition is invalid', async ({ page }) => {
    await mockAccounts(page)
    await page.route(/\/api\/v1\/tasks\/task_123$/, async (route) => {
      const method = route.request().method()

      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(taskDetail)
        })
        return
      }

      if (method === 'PATCH') {
        await route.fulfill({
          status: 409,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 'conflict',
            message: 'Task status transition is not allowed.',
            details: {
              resource: 'task',
              current_status: 'submitted',
              next_status: 'assigned'
            }
          })
        })
        return
      }

      await route.fallback()
    })
    await mockApiJson(page, '/device-profiles', {
      items: [
        {
          id: 'dp_123',
          name: 'QA iPhone 15',
          platform: 'ios',
          device_model: 'iPhone 15 Pro',
          os_name: 'iOS',
          updated_at: '2026-04-03T10:00:00Z'
        }
      ],
      total: 1
    })
    await mockApiJson(
      page,
      '/campaigns/camp_123/qualification-check?device_profile_id=dp_123',
      eligibleQualificationPreview
    )

    await page.goto('/tasks/task_123/edit')
    await page.getByTestId('current-actor-select').selectOption(developerAccount.id)
    await page.getByTestId('task-status-field').selectOption('assigned')
    await page.getByTestId('task-submit').click()

    await expect(page.getByTestId('task-form-error')).toContainText(
      'Task status transition is not allowed.'
    )
  })

  test('renders the task edit error state when the record cannot be loaded', async ({
    page
  }) => {
    await mockApiError(
      page,
      '/tasks/task_missing',
      {
        code: 'resource_not_found',
        message: 'Task not found.',
        details: {
          resource: 'task',
          id: 'task_missing'
        }
      },
      {
        status: 404
      }
    )
    await mockApiJson(page, '/device-profiles', {
      items: [],
      total: 0
    })

    await page.goto('/tasks/task_missing/edit')

    const errorState = page.getByTestId('task-edit-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Task not found.')
  })

  test('renders the tasks empty state when the API returns no items', async ({
    page
  }) => {
    await mockApiJson(page, '/tasks', {
      items: [],
      total: 0
    })

    await page.goto('/tasks')

    await expect(page.getByTestId('tasks-empty')).toBeVisible()
    await expect(page.getByTestId('tasks-list')).toHaveCount(0)
  })

  test('renders the task detail error state when the detail request fails', async ({
    page
  }) => {
    await mockApiError(
      page,
      '/tasks/task_missing',
      {
        code: 'resource_not_found',
        message: 'Task not found.',
        details: {
          resource: 'task',
          id: 'task_missing'
        }
      },
      {
        status: 404
      }
    )

    await page.goto('/tasks/task_missing')

    const errorState = page.getByTestId('task-detail-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Task not found.')
    await expect(page.getByTestId('task-detail-panel')).toHaveCount(0)
  })
})
