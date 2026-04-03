import { expect, test } from '@playwright/test'

import { mockApiError, mockApiJson } from './support/api-mocks'

const deviceProfileListItem = {
  id: 'dp_123',
  name: 'QA iPhone 15',
  platform: 'ios',
  device_model: 'iPhone 15 Pro',
  os_name: 'iOS',
  updated_at: '2026-04-03T10:00:00Z'
}

const deviceProfileDetail = {
  id: 'dp_123',
  name: 'QA iPhone 15',
  platform: 'ios',
  device_model: 'iPhone 15 Pro',
  os_name: 'iOS',
  os_version: '18.1',
  browser_name: 'Safari',
  browser_version: '18.0',
  locale: 'zh-TW',
  notes: 'Internal device',
  created_at: '2026-04-01T09:00:00Z',
  updated_at: '2026-04-03T10:00:00Z'
}

test.describe('device profiles shell flows', () => {
  test('navigates from home to device profiles list and detail', async ({ page }) => {
    await mockApiJson(page, '/device-profiles', {
      items: [deviceProfileListItem],
      total: 1
    })
    await mockApiJson(page, '/device-profiles/dp_123', deviceProfileDetail)

    await page.goto('/')
    await page.getByTestId('home-device-profiles-link').click()

    await expect(page).toHaveURL(/\/device-profiles$/)
    await expect(page.getByTestId('device-profiles-list')).toBeVisible()

    const deviceProfileCard = page.getByTestId('device-profile-card-dp_123')
    await expect(deviceProfileCard).toBeVisible()
    await expect(deviceProfileCard).toContainText(deviceProfileListItem.name)
    await expect(deviceProfileCard).toContainText(deviceProfileListItem.platform)

    await deviceProfileCard.click()

    await expect(page).toHaveURL(/\/device-profiles\/dp_123$/)

    const detailPanel = page.getByTestId('device-profile-detail-panel')
    await expect(detailPanel).toBeVisible()
    await expect(detailPanel).toContainText(deviceProfileDetail.name)
    await expect(detailPanel).toContainText(deviceProfileDetail.device_model)
    await expect(detailPanel).toContainText(deviceProfileDetail.os_version)
  })

  test('renders the device profiles empty state when the API returns no items', async ({
    page
  }) => {
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
})
