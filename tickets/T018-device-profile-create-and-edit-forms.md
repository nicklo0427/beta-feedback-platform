# T018 - Device Profile Create and Edit Forms

## 1. 背景

`T012` 已完成 `Tester Device Profile` 的最小 CRUD 與 frontend list / detail shell，代表系統已能顯示裝置資料，但還缺乏實際可操作的建立與編輯入口。

若沒有表單能力，`Device Profile` 仍然偏工程可用而非產品可用，後續：

- Eligibility 設定
- Task 指派
- Feedback 上下文

都會停留在必須手動 seed 或直接打 API 的狀態。這不符合目前專案已進入「產品化補強」階段的目標。

因此，本票聚焦在把 `Device Profile` 從 shell 提升到可操作 CRUD flow，但仍維持 MVP 最小集合，不做 advanced form。

## 2. 目標

建立 `Device Profile` 的 create / edit form，讓使用者可透過 frontend 完成最小的建立與編輯流程。

本票完成後，應具備以下結果：

- `/device-profiles` 可進入 create flow
- `/device-profiles/[deviceProfileId]` 可進入 edit flow
- frontend 表單可串接既有 backend CRUD
- validation / success / error path 可用

## 3. 範圍

本票只做 MVP 最小集合，範圍如下：

- 建立 device profile create form
- 建立 device profile edit form
- 串接既有 backend `POST /device-profiles` 與 `PATCH /device-profiles/{id}`
- 顯示最小 validation / submit / error / success state
- 補 shell-level 與 form-level Playwright 測試

本票可操作欄位與 `T012` 一致：

- `name`
- `platform`
- `device_model`
- `os_name`
- `os_version`
- `browser_name`
- `browser_version`
- `locale`
- `notes`

## 4. 資料模型建議

本票不新增新欄位，完全沿用 `T012` 的 resource shape 與 contract。

### 4.1 Create / Edit Form Baseline

- create form 使用 `T012` 的 create body
- edit form 使用 `PATCH`
- optional string 欄位在前端送出前可做最小 trimming，但不得自行改變 backend contract

### 4.2 Validation Baseline

- `name` 必填
- `platform` 必填
- `device_model` 必填
- `os_name` 必填
- 其他欄位選填
- 以 backend 為最終 validation source of truth

## 5. API 路徑建議

沿用既有 API：

- `POST /api/v1/device-profiles`
- `PATCH /api/v1/device-profiles/{device_profile_id}`
- `GET /api/v1/device-profiles/{device_profile_id}`

本票不新增新 API。

## 6. 前端頁面 / 路由建議

### 6.1 Feature Placement

- 延用既有：
  - `frontend/features/device-profiles/`

### 6.2 Route Suggestion

- `frontend/pages/device-profiles/new.vue`
- `frontend/pages/device-profiles/[deviceProfileId]/edit.vue`

### 6.3 Form UI Requirements

- create 頁提供最小表單
- edit 頁載入既有資料後提供同一份表單
- 至少包含：
  - loading
  - submit pending
  - validation / backend error
  - success redirect 或 success message
- 補穩定 selector，例如：
  - `data-testid="device-profile-form"`
  - `data-testid="device-profile-submit"`
  - `data-testid="device-profile-form-error"`

## 7. Acceptance Criteria

- frontend 已新增 `Device Profile` create / edit form
- frontend 表單已串接既有 backend CRUD
- create 成功後可回到 detail 或 list
- edit 成功後可回到 detail
- backend error 可顯示在表單中
- frontend typecheck / build 可通過
- Playwright 已補齊 device profile form 的最小流程測試
- 本票未導入大型表單框架或 advanced form builder

## 8. Out of Scope

- 不實作 bulk import
- 不實作批次編輯
- 不實作 account 綁定
- 不實作 advanced form
- 不實作 autosave
- 不實作推薦欄位
- 不調整 backend schema

## 9. Backend Work Items

本票原則上不擴 backend domain，僅允許極小必要配合：

- 若既有 CRUD 已足夠，backend 不應新增新 API
- 若表單 flow 遇到 contract 缺口，只允許做最小修補，不得順手重構 `device_profiles` module

## 10. Frontend Work Items

- 在 `frontend/features/device-profiles/` 中補 form helper 或 composable
- 新增 create / edit route
- 將 API 呼叫維持在 feature / service 層
- 讓 list / detail 頁面有明確入口可導到 create / edit
- 先維持簡單欄位排列，不做高互動 form UX

## 11. Test Items

### 11.1 Frontend Tests

- typecheck
- build

### 11.2 E2E Tests

- create happy path
- create validation / backend error path
- edit happy path
- edit 載入失敗 error path

### 11.3 Regression Focus

- 既有 `/device-profiles` list / detail shell 不可被破壞
- 首頁連到 device profiles 的入口需持續可用

## 12. Risk / Notes

- 本票應盡量重用單一 form 結構，避免 create / edit 各自發展出不同 UI
- 若前端需要新樣式，必須先判斷是共用 SCSS 還是單頁 scoped style；不要因為表單出現就把所有樣式塞進全域
- 這張票的目標是可操作，不是做完整 onboarding form

## 13. 依賴關係（Dependencies）

主要依賴：

- `T012-tester-device-profile-crud-and-shell-flows`

後續可支撐：

- `T019-eligibility-rule-create-and-edit-forms`
- `T020-task-create-and-edit-forms`
- `T022-reputation-baseline-and-summary-metrics`
