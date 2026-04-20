import { expect, test } from '@playwright/test'

test('renders the public homepage IA and core landing sections', async ({ page }) => {
  const response = await page.goto('/')

  expect(response?.ok()).toBeTruthy()

  await expect(page.getByTestId('public-shell-root')).toBeVisible()
  await expect(page.getByTestId('public-shell-header')).toBeVisible()
  await expect(page.getByTestId('app-shell-navigation')).toHaveCount(0)
  await expect(page.getByRole('heading', { name: 'beta-feedback-platform' })).toBeVisible()

  await expect(page.getByTestId('home-guest-hero')).toBeVisible()
  await expect(page.getByTestId('home-guest-visual')).toBeVisible()
  await expect(page.getByTestId('home-trust-proof-section')).toBeVisible()
  await expect(page.getByTestId('home-supporting-visual-review')).toBeVisible()
  await expect(page.getByTestId('home-product-flow-section')).toBeVisible()
  await expect(page.getByTestId('home-role-value-section')).toBeVisible()
  await expect(page.getByTestId('home-supporting-visual-tester')).toBeVisible()
  await expect(page.getByTestId('home-final-cta')).toBeVisible()
  await expect(page.getByTestId('home-non-goals')).toContainText('不是互刷平台')
  await expect(page.getByTestId('home-non-goals')).toContainText('不是評論交換平台')
  await expect(page.getByTestId('home-non-goals')).toContainText('不是灌量工具')
  await expect(page.getByTestId('home-primary-nav')).toHaveCount(0)
})

test('keeps homepage conversion focused on auth and workflow CTA', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded' })

  await expect(page.getByTestId('home-guest-register-link')).toHaveAttribute('href', '/register')
  await expect(page.getByTestId('home-guest-login-link')).toHaveAttribute('href', '/login')
  await expect(page.getByTestId('home-guest-flow-link')).toHaveAttribute('href', '#home-flow')
  await expect(page.getByTestId('home-final-register-link')).toHaveAttribute('href', '/register')
  await expect(page.getByTestId('home-final-login-link')).toHaveAttribute('href', '/login')

  await expect(page.locator('.home-hero-actions a').nth(0)).toContainText('建立帳號')
  await expect(page.locator('.home-hero-actions a').nth(1)).toContainText('登入工作區')
  await expect(page.locator('.home-hero-actions a').nth(2)).toContainText('了解如何運作')

  await expect(page.getByTestId('home-projects-link')).toHaveCount(0)
  await expect(page.getByTestId('home-accounts-link')).toHaveCount(0)
  await expect(page.getByTestId('home-entry-login-card')).toHaveCount(0)
  await expect(page.getByTestId('home-entry-register-card')).toHaveCount(0)
})

test('keeps the public homepage readable on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })

  await page.goto('/')

  await expect(page.getByTestId('public-shell-header')).toBeVisible()
  await expect(page.getByTestId('home-guest-hero')).toBeVisible()
  await expect(page.getByTestId('home-guest-visual')).toBeVisible()
  await expect(page.getByTestId('home-trust-proof-section')).toBeVisible()
  await expect(page.getByTestId('home-product-flow-section')).toBeVisible()
  await expect(page.getByTestId('home-role-value-section')).toBeVisible()
  await expect(page.getByTestId('home-final-cta')).toBeVisible()
})

test('stays a public landing page even when local actor context exists', async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem('beta-feedback-platform.current-actor-id', 'acct_dev_123')
  })

  await page.goto('/')

  await expect(page.getByTestId('home-guest-hero')).toBeVisible()
  await expect(page.getByTestId('home-trust-proof-section')).toBeVisible()
  await expect(page.getByTestId('home-workspace-section')).toHaveCount(0)
  await expect(page.getByTestId('home-role-aware-section')).toHaveCount(0)
})
