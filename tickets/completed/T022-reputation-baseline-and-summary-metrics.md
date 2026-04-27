# T022 - Reputation Baseline and Summary Metrics

## 1. 背景

PRD 已明確把 `Reputation` 列為核心模組，但目前 repo 雖然已完成 task 與 feedback 流程，仍缺乏最小可用的信譽基礎。

如果現在直接做完整雙向評分系統，會遇到兩個問題：

- 目前尚未有完整帳號與 ownership model
- 現有資料仍以 `campaign / device_profile / task / feedback` 為主，不適合硬做複雜 score engine

因此，下一步較合理的做法不是直接做 rating platform，而是先建立基於現有資料可推導的 `Reputation Summary Baseline`，讓產品能逐步表達：

- tester-side 的提交可靠度
- campaign-side 的合作完成度

## 2. 目標

建立 `Reputation` 的 MVP 初版 summary metrics，先以 read-only derived metrics 形式提供 tester-side 與 campaign-side 的最小信譽資訊。

本票完成後，應具備以下結果：

- backend 可提供 reputation summary API
- frontend 可在 `device profile detail` 與 `campaign detail` 顯示 summary shell
- derived metrics 可被測試與驗證
- 後續若帳號系統完成，可在此基礎上映射到正式 user reputation

## 3. 範圍

本票只做 MVP 最小集合，範圍如下：

- 建立 read-only `reputation` summary API
- tester-side reputation anchor 採 `device_profile_id`
- campaign-side collaboration summary anchor 採 `campaign_id`
- frontend 補 summary shell
- 補 backend pytest 與 frontend Playwright 測試

本票只做 derived metrics，不做手動寫入型 reputation record。

## 4. 資料模型建議

### 4.1 Tester Reputation Summary

- `device_profile_id`: `string`
- `tasks_assigned_count`: `number`
- `tasks_submitted_count`: `number`
- `feedback_submitted_count`: `number`
- `submission_rate`: `number`，0..1
- `last_feedback_at`: `string | null`
- `updated_at`: `string (ISO 8601)`

### 4.2 Campaign Collaboration Summary

- `campaign_id`: `string`
- `tasks_total_count`: `number`
- `tasks_closed_count`: `number`
- `feedback_received_count`: `number`
- `closure_rate`: `number`，0..1
- `last_feedback_at`: `string | null`
- `updated_at`: `string (ISO 8601)`

### 4.3 Derivation Rules

- `tasks_assigned_count`：`device_profile_id` 相符且狀態進入 `assigned` 之後的 task 數
- `tasks_submitted_count`：狀態為 `submitted` 或 `closed` 且曾有 submission 的 task 數
- `feedback_submitted_count`：屬於該 `device_profile_id` 的 feedback 數
- `submission_rate = tasks_submitted_count / tasks_assigned_count`
- `tasks_total_count`：屬於該 `campaign_id` 的 task 數
- `tasks_closed_count`：屬於該 `campaign_id` 且狀態為 `closed` 的 task 數
- `feedback_received_count`：屬於該 `campaign_id` 的 feedback 數
- `closure_rate = tasks_closed_count / tasks_total_count`

本票中若分母為 0，rate 一律回 `0`

## 5. API 路徑建議

- `GET /api/v1/device-profiles/{device_profile_id}/reputation`
- `GET /api/v1/campaigns/{campaign_id}/reputation`

本票不做 create / patch / delete。

API baseline：

- 成功時直接回 summary resource
- 若 anchor resource 不存在，回 `resource_not_found`

## 6. 前端頁面 / 路由建議

### 6.1 Feature Placement

- `frontend/features/reputation/`
  - `types.ts`
  - `api.ts`

### 6.2 UI Placement

- `frontend/pages/device-profiles/[deviceProfileId].vue`
- `frontend/pages/campaigns/[campaignId].vue`

### 6.3 UI Shell Requirements

- `device profile detail` 顯示 tester-side reputation summary
- `campaign detail` 顯示 collaboration summary
- 至少顯示：
  - count metrics
  - rate metrics
  - `last_feedback_at`
- 提供：
  - loading state
  - empty / zero state
  - basic error state
- 補穩定 selector，例如：
  - `data-testid="device-profile-reputation-panel"`
  - `data-testid="campaign-reputation-panel"`

## 7. Acceptance Criteria

- backend 已新增 `reputation` 模組或等效 summary 實作
- reputation summary 可由既有 `tasks / feedback` 資料推導
- API path、error baseline 符合 `API_CONVENTIONS.md`
- frontend 已可在 `device profile detail` 與 `campaign detail` 顯示 summary shell
- frontend API 呼叫未散落在 `pages/` 中
- backend pytest 已補齊 derived metrics 與 error path 測試
- frontend Playwright 已補齊 summary shell-level E2E
- 本票未實作公開排行、badge、複雜 score engine、爭議處理流程

## 8. Out of Scope

- 不實作公開排行
- 不實作 badge / tier system
- 不實作複雜 score formula
- 不實作 dispute / arbitration
- 不實作完整雙向個人評分
- 不實作帳號系統
- 不實作大規模 analytics dashboard

## 9. Backend Work Items

- 在 `backend/app/modules/` 下新增 `reputation` 模組或等效 derived summary 結構
- 建立 read-only API
- 由既有 `tasks / feedback` repository 或 service 推導 summary
- 驗證 `device_profile_id` 或 `campaign_id` anchor 存在
- 保持 in-memory 策略，不新增正式 persistence 設計

## 10. Frontend Work Items

- 在 `frontend/features/reputation/` 下建立最小必要檔案
- 擴充 `device profile detail` 與 `campaign detail`
- 補 summary panel，不建立獨立 reputation dashboard
- UI 以簡單數字摘要與說明為主，不做進階分析頁

## 11. Test Items

### 11.1 Backend Tests

- derived metrics correctness
- zero-state metrics
- anchor not found error
- summary timestamp / last activity derivation

### 11.2 Frontend Tests

- typecheck
- build

### 11.3 E2E Tests

- `device profile detail` reputation happy path
- `campaign detail` reputation happy path
- zero-state / empty-state
- error state

## 12. Risk / Notes

- `Reputation` 第一版是 derived summary，不是完整評分系統
- 目前使用 `device_profile_id` 與 `campaign_id` 作為 anchor 是 MVP 務實做法，未來帳號系統完成後可能要重映射
- rate 與 count 命名必須清楚，避免 UI 被誤解成官方品質背書

## 13. 依賴關係（Dependencies）

主要依賴：

- `T016-safety-and-reputation-mvp-schema-draft`
- `T018-device-profile-create-and-edit-forms`
- `T020-task-create-and-edit-forms`
- `T021-feedback-submit-and-edit-forms`

可部分依賴但非硬前提：

- `T017-campaign-safety-source-labeling-and-risk-flags`
