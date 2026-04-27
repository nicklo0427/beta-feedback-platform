# T046 - Task Assignment Eligibility Preview and Guardrails

## 1. 背景

目前 developer 已能建立與編輯 `Task`，也能指定 `device_profile_id`，但 assignment 還沒有真正與 eligibility 接起來。

這代表：

- developer 可能把不符合資格的 device profile 指派到 task
- frontend 沒有 assignment qualification preview
- backend 也缺少一致的 `assignment_not_eligible` guard

## 2. 目標

為 task assignment 補上 qualification preview 與 guardrails，讓 developer 只能把符合資格的 device profile 指派到 campaign task。

## 3. 範圍

本票只做 MVP 最小集合：

- backend 新增 assignment qualification preview baseline
- backend 在 task create / edit assignment 時檢查 qualification
- frontend task form 顯示 qualification preview
- 不符合時阻止送出並顯示清楚錯誤

## 4. 資料模型建議

本票不新增新 domain，重用：

- `Campaign`
- `EligibilityRule`
- `DeviceProfile`
- `Task.device_profile_id`

preview result 至少應包含：

- `device_profile_id`
- `qualification_status`
- `matched_rule_id`
- `reason_codes`
- `reason_summary`

## 5. API 路徑建議

建議新增：

- `GET /api/v1/campaigns/{campaign_id}/qualification-check?device_profile_id=...`

並在以下 mutation 中納入 guard：

- `POST /api/v1/campaigns/{campaign_id}/tasks`
- `PATCH /api/v1/tasks/{task_id}`

若 assignment 不符合資格，建議回：

- `409 assignment_not_eligible`

## 6. 前端頁面 / 路由建議

涉及頁面：

- `frontend/pages/campaigns/task-new-[campaignId].vue`
- `frontend/pages/tasks/edit-[taskId].vue`

建議行為：

- device profile 選定後即顯示 qualification preview
- 若不符合資格，顯示原因摘要
- 若符合資格，顯示 matched baseline

## 7. Acceptance Criteria

- developer 只能把符合資格的 device profile 指派到 task
- task create / edit form 會顯示 qualification preview
- assignment 不符合時，backend 與 frontend 都會顯示清楚原因
- 既有 task create / edit flow 與 current actor guard 不被破壞

## 8. Out of Scope

- 不做 auto assignment
- 不做 candidate ranking
- 不做 recommendation UI
- 不做 bulk assignment

## 9. Backend Work Items

- 新增 qualification preview route
- 在 task create / edit assignment 接上 eligibility guard
- 補 pytest

## 10. Frontend Work Items

- task create / edit form 補 preview panel
- 顯示 assignment qualification 狀態與原因摘要
- 保持 API 呼叫集中在 `features/tasks/` 與相鄰 feature 層

## 11. Test Items

### 11.1 Backend Tests

- preview happy path
- preview fail path
- task create with eligible assignment
- task create with ineligible assignment
- task edit assignment to ineligible device profile

### 11.2 Frontend Tests

- typecheck
- build

### 11.3 E2E Tests

- task create preview happy path
- task create preview fail path
- task edit preview fail path
- regression：tasks form / tester inbox / feedback flow

## 12. Risk / Notes

- 這張票不要擴成 candidate search 或 recommendation 功能
- qualification preview 與 backend guard 必須共用同一套 semantics，避免 UI 顯示與 backend 驗證不一致

## 13. 依賴關係（Dependencies）

主要依賴：

- `T044-qualification-and-assignment-semantics-draft`
- `T045-campaign-qualification-check-api-and-current-tester-shell`

後續支撐：

- `T048-qualification-context-panels-for-task-detail-and-inbox`
