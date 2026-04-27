import { expect, test } from '@playwright/test'

test('renders the public homepage IA and core landing sections', async ({ page }) => {
  const response = await page.goto('/')

  expect(response?.ok()).toBeTruthy()

  await expect(page.getByTestId('public-shell-root')).toBeVisible()
  await expect(page.getByTestId('public-shell-header')).toBeVisible()
  await expect(page.getByTestId('public-shell-brand-icon')).toBeVisible()
  await expect(page.getByTestId('public-shell-brand-icon')).toHaveAttribute(
    'src',
    /header-brand-icon\.webp$/
  )
  await expect(page.getByTestId('app-shell-navigation')).toHaveCount(0)
  await expect(page.getByRole('heading', { name: /做了新東西/ })).toBeVisible()

  await expect(page.getByTestId('home-guest-hero')).toBeVisible()
  await expect(page.getByTestId('home-guest-visual')).toBeVisible()
  await expect(page.getByTestId('home-guest-visual').locator('img')).toHaveAttribute(
    'src',
    /hero-people-collaboration\.webp$/
  )
  await expect(page.getByTestId('home-guest-visual').locator('img')).toHaveAttribute(
    'alt',
    /協作場景/
  )
  await expect(page.getByTestId('home-trust-proof-section')).toBeVisible()
  await expect(page.getByTestId('home-supporting-visual-review')).toBeVisible()
  await expect(page.getByTestId('home-trust-signal-image')).toHaveAttribute(
    'src',
    /professional-signal-not-shortcut\.webp$/
  )
  await expect(page.getByTestId('home-trust-tabs')).toBeVisible()
  await expect(page.getByTestId('home-trust-signal-notShortcut')).toHaveAttribute('aria-selected', 'true')
  await expect(page.getByTestId('home-trust-panel-notShortcut')).toBeVisible()
  await expect(page.getByTestId('home-product-flow-section')).toBeVisible()
  await expect(page.getByTestId('home-product-flow-section')).toContainText('發起試玩')
  await expect(page.getByTestId('home-product-flow-section')).toContainText('找人試用')
  await expect(page.getByTestId('home-product-flow-section')).toContainText('收回饋，整理下一步')
  await expect(page.getByTestId('home-flow-stage-create')).toBeVisible()
  await expect(page.getByTestId('home-flow-stage-image-create')).toHaveAttribute(
    'src',
    /product-flow-stage-create\.webp$/
  )
  await expect(page.getByTestId('home-flow-stage-image-invite')).toHaveAttribute(
    'src',
    /product-flow-stage-invite\.webp$/
  )
  await expect(page.getByTestId('home-flow-stage-image-learn')).toHaveAttribute(
    'src',
    /product-flow-stage-learn\.webp$/
  )
  await expect(page.getByTestId('home-role-value-section')).toBeVisible()
  await expect(page.getByTestId('home-role-card-developer')).toBeVisible()
  await expect(page.getByTestId('home-role-card-tester')).toBeVisible()
  await expect(page.getByTestId('home-role-image-developer')).toHaveAttribute(
    'src',
    /role-value-developer\.webp$/
  )
  await expect(page.getByTestId('home-role-image-tester')).toHaveAttribute(
    'src',
    /role-value-tester\.webp$/
  )
  await expect(page.getByTestId('home-role-handoff')).toBeVisible()
  await expect(page.getByTestId('home-final-cta')).toBeVisible()
  await expect(page.getByTestId('home-non-goals')).toContainText('不是互刷平台')
  await expect(page.getByTestId('home-non-goals')).toContainText('不是評論交換平台')
  await expect(page.getByTestId('home-non-goals')).toContainText('不是灌量工具')
  await expect(page.getByTestId('home-primary-nav')).toHaveCount(0)
})

test('switches trust signal details and visuals from the tabs', async ({ page }) => {
  await page.goto('/')
  await page.waitForLoadState('networkidle')

  await expect(page.getByTestId('home-trust-signal-image')).toHaveAttribute(
    'src',
    /professional-signal-not-shortcut\.webp$/
  )

  await page.getByTestId('home-trust-signal-safetyFirst').click()
  await expect(page.getByTestId('home-trust-signal-safetyFirst')).toHaveAttribute('aria-selected', 'true')
  await expect(page.getByTestId('home-trust-panel-safetyFirst')).toContainText('官方測試與分發方式')
  await expect(page.getByTestId('home-trust-signal-image')).toHaveAttribute(
    'src',
    /professional-signal-safety-first\.webp$/
  )

  await page.getByTestId('home-trust-signal-platforms').click()
  await expect(page.getByTestId('home-trust-signal-platforms')).toHaveAttribute('aria-selected', 'true')
  await expect(page.getByTestId('home-trust-panel-platforms')).toContainText('Web / Mobile Web / PWA')
  await expect(page.getByTestId('home-trust-panel-platforms')).toContainText('iOS')
  await expect(page.getByTestId('home-trust-panel-platforms')).toContainText('Android')
  await expect(page.getByTestId('home-trust-signal-image')).toHaveAttribute(
    'src',
    /professional-signal-platforms\.webp$/
  )
})

test('keeps homepage conversion focused on auth and workflow CTA', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded' })

  await expect(page.getByTestId('home-guest-register-link')).toHaveAttribute('href', '/register')
  await expect(page.getByTestId('home-guest-login-link')).toHaveAttribute('href', '/login')
  await expect(page.getByTestId('home-guest-flow-link')).toHaveAttribute('href', '#home-flow')
  await expect(page.getByTestId('home-final-register-link')).toHaveAttribute('href', '/register')
  await expect(page.getByTestId('home-final-login-link')).toHaveAttribute('href', '/login')
  await expect(page.getByTestId('home-role-cta-developer')).toHaveAttribute(
    'href',
    '/register?role=developer'
  )
  await expect(page.getByTestId('home-role-cta-tester')).toHaveAttribute(
    'href',
    '/register?role=tester'
  )

  await expect(page.locator('.home-hero-actions a').nth(0)).toContainText('開始找人試玩')
  await expect(page.locator('.home-hero-actions a').nth(1)).toContainText('登入工作區')
  await expect(page.locator('.home-hero-actions a').nth(2)).toContainText('看看怎麼玩')

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
  await expect(page.getByTestId('home-guest-visual').locator('img')).toHaveAttribute(
    'src',
    /hero-people-collaboration\.webp$/
  )
  await expect(page.getByTestId('home-trust-proof-section')).toBeVisible()
  await expect(page.getByTestId('home-product-flow-section')).toBeVisible()
  await expect(page.getByTestId('home-flow-stage-image-create')).toBeVisible()
  await expect(page.getByTestId('home-flow-stage-image-invite')).toBeVisible()
  await expect(page.getByTestId('home-flow-stage-image-learn')).toBeVisible()
  await expect(page.getByTestId('home-role-value-section')).toBeVisible()
  await expect(page.getByTestId('home-role-card-developer')).toBeVisible()
  await expect(page.getByTestId('home-role-card-tester')).toBeVisible()
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
