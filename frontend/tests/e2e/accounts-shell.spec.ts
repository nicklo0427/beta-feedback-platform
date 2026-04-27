import { expect, test } from '@playwright/test'

import { formatAccountRolesLabel } from '~/features/accounts/types'

import { mockApiError, mockApiJson } from './support/api-mocks'

const accountListItem = {
  id: 'acct_123',
  display_name: 'Alice QA',
  role: 'tester',
  roles: ['tester'],
  updated_at: '2026-04-05T09:00:00Z'
}

const accountDetail = {
  id: 'acct_123',
  display_name: 'Alice QA',
  role: 'tester',
  roles: ['tester'],
  bio: 'Mobile web tester',
  locale: 'zh-TW',
  created_at: '2026-04-05T08:00:00Z',
  updated_at: '2026-04-05T09:00:00Z'
}

const testerAccountSummary = {
  account_id: 'acct_123',
  role: 'tester',
  roles: ['tester'],
  developer_summary: null,
  tester_summary: {
    owned_device_profiles_count: 1,
    assigned_tasks_count: 2,
    submitted_feedback_count: 1,
    recent_device_profiles: [
      {
        id: 'dp_123',
        name: 'Alice iPhone',
        platform: 'ios',
        updated_at: '2026-04-05T09:05:00Z'
      }
    ],
    recent_tasks: [
      {
        id: 'task_123',
        campaign_id: 'camp_123',
        title: 'Verify onboarding',
        status: 'submitted',
        updated_at: '2026-04-05T09:10:00Z'
      }
    ],
    recent_feedback: [
      {
        id: 'fb_123',
        task_id: 'task_123',
        summary: 'First-run copy feels unclear',
        review_status: 'submitted',
        submitted_at: '2026-04-05T09:12:00Z'
      }
    ]
  },
  updated_at: '2026-04-05T09:12:00Z'
}

const developerAccountDetail = {
  id: 'acct_dev_123',
  display_name: 'Build Owner',
  role: 'developer',
  roles: ['developer'],
  bio: 'Owns release workflows',
  locale: 'zh-TW',
  created_at: '2026-04-05T08:00:00Z',
  updated_at: '2026-04-05T09:00:00Z'
}

const developerAccountSummary = {
  account_id: 'acct_dev_123',
  role: 'developer',
  roles: ['developer'],
  developer_summary: {
    owned_projects_count: 2,
    owned_campaigns_count: 3,
    feedback_to_review_count: 1,
    recent_projects: [
      {
        id: 'proj_123',
        name: 'Owned Project',
        updated_at: '2026-04-05T09:05:00Z'
      }
    ],
    recent_campaigns: [
      {
        id: 'camp_123',
        project_id: 'proj_123',
        name: 'Closed Beta Round 1',
        status: 'draft',
        updated_at: '2026-04-05T09:10:00Z'
      }
    ]
  },
  tester_summary: null,
  updated_at: '2026-04-05T09:10:00Z'
}

const testerZeroStateDetail = {
  id: 'acct_zero_123',
  display_name: 'Zero Tester',
  role: 'tester',
  roles: ['tester'],
  bio: null,
  locale: null,
  created_at: '2026-04-05T08:00:00Z',
  updated_at: '2026-04-05T09:00:00Z'
}

const testerZeroStateSummary = {
  account_id: 'acct_zero_123',
  role: 'tester',
  roles: ['tester'],
  developer_summary: null,
  tester_summary: {
    owned_device_profiles_count: 0,
    assigned_tasks_count: 0,
    submitted_feedback_count: 0,
    recent_device_profiles: [],
    recent_tasks: [],
    recent_feedback: []
  },
  updated_at: '2026-04-05T09:00:00Z'
}

