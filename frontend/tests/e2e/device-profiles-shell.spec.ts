import { expect, test } from '@playwright/test'

import { formatPlatformLabel } from '~/features/platform-display'

import { mockApiError, mockApiJson } from './support/api-mocks'

const testerAccount = {
  id: 'acct_tester_123',
  display_name: 'QA Tester',
  role: 'tester',
  updated_at: '2026-04-03T09:30:00Z'
}

const deviceProfileListItem = {
  id: 'dp_123',
  name: 'QA iPhone 15',
  platform: 'ios',
  device_model: 'iPhone 15 Pro',
  os_name: 'iOS',
  install_channel: 'TestFlight',
  owner_account_id: testerAccount.id,
  updated_at: '2026-04-03T10:00:00Z'
}

const deviceProfileDetail = {
  id: 'dp_123',
  name: 'QA iPhone 15',
  platform: 'ios',
  device_model: 'iPhone 15 Pro',
  os_name: 'iOS',
  install_channel: 'TestFlight',
  os_version: '18.1',
  browser_name: 'Safari',
  browser_version: '18.0',
  locale: 'zh-TW',
  notes: 'Internal device',
  owner_account_id: testerAccount.id,
  created_at: '2026-04-01T09:00:00Z',
  updated_at: '2026-04-03T10:00:00Z'
}

const deviceProfileReputation = {
  device_profile_id: 'dp_123',
  tasks_assigned_count: 4,
  tasks_submitted_count: 3,
  feedback_submitted_count: 3,
  submission_rate: 0.75,
  last_feedback_at: '2026-04-03T11:31:00Z',
  updated_at: '2026-04-03T11:31:00Z'
}

