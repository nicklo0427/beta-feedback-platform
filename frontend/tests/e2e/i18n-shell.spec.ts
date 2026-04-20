import { expect, test, type Page } from '@playwright/test'

async function mockAccounts(page: Page): Promise<void> {
  await page.route(/\/api\/v1\/accounts$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [],
        total: 0
      })
    })
  })
}

test('switches the shell locale to English and persists across routes', async ({ page }) => {
  await mockAccounts(page)

  await page.goto('/')
  await page.waitForLoadState('networkidle')
  await expect(page.getByTestId('public-shell-root')).toBeVisible()
  await expect(page.getByTestId('public-shell-header')).toBeVisible()

  await expect(page.getByTestId('public-shell-login-link')).toContainText('登入')
  await expect(page.getByTestId('home-guest-login-link')).toContainText('登入工作區')

  await page.getByTestId('locale-select').selectOption('en')

  await expect(page.getByTestId('locale-select')).toHaveValue('en')

  await page.reload()
  await page.waitForLoadState('networkidle')

  await expect(page.getByTestId('locale-select')).toHaveValue('en')

  await page.goto('/login')

  await expect(
    page.getByRole('heading', { name: 'Sign in and continue' })
  ).toBeVisible()
  await expect(page.getByTestId('public-shell-register-link')).toContainText('Register')
  await expect(page.getByTestId('login-submit')).toContainText('Sign in')
})
