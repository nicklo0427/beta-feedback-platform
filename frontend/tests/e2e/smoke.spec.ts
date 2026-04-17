import { expect, test } from '@playwright/test'

test('loads without an uncaught runtime crash', async ({ page }) => {
  const pageErrors: string[] = []

  page.on('pageerror', (error) => {
    pageErrors.push(error.message)
  })

  const response = await page.goto('/')

  expect(response?.ok()).toBeTruthy()
  await expect(page.getByTestId('public-shell-root')).toBeVisible()
  expect(pageErrors).toEqual([])
})
