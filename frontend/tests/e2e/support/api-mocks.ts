import type { Page } from '@playwright/test'

interface MockApiResponseOptions {
  status?: number
}

interface MockApiErrorPayload {
  code: string
  message: string
  details: unknown
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function buildApiMatcher(path: string): RegExp {
  return new RegExp(`${escapeRegExp(`/api/v1${path}`)}$`)
}

export async function mockApiJson(
  page: Page,
  path: string,
  body: unknown,
  options: MockApiResponseOptions = {}
): Promise<void> {
  await page.route(buildApiMatcher(path), async (route) => {
    await route.fulfill({
      status: options.status ?? 200,
      contentType: 'application/json',
      body: JSON.stringify(body)
    })
  })
}

export async function mockApiError(
  page: Page,
  path: string,
  payload: MockApiErrorPayload,
  options: MockApiResponseOptions = {}
): Promise<void> {
  await mockApiJson(page, path, payload, {
    status: options.status ?? 500
  })
}
