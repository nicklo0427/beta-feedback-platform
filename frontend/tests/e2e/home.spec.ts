import { expect, test } from '@playwright/test'

test('renders the homepage IA and overview shell', async ({ page }) => {
  const response = await page.goto('/')

  expect(response?.ok()).toBeTruthy()

  await expect(
    page.getByRole('heading', { name: 'beta-feedback-platform' })
  ).toBeVisible()

  await expect(page.getByTestId('home-overview-section')).toBeVisible()
  await expect(page.getByTestId('home-primary-nav')).toBeVisible()
  await expect(page.getByTestId('home-core-flow')).toBeVisible()
  await expect(page.getByTestId('home-non-goals')).toContainText('不是互刷平台')
  await expect(page.getByTestId('home-non-goals')).toContainText('不是評論交換平台')
  await expect(page.getByTestId('home-non-goals')).toContainText('不是灌量工具')
})

test('navigates from the homepage to core module list pages', async ({ page }) => {
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