test.describe('accounts shell flows', () => {
  test('navigates from accounts list to account detail', async ({ page }) => {
    await mockApiJson(page, '/accounts', {
      items: [accountListItem],
      total: 1
    })
    await mockApiJson(page, '/accounts/acct_123', accountDetail)
    await mockApiJson(page, '/accounts/acct_123/summary', testerAccountSummary)

    await page.goto('/accounts')

    await expect(page).toHaveURL(/\/accounts$/)
    await page.waitForLoadState('networkidle')
    await expect(page.getByTestId('accounts-list')).toBeVisible()

    const accountCard = page.getByTestId('account-card-acct_123')
    await expect(accountCard).toBeVisible()
    await expect(accountCard).toContainText(accountListItem.display_name)
    await expect(accountCard).toContainText(formatAccountRolesLabel(accountListItem))

    await accountCard.click()

    await expect(page).toHaveURL(/\/accounts\/acct_123$/)
    await page.getByTestId('current-actor-select').first().selectOption(accountDetail.id)
    const detailPanel = page.getByTestId('account-detail-panel')
    await expect(detailPanel).toBeVisible()
    await expect(detailPanel).toContainText(accountDetail.display_name)
    await expect(detailPanel).toContainText(accountDetail.id)
    await expect(detailPanel).toContainText(accountDetail.bio)

    const testerSummaryPanel = page.getByTestId('account-summary-tester-panel')
    await expect(testerSummaryPanel).toBeVisible()
    await expect(testerSummaryPanel).toContainText('擁有裝置數')
    await expect(testerSummaryPanel).toContainText('已提交回饋數')
  })

  test('supports creating an account from the frontend form', async ({ page }) => {
    const createdAccount = {
      id: 'acct_456',
      display_name: 'Build Owner',
      role: 'developer',
      roles: ['developer', 'tester'],
      bio: 'Owns release campaigns',
      locale: 'en-US',
      created_at: '2026-04-05T10:00:00Z',
      updated_at: '2026-04-05T10:00:00Z'
    }

    await page.route(/\/api\/v1\/accounts$/, async (route) => {
      const method = route.request().method()

      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [
              {
                id: createdAccount.id,
                display_name: createdAccount.display_name,
                role: createdAccount.role,
                roles: createdAccount.roles,
                updated_at: createdAccount.updated_at
              }
            ],
            total: 1
          })
        })
        return
      }

      if (method === 'POST') {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify(createdAccount)
        })
        return
      }

      await route.fallback()
    })

    await mockApiJson(page, '/accounts/acct_456', createdAccount)
    await mockApiJson(page, '/accounts/acct_456/summary', {
      account_id: 'acct_456',
      role: 'developer',
      roles: ['developer', 'tester'],
      developer_summary: {
        owned_projects_count: 0,
        owned_campaigns_count: 0,
        feedback_to_review_count: 0,
        recent_projects: [],
        recent_campaigns: []
      },
      tester_summary: null,
      updated_at: createdAccount.updated_at
    })

    await page.goto('/accounts')
    await page.getByTestId('account-create-link').click()

    await expect(page).toHaveURL(/\/accounts\/new$/)
    await expect(page.getByTestId('account-form')).toBeVisible()
    await page.waitForLoadState('networkidle')

    await page.getByTestId('account-display-name-input').fill('Build Owner')
    await expect(page.getByTestId('account-role-checkbox-developer')).toBeChecked()
    await expect(page.getByTestId('account-role-checkbox-tester')).toBeChecked()
    await page.getByTestId('account-bio-input').fill('Owns release campaigns')
    await page.getByTestId('account-locale-input').fill('en-US')
    const createRequestPromise = page.waitForRequest((request) => {
      return /\/api\/v1\/accounts$/.test(request.url()) && request.method() === 'POST'
    })
    await page.getByTestId('account-submit').click()

    const createRequest = await createRequestPromise
    expect(createRequest.postDataJSON()).toEqual({
      display_name: 'Build Owner',
      role: 'developer',
      roles: ['developer', 'tester'],
      bio: 'Owns release campaigns',
      locale: 'en-US'
    })

    await expect(page).toHaveURL(/\/accounts\/acct_456$/)
    await page.getByTestId('current-actor-select').first().selectOption(createdAccount.id)
    await expect(page.getByTestId('account-detail-panel')).toContainText(
      createdAccount.display_name
    )
  })

  test('shows account create form validation and backend errors', async ({ page }) => {
    await page.route(/\/api\/v1\/accounts$/, async (route) => {
      if (route.request().method() !== 'POST') {
        await route.fallback()
        return
      }

      await route.fulfill({
        status: 422,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 'validation_error',
          message: 'Request validation failed.',
          details: {
            fields: [
              {
                field: 'display_name',
                message: 'This field is required.'
              }
            ]
          }
        })
      })
    })

    await page.goto('/accounts/new')
    await expect(page.getByTestId('account-form')).toBeVisible()
    await page.waitForLoadState('networkidle')
    await page.getByTestId('account-submit').click()

    await expect(page.getByTestId('account-form-error')).toContainText(
      '顯示名稱為必填。'
    )

    await page.getByTestId('account-display-name-input').fill('Builder')
    await page.getByTestId('account-submit').click()

    await expect(page.getByTestId('account-form-error')).toContainText(
      'Request validation failed.'
    )
  })

  test('supports editing an account from the frontend form', async ({ page }) => {
    const originalAccount = {
      ...accountDetail
    }
    const updatedAccount = {
      ...accountDetail,
      display_name: 'Alice Device QA',
      bio: 'Updated tester bio'
    }

    let detailResponse = originalAccount
    let updateRequestBody: unknown = null

    await mockApiJson(page, '/accounts', {
      items: [accountListItem],
      total: 1
    })

    await page.route(/\/api\/v1\/accounts\/acct_123$/, async (route) => {
      const method = route.request().method()

      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(detailResponse)
        })
        return
      }

      if (method === 'PATCH') {
        updateRequestBody = JSON.parse(route.request().postData() ?? '{}')
        detailResponse = updatedAccount
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(updatedAccount)
        })
        return
      }

      await route.fallback()
    })
    await mockApiJson(page, '/accounts/acct_123/summary', testerAccountSummary)

    await page.goto('/accounts/acct_123')
    await page.getByTestId('current-actor-select').first().selectOption(accountDetail.id)
    await page.getByTestId('account-edit-link').click()

    await expect(page).toHaveURL(/\/accounts\/acct_123\/edit$/)
    await expect(page.getByTestId('account-edit-panel')).toBeVisible()

    await page.getByTestId('account-display-name-input').fill('Alice Device QA')
    await page.getByTestId('account-bio-input').fill('Updated tester bio')
    await page.getByTestId('account-submit').click()

    expect(updateRequestBody).toEqual({
      display_name: 'Alice Device QA',
      bio: 'Updated tester bio'
    })

    await expect(page).toHaveURL(/\/accounts\/acct_123$/)
    await page.getByTestId('current-actor-select').first().selectOption(accountDetail.id)
    await expect(page.getByTestId('account-detail-panel')).toContainText(
      updatedAccount.display_name
    )
    await expect(page.getByTestId('account-detail-panel')).toContainText(
      updatedAccount.bio
    )
  })

  test('renders developer collaboration summary on account detail', async ({
    page
  }) => {
    await mockApiJson(page, '/accounts', {
      items: [
        {
          id: developerAccountDetail.id,
          display_name: developerAccountDetail.display_name,
          role: developerAccountDetail.role,
          roles: developerAccountDetail.roles,
          updated_at: developerAccountDetail.updated_at
        }
      ],
      total: 1
    })
    await mockApiJson(page, '/accounts/acct_dev_123', developerAccountDetail)
    await mockApiJson(page, '/accounts/acct_dev_123/summary', developerAccountSummary)

    await page.goto('/accounts/acct_dev_123')
    await page
      .getByTestId('current-actor-select').first()
      .first()
      .selectOption(developerAccountDetail.id)

    const developerSummaryPanel = page.getByTestId('account-summary-developer-panel')
    await expect(developerSummaryPanel).toBeVisible()
    await expect(developerSummaryPanel).toContainText('擁有專案數')
    await expect(developerSummaryPanel).toContainText('待審閱回饋數')
    await expect(page.getByTestId('account-summary-project-proj_123')).toBeVisible()
    await expect(page.getByTestId('account-summary-campaign-camp_123')).toBeVisible()
  })

  test('renders tester collaboration zero state on account detail', async ({
    page
  }) => {
    await mockApiJson(page, '/accounts', {
      items: [
        {
          id: testerZeroStateDetail.id,
          display_name: testerZeroStateDetail.display_name,
          role: testerZeroStateDetail.role,
          roles: testerZeroStateDetail.roles,
          updated_at: testerZeroStateDetail.updated_at
        }
      ],
      total: 1
    })
    await mockApiJson(page, '/accounts/acct_zero_123', testerZeroStateDetail)
    await mockApiJson(page, '/accounts/acct_zero_123/summary', testerZeroStateSummary)

    await page.goto('/accounts/acct_zero_123')
    await page
      .getByTestId('current-actor-select').first()
      .first()
      .selectOption(testerZeroStateDetail.id)

    await expect(page.getByTestId('account-summary-tester-panel')).toBeVisible()
    await expect(page.getByTestId('account-summary-tester-empty')).toBeVisible()
  })

  test('renders the accounts empty state when the API returns no items', async ({
    page
  }) => {
    await mockApiJson(page, '/accounts', {
      items: [],
      total: 0
    })

    await page.goto('/accounts')

    await expect(page.getByTestId('accounts-empty')).toBeVisible()
    await expect(page.getByTestId('accounts-list')).toHaveCount(0)
  })

  test('renders the account edit error state when the record cannot be loaded', async ({
    page
  }) => {
    await mockApiError(
      page,
      '/accounts/acct_missing',
      {
        code: 'resource_not_found',
        message: 'Account not found.',
        details: {
          resource: 'account',
          id: 'acct_missing'
        }
      },
      {
        status: 404
      }
    )

    await page.goto('/accounts/acct_missing/edit')

    const errorState = page.getByTestId('account-edit-error')
    await expect(errorState).toBeVisible()
    await expect(errorState).toContainText('Account not found.')
    await expect(page.getByTestId('account-edit-panel')).toHaveCount(0)
  })

  test('requires selecting the matching actor to view account detail', async ({
    page
  }) => {
    await mockApiJson(page, '/accounts', {
      items: [accountListItem],
      total: 1
    })
    await mockApiError(
      page,
      '/accounts/acct_123',
      {
        code: 'missing_actor_context',
        message: 'Current actor is required.',
        details: {
          header: 'X-Actor-Id'
        }
      },
      {
        status: 400
      }
    )

    await page.goto('/accounts/acct_123')
    await expect(page.getByTestId('account-detail-select-actor')).toBeVisible()
  })
})
