# T020 - Task Create and Edit Forms

## 1. 背景

`T014` 已完成 `Task` 的最小資料模型、狀態流轉與 shell 顯示，但目前 `Task` 仍缺乏真正可操作的建立與編輯入口。

沒有表單能力時，platform 雖然有 task CRUD 與 `/tasks` shell，實際上仍無法透過 UI 完成：

- 在 campaign 之下建立任務
- 指派到某個 device profile
- 調整 task status
- 驗證 status transition 與 assignment flow

本票的目標，是把 `Task` 從 shell-level 顯示推進到可操作流程，但仍維持 MVP 最小集合，不做批次 assignment 或 reminder。

## 2. 目標

建立 `Task` 的 create / edit form，讓開發者可透過 frontend 建立任務、指派 device profile，並更新允許欄位與狀態。

本票完成後，應具備以下結果：

- 可在 campaign context 下建立 task
- 可從 task detail 進入 edit flow
- status transition 可透過表單觸發，並由 backend 驗證
- task list / detail / form flow 可串起來

## 3. 範圍

本票只做 MVP 最小集合，範圍如下：

- 建立 task create form
- 建立 task edit form
- 串接既有 task create / patch API
- 顯示最小 validation / submit / error / success state
- 補 Playwright form flow 測試

本票可操作欄位與 `T014` 一致：

- `title`
- `instruction_summary`
- `device_profile_id`
- `status`

## 4. 資料模型建議

本票不新增欄位，完全沿用 `T014` 的 task shape。

### 4.1 Form Baseline

- create form 由 route context 提供 `campaign_id`
- create 時 `status` 預設為 `draft`
- edit form 不允許修改 `campaign_id`
- `device_profile_id` 可為空，但進入某些狀態前會被 backend 拒絕

### 4.2 Status Flow Notes

前端可顯示允許的 status 選項，但最終合法性仍以 backend service 為準。

本票不自行重寫 transition engine，只負責尊重既有規則並顯示錯誤。

## 5. API 路徑建議

沿用既有 API：

- `POST /api/v1/campaigns/{campaign_id}/tasks`
- `GET /api/v1/tasks/{task_id}`
- `PATCH /api/v1/tasks/{task_id}`
- `GET /api/v1/tasks?campaign_id=...`

本票不新增新 API。

## 6. 前端頁面 / 路由建議

### 6.1 Feature Placement

- 延用既有：
  - `frontend/features/tasks/`

### 6.2 Route Suggestion

- `frontend/pages/campaigns/[campaignId]/tasks/new.vue`
- `frontend/pages/tasks/[taskId]/edit.vue`

### 6.3 Form UI Requirements

- create 頁需明確顯示 campaign context
- edit 頁需先載入單筆 task
- 至少包含：
  - loading
  - submit pending
  - validation / backend error
  - success redirect
- 補穩定 selector，例如：
  - `data-testid="task-form"`
  - `data-testid="task-submit"`
  - `data-testid="task-status-field"`
  - `data-testid="task-device-profile-field"`

## 7. Acceptance Criteria

- frontend 已新增 task create / edit form
- create form 可在 campaign context 下建立 task
- edit form 可更新允許欄位與 status
- backend 非法狀態轉移錯誤可顯示在表單中
- 成功建立或更新後可回到 task detail 或 list
- frontend typecheck / build 可通過
- Playwright 已補齊 task form 的最小流程測試
- 本票未實作 batch assignment、auto assignment、reminder、notification

## 8. Out of Scope

- 不實作 batch assignment UI
- 不實作 auto assignment
- 不實作 reminder / notification
- 不實作 reward system
- 不實作 SLA 管理
- 不實作 backend status flow 重設計

## 9. Backend Work Items

本票原則上不擴 backend domain，僅允許極小必要配合：

- 若既有 task API 已足夠，backend 不應新增新 endpoint
- 若 form flow 發現 device profile query 或 validation message 有缺口，只允許做最小修補

## 10. Frontend Work Items

- 在 `frontend/features/tasks/` 中補 form helper
- 新增 create / edit route
- 在 `campaign detail` 與 `/tasks` 提供清楚入口
- 保持 API 呼叫在 feature / service 層
- 若需要列出可選 `device_profile_id`，可先使用最小下拉或文字輸入，不做複雜搜尋器

## 11. Test Items

### 11.1 Frontend Tests

- typecheck
- build

### 11.2 E2E Tests

- create happy path
- create validation / backend error path
- edit happy path
- 非法狀態轉移 error path

### 11.3 Regression Focus

- 既有 `/tasks` list / detail shell 不可被破壞
- 既有 campaign detail 內嵌 task section 不可被破壞

## 12. Risk / Notes

- `Task` form 很容易被擴成任務工作台，本票只做最小單筆 create / edit flow
- `device_profile_id` 選擇 UX 應保持簡單，不做搜尋系統或批次分派
- 若新增表單樣式，需先判斷是共用表單樣式還是單頁微調，不要無理由擴大全域 SCSS

## 13. 依賴關係（Dependencies）

主要依賴：

- `T014-task-assignment-and-task-status-flow`
- `T018-device-profile-create-and-edit-forms`

後續可支撐：

- `T021-feedback-submit-and-edit-forms`
- `T022-reputation-baseline-and-summary-metrics`