test.describe('device profiles shell flows', () => {
  test('navigates from the device profiles list to detail', async ({ page }) => {
    await mockApiJson(page, '/accounts', {
      items: [testerAccount],
      total: 1
    })
    await mockApiJson(page, '/device-profiles', {
      items: [deviceProfileListItem],
      total: 1
    })
    await mockApiJson(page, '/device-profiles/dp_123', deviceProfileDetail)
    await mockApiJson(page, '/device-profiles/dp_123/reputation', deviceProfileReputation)

    await page.goto('/device-profiles')

    await expect(page).toHaveURL(/\/device-profiles$/)
    await expect(page.getByTestId('device-profiles-list')).toBeVisible()

    const deviceProfileCard = page.getByTestId('device-profile-card-dp_123')
    await expect(deviceProfileCard).toBeVisible()
    await expect(deviceProfileCard).toContainText(deviceProfileListItem.name)
    await expect(deviceProfileCard).toContainText(
      formatPlatformLabel(deviceProfileListItem.platform)
    )
    await expect(deviceProfileCard).toContainText(deviceProfileListItem.install_channel)
    await expect(deviceProfileCard).toContainText(deviceProfileListItem.owner_account_id)

    await deviceProfileCard.click()

    await expect(page).toHaveURL(/\/device-profiles\/dp_123$/)

    const detailPanel = page.getByTestId('device-profile-detail-panel')
    await expect(detailPanel).toBeVisible()
    await expect(detailPanel).toContainText(deviceProfileDetail.name)
    await expect(detailPanel).toContainText(deviceProfileDetail.device_model)
    await expect(detailPanel).toContainText(deviceProfileDetail.install_channel)
    await expect(detailPanel).toContainText(deviceProfileDetail.os_version)
    await expect(detailPanel).toContainText(deviceProfileDetail.owner_account_id)

    const reputationPanel = page.getByTestId('device-profile-reputation-panel')
    await expect(reputationPanel).toBeVisible()
    await expect(reputationPanel).toContainText('0.75')
    await expect(reputationPanel).toContainText('4')
    await expect(reputationPanel).toContainText(deviceProfileReputation.last_feedback_at)
  })

  test('supports creating a device profile from the frontend form', async ({ page }) => {
    const createdDeviceProfile = {
      id: 'dp_456',
      name: 'QA Pixel 9',
      platform: 'android',
      device_model: 'Pixel 9',
      os_name: 'Android',
      install_channel: 'Play Store Internal',
      os_version: '15',
      browser_name: 'Chrome',
      browser_version: '136',
      locale: 'en-US',
      notes: 'Owned by the internal QA team.',
      owner_account_id: testerAccount.id,
      created_at: '2026-04-03T12:00:00Z',
      updated_at: '2026-04-03T12:00:00Z'
    }

    let createRequestBody: unknown = null
    let actorHeader: string | undefined

    await page.route(/\/api\/v1\/device-profiles$/, async (route) => {
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
          body: JSON.stringify(createdDeviceProfile)
        })
        return
      }

      await route.fallback()
    })

    await mockApiJson(page, '/accounts', {
      items: [testerAccount],
      total: 1
    })
    await mockApiJson(page, '/device-profiles/dp_456', createdDeviceProfile)

    await page.goto('/device-profiles')
    await page.getByTestId('device-profile-create-link').click()

    await expect(page).toHaveURL(/\/device-profiles\/new$/)
    await page.getByTestId('current-actor-select').first().selectOption(testerAccount.id)
    await expect(page.getByTestId('device-profile-form')).toBeVisible()
    await page.waitForLoadState('networkidle')

    await page.getByTestId('device-profile-name-input').fill('QA Pixel 9')
    await page.getByTestId('device-profile-platform-select').selectOption('android')
    await page.getByTestId('device-profile-device-model-input').fill('Pixel 9')
    await page.getByTestId('device-profile-os-name-input').fill('Android')
    await page.getByTestId('device-profile-install-channel-input').fill('Play Store Internal')
    await page.getByTestId('device-profile-os-version-input').fill('15')
    await page.getByTestId('device-profile-browser-name-input').fill('Chrome')
    await page.getByTestId('device-profile-browser-version-input').fill('136')
    await page.getByTestId('device-profile-locale-input').fill('en-US')
    await page.getByTestId('device-profile-notes-input').fill(
      'Owned by the internal QA team.'
    )
    await page.getByTestId('device-profile-submit').click()

    expect(createRequestBody).toEqual({
      name: 'QA Pixel 9',
      platform: 'android',
      device_model: 'Pixel 9',
      os_name: 'Android',
      install_channel: 'Play Store Internal',
      os_version: '15',
      browser_name: 'Chrome',
      browser_version: '136',
      locale: 'en-US',
      notes: 'Owned by the internal QA team.'
    })
    expect(actorHeader).toBe(testerAccount.id)

    await expect(page).toHaveURL(/\/device-profiles\/dp_456$/)
    await expect(page.getByTestId('device-profile-detail-panel')).toContainText(
      createdDeviceProfile.name
    )
    await expect(page.getByTestId('device-profile-detail-panel')).toContainText(
      createdDeviceProfile.install_channel
    )
    await expect(page.getByTestId('device-profile-detail-panel')).toContainText(
      createdDeviceProfile.owner_account_id
    )
  })

  test('shows create form validation and backend errors', async ({ page }) => {
    await mockApiJson(page, '/accounts', {
      items: [testerAccount],
      total: 1
    })

    await page.route(/\/api\/v1\/device-profiles$/, async (route) => {
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

    await page.goto('/device-profiles/new')
    await page.getByTestId('current-actor-select').first().selectOption(testerAccount.id)
    await expect(page.getByTestId('device-profile-form')).toBeVisible()
    await page.getByTestId('device-profile-submit').click()

    await expect(page.getByTestId('device-profile-form-error')).toContainText(
      '名稱為必填。'
    )

    await page.getByTestId('device-profile-name-input').fill('QA Web Device')
    await page.getByTestId('device-profile-platform-select').selectOption('web')
    await page.getByTestId('device-profile-device-model-input').fill('MacBook Pro')
    await page.getByTestId('device-profile-os-name-input').fill('macOS')
    await page.getByTestId('device-profile-install-channel-input').fill('BrowserStack')
    await page.getByTestId('device-profile-submit').click()

    await expect(page.getByTestId('device-profile-form-error')).toContainText(
      'Request validation failed.'
    )
  })

  test('supports editing a device profile from the frontend form', async ({ page }) => {
    const originalDeviceProfile = {
      ...deviceProfileDetail
    }
    const updatedDeviceProfile = {
      ...deviceProfileDetail,
      name: 'QA iPhone 15 Updated',
      install_channel: 'App Store Connect',
      locale: 'en-US',
      notes: 'Updated from the edit flow.'
    }

    let detailResponse = originalDeviceProfile
    let updateRequestBody: unknown = null

    await page.route(/\/api\/v1\/device-profiles\/dp_123$/, async (route) => {
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
        detailResponse = updatedDeviceProfile
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(updatedDeviceProfile)
        })
        return
      }

      await route.fallback()
    })

    await mockApiJson(page, '/device-profiles/dp_123/reputation', deviceProfileReputation)

    await page.goto('/device-profiles/dp_123')
    await page.getByTestId('device-profile-edit-link').click()

    await expect(page).toHaveURL(/\/device-profiles\/dp_123\/edit$/)
    await expect(page.getByTestId('device-profile-edit-panel')).toBeVisible()

    await page.getByTestId('device-profile-name-input').fill('QA iPhone 15 Updated')
    await page.getByTestId('device-profile-install-channel-input').fill('App Store Connect')
    await page.getByTestId('device-profile-locale-input').fill('en-US')
    await page.getByTestId('device-profile-notes-input').fill('Updated from the edit flow.')
    await page.getByTestId('device-profile-submit').click()

    expect(updateRequestBody).toEqual({
      name: 'QA iPhone 15 Updated',
      install_channel: 'App Store Connect',
      locale: 'en-US',
      notes: 'Updated from the edit flow.'
    })

    await expect(page).toHaveURL(/\/device-profiles\/dp_123$/)
    await expect(page.getByTestId('device-profile-detail-panel')).toContainText(
      updatedDeviceProfile.name
    )
    await expect(page.getByTestId('device-profile-detail-panel')).toContainText(
      updatedDeviceProfile.install_channel
    )
    await expect(page.getByTestId('device-profile-detail-panel')).toContainText(
      updatedDeviceProfile.locale
    )
  })

  test('renders the device profile edit error state when the record cannot be loaded', async ({
    page
  }) => {
    await mockApiError(
      page,
      '/device-profiles/dp_missing',
      {
        code: 'resource_not_found',
        message: 'Device profile not found.',
        details: {
          resource: 'device_profile',
          id: 'dp_missing'
        }
      },
      {
        status: 404
      }
    )

    await page.goto('/device-profiles/dp_missing/edit')

    const errorState = page.getByTestId('device-profile-edit-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Device profile not found.')
  })

  test('renders the device profiles empty state when the API returns no items', async ({
    page
  }) => {
    await mockApiJson(page, '/accounts', {
      items: [testerAccount],
      total: 1
    })
    await mockApiJson(page, '/device-profiles', {
      items: [],
      total: 0
    })

    await page.goto('/device-profiles')

    await expect(page.getByTestId('device-profiles-empty')).toBeVisible()
    await expect(page.getByTestId('device-profiles-list')).toHaveCount(0)
  })

  test('renders the device profile detail error state when the detail request fails', async ({
    page
  }) => {
    await mockApiError(
      page,
      '/device-profiles/dp_missing',
      {
        code: 'resource_not_found',
        message: 'Device profile not found.',
        details: {
          resource: 'device_profile',
          id: 'dp_missing'
        }
      },
      {
        status: 404
      }
    )

    await page.goto('/device-profiles/dp_missing')

    const errorState = page.getByTestId('device-profile-detail-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Device profile not found.')
    await expect(page.getByTestId('device-profile-detail-panel')).toHaveCount(0)
  })

  test('renders the device profile reputation zero state when no signals exist', async ({
    page
  }) => {
    await mockApiJson(page, '/device-profiles/dp_123', deviceProfileDetail)
    await mockApiJson(page, '/device-profiles/dp_123/reputation', {
      device_profile_id: 'dp_123',
      tasks_assigned_count: 0,
      tasks_submitted_count: 0,
      feedback_submitted_count: 0,
      submission_rate: 0,
      last_feedback_at: null,
      updated_at: '2026-04-03T10:00:00Z'
    })

    await page.goto('/device-profiles/dp_123')

    await expect(page.getByTestId('device-profile-reputation-zero')).toBeVisible()
    await expect(page.getByTestId('device-profile-reputation-panel')).toHaveCount(0)
  })

  test('renders the device profile reputation error state when the summary request fails', async ({
    page
  }) => {
    await mockApiJson(page, '/device-profiles/dp_123', deviceProfileDetail)
    await mockApiError(
      page,
      '/device-profiles/dp_123/reputation',
      {
        code: 'internal_error',
        message: 'Reputation service unavailable.',
        details: null
      },
      {
        status: 500
      }
    )

    await page.goto('/device-profiles/dp_123')

    const errorState = page.getByTestId('device-profile-reputation-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Reputation service unavailable.')
    await expect(page.getByTestId('device-profile-reputation-panel')).toHaveCount(0)
  })
})
