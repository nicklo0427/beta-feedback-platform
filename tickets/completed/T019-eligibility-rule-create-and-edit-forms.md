# T019 - Eligibility Rule Create and Edit Forms

## 1. 背景

`T013` 已完成 `Eligibility Rule` 的資料表示、backend CRUD 與 `campaign detail` 下的 shell 顯示，但目前開發者仍無法透過 UI 真正建立與修改資格條件。

沒有表單入口時，eligibility 只存在於 shell 與 API，產品無法真正支持：

- 設定 campaign 參與條件
- 調整平台 / OS / 安裝渠道限制
- 驗證 campaign 是否已具備最小資格條件設定

本票的目的是把 `Eligibility Rule` 從資料存在提升到可操作，但仍維持 MVP 最小集合，不做動態 rule builder。

## 2. 目標

建立 `Eligibility Rule` 的 create / edit form，讓開發者可透過 frontend 為 `Campaign` 建立或更新最小資格條件。

本票完成後，應具備以下結果：

- 可從 campaign detail 進入 create eligibility rule flow
- 可從 rule detail 或 campaign detail 進入 edit flow
- frontend 表單可串接既有 backend CRUD
- 結果可回寫到既有 campaign detail eligibility section

## 3. 範圍

本票只做 MVP 最小集合，範圍如下：

- 建立 eligibility rule create form
- 建立 eligibility rule edit form
- 串接既有 nested create 與 patch API
- 顯示最小 validation / submit / error / success state
- 補 Playwright form flow 測試

本票可操作欄位與 `T013` 一致：

- `platform`
- `os_name`
- `os_version_min`
- `os_version_max`
- `install_channel`
- `is_active`

## 4. 資料模型建議

本票不新增欄位，完全沿用 `T013` 的 eligibility rule shape。

### 4.1 Form Baseline

- create form 不需要 `campaign_id` 手填，應由 route context 帶入
- edit form 不允許修改 `campaign_id`
- `platform` 必填
- `is_active` 預設為 `true`
- `os_version_min / os_version_max` 仍視為普通字串欄位

### 4.2 Validation Notes

- 前端只做最小欄位層級驗證
- 真正 enum 與 payload 驗證仍以 backend 為準
- 本票不做版本號邏輯比較器

## 5. API 路徑建議

沿用既有 API：

- `POST /api/v1/campaigns/{campaign_id}/eligibility-rules`
- `GET /api/v1/eligibility-rules/{eligibility_rule_id}`
- `PATCH /api/v1/eligibility-rules/{eligibility_rule_id}`

本票不新增新 API。

## 6. 前端頁面 / 路由建議

### 6.1 Feature Placement

- 延用既有：
  - `frontend/features/eligibility/`

### 6.2 Route Suggestion

- `frontend/pages/campaigns/[campaignId]/eligibility-rules/new.vue`
- `frontend/pages/campaigns/[campaignId]/eligibility-rules/[eligibilityRuleId]/edit.vue`

### 6.3 Form UI Requirements

- create 頁或內嵌 flow 需能顯示 campaign context
- edit 頁需先載入單筆 rule
- 至少包含：
  - loading
  - submit pending
  - validation / backend error
  - success redirect
- 補穩定 selector，例如：
  - `data-testid="eligibility-rule-form"`
  - `data-testid="eligibility-rule-submit"`
  - `data-testid="eligibility-rule-form-error"`

## 7. Acceptance Criteria

- frontend 已新增 `Eligibility Rule` create / edit form
- form 已串接既有 backend create / patch API
- create 成功後可回到 `campaign detail` 並看到新 rule
- edit 成功後可回到 rule detail 或 `campaign detail`
- backend error 可顯示在表單中
- frontend typecheck / build 可通過
- Playwright 已補齊 eligibility form 的最小流程測試
- 本票未實作 dynamic rule builder、matching engine、auto recommendation

## 8. Out of Scope

- 不實作 matching engine
- 不實作複雜規則編譯器
- 不實作布林邏輯樹
- 不實作 dynamic rule builder UI
- 不實作 auto matching
- 不實作推薦 tester
- 不實作 backend schema 重構

## 9. Backend Work Items

本票原則上不擴 backend domain，僅允許極小必要配合：

- 若既有 eligibility CRUD 已足夠，backend 不應新增新 API
- 若表單 flow 發現 validation message 或 contract 缺口，只允許做最小修補

## 10. Frontend Work Items

- 在 `frontend/features/eligibility/` 中補 form helper 或 composable
- 新增 create / edit route
- 從 `campaign detail` 提供新增 / 編輯入口
- 保持 API 呼叫在 feature / service 層
- UI 以簡單表單為主，不做可視化規則編輯器

## 11. Test Items

### 11.1 Frontend Tests

- typecheck
- build

### 11.2 E2E Tests

- create happy path
- create validation / backend error path
- edit happy path
- campaign detail 回寫驗證

### 11.3 Regression Focus

- 既有 eligibility shell 與 rule detail shell 不可被破壞
- campaign detail 既有 data-testid 需維持穩定

## 12. Risk / Notes

- eligibility form 很容易被做成進階規則系統，這不是本票目標
- `os_version_min / os_version_max` 先維持普通字串欄位，避免提早引入版本解析器
- 若需要新增樣式，應先判斷是否有跨頁共用價值；不要把單一表單微調全部塞進全域 SCSS

## 13. 依賴關係（Dependencies）

主要依賴：

- `T013-campaign-eligibility-filter-rules`
- `T018-device-profile-create-and-edit-forms`（非硬依賴，但完成後更有助於端到端操作）

後續可支撐：

- `T020-task-create-and-edit-forms`
