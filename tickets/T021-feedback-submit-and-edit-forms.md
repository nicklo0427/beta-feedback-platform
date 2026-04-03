# T021 - Feedback Submit and Edit Forms

## 1. 背景

`T015` 已完成 `Feedback` 的最小資料模型、task 關聯與 shell 顯示，但目前使用者仍無法透過 UI 真正提交或修改 feedback。

這使得目前的 MVP 閉環雖然在資料結構上完整，但在產品操作上仍缺最後一哩：

- 無法在 task 底下送出結構化回饋
- 無法從 frontend 驗證 feedback 與 task flow 的真實操作
- 無法讓後續 reputation 建立在實際提交流程之上

因此，本票的目標是補齊 `Feedback` submit / edit form，讓 MVP 主流程真正可被操作。

## 2. 目標

建立 `Feedback` 的 submit / edit form，讓 tester 可在 task context 下提交或修改結構化回饋。

本票完成後，應具備以下結果：

- 可在 task 底下建立 feedback
- 可在 feedback detail 進入 edit flow
- frontend 表單可串接既有 backend feedback CRUD
- 提交成功後可回到 task detail feedback section 或 feedback detail

## 3. 範圍

本票只做 MVP 最小集合，範圍如下：

- 建立 feedback submit form
- 建立 feedback edit form
- 串接既有 nested create 與 patch API
- 顯示最小 validation / submit / error / success state
- 補 Playwright form flow 測試

本票可操作欄位與 `T015` 一致：

- `summary`
- `rating`
- `severity`
- `category`
- `reproduction_steps`
- `expected_result`
- `actual_result`
- `note`

## 4. 資料模型建議

本票不新增欄位，完全沿用 `T015` 的 feedback shape。

### 4.1 Form Baseline

- create form 由 route context 提供 `task_id`
- `campaign_id` 與 `device_profile_id` 不可由前端手填
- edit form 不允許修改 `task_id`
- `summary`、`severity`、`category` 為最小必要欄位

### 4.2 Validation Notes

- `rating` 若提供，應限制在 `1..5`
- `severity` 與 `category` 採固定選項
- optional text 欄位允許為空
- 真正 validation 仍以 backend 為準

## 5. API 路徑建議

沿用既有 API：

- `POST /api/v1/tasks/{task_id}/feedback`
- `GET /api/v1/feedback/{feedback_id}`
- `PATCH /api/v1/feedback/{feedback_id}`
- `GET /api/v1/tasks/{task_id}/feedback`

本票不新增新 API。

## 6. 前端頁面 / 路由建議

### 6.1 Feature Placement

- 延用既有：
  - `frontend/features/feedback/`

### 6.2 Route Suggestion

- `frontend/pages/tasks/[taskId]/feedback/new.vue`
- `frontend/pages/tasks/[taskId]/feedback/[feedbackId]/edit.vue`

### 6.3 Form UI Requirements

- create 頁需顯示 task context
- edit 頁需先載入單筆 feedback
- 至少包含：
  - loading
  - submit pending
  - validation / backend error
  - success redirect
- 補穩定 selector，例如：
  - `data-testid="feedback-form"`
  - `data-testid="feedback-submit"`
  - `data-testid="feedback-severity-field"`
  - `data-testid="feedback-category-field"`

## 7. Acceptance Criteria

- frontend 已新增 feedback submit / edit form
- create form 可在 task context 下提交 feedback
- edit form 可更新允許欄位
- 成功提交後可回到 task detail feedback section 或 feedback detail
- backend error 與 validation error 可顯示在表單中
- frontend typecheck / build 可通過
- Playwright 已補齊 feedback form 的最小流程測試
- 本票未實作附件上傳、rich text、AI summary、duplicate detection、moderation workflow

## 8. Out of Scope

- 不實作附件上傳
- 不實作 screenshot / video 管理
- 不實作 rich text editor
- 不實作 AI summary
- 不實作 duplicate detection
- 不實作 moderation workflow
- 不實作 backend schema 重構

## 9. Backend Work Items

本票原則上不擴 backend domain，僅允許極小必要配合：

- 若既有 feedback API 已足夠，backend 不應新增新 endpoint
- 若 submit / edit flow 遇到 validation message 或 state coupling 缺口，只允許最小修補

## 10. Frontend Work Items

- 在 `frontend/features/feedback/` 中補 form helper
- 新增 submit / edit route
- 從 `task detail` 與 `feedback detail` 提供清楚入口
- 保持 API 呼叫在 feature / service 層
- UI 先以清楚表單欄位與結果導向為主，不做 editor 級體驗

## 11. Test Items

### 11.1 Frontend Tests

- typecheck
- build

### 11.2 E2E Tests

- submit happy path
- submit validation / backend error path
- edit happy path
- task detail feedback section 回寫驗證

### 11.3 Regression Focus

- 既有 task detail 內嵌 feedback shell 不可被破壞
- nested feedback detail shell 不可被破壞

## 12. Risk / Notes

- feedback form 很容易擴成完整 bug report workspace，本票只做最小 submit / edit
- `rating` 是輔助欄位，不應在 UI 上喧賓奪主
- 若新增樣式，需先判斷是否有跨頁共用價值；本票不應為單一表單引入新的全域設計語言

## 13. 依賴關係（Dependencies）

主要依賴：

- `T015-structured-feedback-submission`
- `T020-task-create-and-edit-forms`

後續可支撐：

- `T022-reputation-baseline-and-summary-metrics`
- `T023-homepage-ia-and-overview-shell-refresh`
