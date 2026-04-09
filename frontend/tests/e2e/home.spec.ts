import { expect, test, type Page } from '@playwright/test'

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

async function mockAccounts(
  page: Page,
  accounts: Array<typeof developerAccount | typeof testerAccount>
): Promise<void> {
  await page.route(/\/api\/v1\/accounts$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: accounts,
        total: accounts.length
      })
    })
  })
}

test('renders the homepage IA and overview shell', async ({ page }) => {
  await mockAccounts(page, [])

  const response = await page.goto('/')

  expect(response?.ok()).toBeTruthy()

  await expect(
    page.getByRole('heading', { name: 'beta-feedback-platform' })
  ).toBeVisible()

  await expect(page.getByTestId('home-role-aware-section')).toBeVisible()
  await expect(page.getByTestId('home-role-select-actor')).toBeVisible()
  await expect(page.getByTestId('home-overview-section')).toBeVisible()
  await expect(page.getByTestId('home-primary-nav')).toBeVisible()
  await expect(page.getByTestId('home-core-flow')).toBeVisible()
  await expect(page.getByTestId('home-non-goals')).toContainText('不是互刷平台')
  await expect(page.getByTestId('home-non-goals')).toContainText('不是評論交換平台')
  await expect(page.getByTestId('home-non-goals')).toContainText('不是灌量工具')
})

test('navigates from the homepage to core module list pages', async ({ page }) => {
  await mockAccounts(page, [])

  await page.goto('/')

  await page.getByTestId('home-accounts-link').click()
  await expect(page).toHaveURL(/\/accounts$/)

  await page.goto('/')
  await page.getByTestId('home-projects-link').click()
  await expect(page).toHaveURL(/\/projects$/)

  await page.goto('/')
  await page.getByTestId('home-campaigns-link').click()
  await expect(page).toHaveURL(/\/campaigns$/)

  await page.goto('/')
  await page.getByTestId('home-device-profiles-link').click()
  await expect(page).toHaveURL(/\/device-profiles$/)

  await page.goto('/')
  await page.getByTestId('home-tasks-link').click()
  await expect(page).toHaveURL(/\/tasks$/)
})

test('switches to a developer-aware homepage overview and opens the owned project workspace', async ({
  page
}) => {
  await mockAccounts(page, [developerAccount, testerAccount])

  await page.route(/\/api\/v1\/projects\?mine=true$/, async (route) => {
    expect(route.request().headers()['x-actor-id']).toBe(developerAccount.id)
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [],
        total: 2
      })
    })
  })

  await page.route(/\/api\/v1\/campaigns\?mine=true$/, async (route) => {
    expect(route.request().headers()['x-actor-id']).toBe(developerAccount.id)
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [],
        total: 5
      })
    })
  })

  await page.route(/\/api\/v1\/feedback\?mine=true&review_status=submitted$/, async (route) => {
    expect(route.request().headers()['x-actor-id']).toBe(developerAccount.id)
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [],
        total: 3
      })
    })
  })

  await page.goto('/')
  await page.getByTestId('current-actor-select').selectOption(developerAccount.id)

  await expect(page.getByTestId('home-role-developer')).toBeVisible()
  await expect(page.getByTestId('home-role-card-projects')).toContainText('2')
  await expect(page.getByTestId('home-role-card-campaigns')).toContainText('5')
  await expect(page.getByTestId('home-role-card-review-queue')).toContainText('3')
  await expect(page.getByTestId('home-role-meta')).toContainText('Release Owner')
  await expect(page.getByTestId('home-role-meta')).toContainText('開發者')
  await expect(page.getByTestId('home-role-action-campaigns')).toBeVisible()

  await page.getByTestId('home-role-action-projects').click()
  await expect(page).toHaveURL(/\/my\/projects$/)
})

test('switches to a tester-aware homepage overview and opens the tester inbox', async ({
  page
}) => {
  await mockAccounts(page, [testerAccount])

  await page.route(/\/api\/v1\/device-profiles\?mine=true$/, async (route) => {
    expect(route.request().headers()['x-actor-id']).toBe(testerAccount.id)
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [],
        total: 2
      })
    })
  })

  await page.route(/\/api\/v1\/tasks\?status=assigned&mine=true$/, async (route) => {
    expect(route.request().headers()['x-actor-id']).toBe(testerAccount.id)
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [],
        total: 4
      })
    })
  })

  await page.route(/\/api\/v1\/tasks\?status=in_progress&mine=true$/, async (route) => {
    expect(route.request().headers()['x-actor-id']).toBe(testerAccount.id)
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [],
        total: 1
      })
    })
  })

  await page.goto('/')
  await page.getByTestId('current-actor-select').selectOption(testerAccount.id)

  await expect(page.getByTestId('home-role-tester')).toBeVisible()
  await expect(page.getByTestId('home-role-card-device-profiles')).toContainText('2')
  await expect(page.getByTestId('home-role-card-assigned-tasks')).toContainText('4')
  await expect(page.getByTestId('home-role-card-in-progress-tasks')).toContainText('1')
  await expect(page.getByTestId('home-role-meta')).toContainText('QA Tester')
  await expect(page.getByTestId('home-role-meta')).toContainText('測試者')
  await expect(page.getByTestId('home-role-action-eligible-campaigns')).toBeVisible()

  await page.getByTestId('home-role-action-my-tasks').click()
  await expect(page).toHaveURL(/\/my\/tasks$/)
})
