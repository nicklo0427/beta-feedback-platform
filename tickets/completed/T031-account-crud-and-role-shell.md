# T031 - Account CRUD and Role Shell

## 1. 背景

目前產品已具備大部分核心資料流，但還沒有 `Account` 資源。這代表系統雖然能建立：

- `Project`
- `Device Profile`
- `Task`
- `Feedback`

卻還無法清楚表示「這些資料是誰的」。

本票的目標不是做正式登入，而是先建立本地可操作的 `Account` baseline。

## 2. 目標

建立 `Account` 的最小 CRUD 與 frontend shell，讓系統開始擁有：

- developer / tester 的正式資料表示
- 後續 ownership 與 current actor 的穩定 anchor

## 3. 範圍

本票只做 MVP 最小集合：

- backend `accounts` 模組 CRUD
- frontend `accounts` list / detail / create / edit
- role baseline：`developer`、`tester`
- shell-level + form-level E2E

## 4. 資料模型建議

`Account` 建議至少包含：

- `id`
- `display_name`
- `role`
- `bio`
- `locale`
- `created_at`
- `updated_at`

規則：

- `display_name` 必填
- `role` 必填
- `bio`、`locale` 選填

## 5. API 路徑建議

- `GET /api/v1/accounts`
- `POST /api/v1/accounts`
- `GET /api/v1/accounts/{account_id}`
- `PATCH /api/v1/accounts/{account_id}`
- `DELETE /api/v1/accounts/{account_id}`

API contract 延續既有：

- list 使用 `{ items, total }`
- error 使用 `code / message / details`
- in-memory repository

## 6. 前端頁面 / 路由建議

- `frontend/pages/accounts/index.vue`
- `frontend/pages/accounts/[accountId].vue`
- `frontend/pages/accounts/new.vue`
- `frontend/pages/accounts/edit-[accountId].vue`

頁面至少包含：

- loading
- empty
- error
- happy path

## 7. Acceptance Criteria

- 可建立 `developer` account
- 可建立 `tester` account
- 可編輯 account 基本欄位
- account list / detail / create / edit flow 可串起來
- backend pytest 補齊：
  - validation
  - service
  - API
- frontend typecheck / build / Playwright 可通過

## 8. Out of Scope

- 不做 login
- 不做 password
- 不做 email 驗證
- 不做 profile image upload
- 不做 organization / team

## 9. Backend Work Items

- 建立 `accounts` 模組
- 建立最小 schema / service / repository / router
- 補 validation / service / API tests
- 保持 in-memory strategy

## 10. Frontend Work Items

- 建立 `features/accounts/`
- 建立 list / detail / create / edit
- 表單只做最小欄位
- API 呼叫維持在 feature / service 層

## 11. Test Items

### 11.1 Backend Tests

- create / update happy path
- blank `display_name`
- bad `role`
- not found

### 11.2 Frontend Tests

- `npm run typecheck`
- `npm run build`

### 11.3 E2E Tests

- account create happy path
- account edit happy path
- account empty state
- bad payload / backend error

## 12. Risk / Notes

- 不要順手把這張票擴成 auth system
- route 與 form pattern 應沿用目前 repo 的既有寫法

## 13. 依賴關係（Dependencies）

主要依賴：

- `T030-account-and-ownership-mvp-schema-draft`

後續支撐：

- `T032-current-actor-context-and-ownership-baseline`
