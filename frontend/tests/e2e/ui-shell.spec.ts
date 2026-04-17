import { expect, test } from '@playwright/test'

const fallbackAccounts = {
  items: [
    {
      id: 'acct_dev_shell',
      display_name: 'Shell Dev',
      role: 'developer',
      updated_at: '2026-04-13T08:00:00Z'
    }
  ],
  total: 1
}

test.describe('ui shell foundation', () => {
  test.beforeEach(async ({ page }) => {
    await page.route(/\/api\/v1\/accounts$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(fallbackAccounts)
      })
    })

    await page.route(/\/api\/v1\/projects$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0
        })
      })
    })
  })

  test('persists theme toggle choice across reloads', async ({ page }) => {
    await page.goto('/projects')
    await page.evaluate(() => {
      window.localStorage.removeItem('beta-feedback-platform.current-actor-id')
      window.localStorage.removeItem('beta-feedback-platform.theme-mode')
    })
    await page.reload()
    await expect(page.getByTestId('current-actor-select')).toBeVisible()

    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light')
    await page.getByTestId('theme-toggle').click()
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')

    await page.reload()
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  })

  test('uses the desktop shell navigation for primary routes', async ({ page }) => {
    await page.goto('/projects')
    await page.evaluate(() => {
      window.localStorage.removeItem('beta-feedback-platform.current-actor-id')
      window.localStorage.removeItem('beta-feedback-platform.theme-mode')
    })
    await page.reload()
    await expect(page.getByTestId('current-actor-select')).toBeVisible()

    await expect(page.getByTestId('app-shell-navigation')).toBeVisible()
    await page.getByTestId('nav-projects').click()
    await expect(page).toHaveURL(/\/projects$/)

    await page.getByTestId('nav-device-profiles').click()
    await expect(page).toHaveURL(/\/device-profiles$/)
  })

  test('supports mobile drawer navigation without breaking the route contract', async ({
    page
  }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto('/projects')
    await page.evaluate(() => {
      window.localStorage.removeItem('beta-feedback-platform.current-actor-id')
      window.localStorage.removeItem('beta-feedback-platform.theme-mode')
    })
    await page.reload()
    await expect(page.getByTestId('current-actor-select')).toBeVisible()

    await expect(page.getByTestId('app-mobile-nav-toggle')).toBeVisible()
    await page.getByTestId('app-mobile-nav-toggle').click()
    await page.getByTestId('nav-review-feedback').scrollIntoViewIfNeeded()
    await page.getByTestId('nav-review-feedback').evaluate((element: HTMLElement) => {
      element.click()
    })

    await expect(page).toHaveURL(/\/review\/feedback$/)
  })
})
