import { expect, test } from '@playwright/test'

test('renders the frontend bootstrap home page', async ({ page }) => {
  const response = await page.goto('/')

  expect(response?.ok()).toBeTruthy()

  await expect(
    page.getByRole('heading', { name: 'beta-feedback-platform' })
  ).toBeVisible()

  await expect(
    page.getByText('Nuxt 3 + TypeScript 的最小前端骨架')
  ).toBeVisible()
})
