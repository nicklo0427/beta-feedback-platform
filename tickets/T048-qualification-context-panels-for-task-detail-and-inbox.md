# T048 - Qualification Context Panels for Task Detail and Inbox

## 1. 背景

即使 assignment 已完成，tester 與 developer 目前仍不容易理解：

- 這筆 task 是基於哪個 device profile 被指派
- 這筆 assignment 是依哪條資格條件命中
- eligibility rules 後續若變動，這筆 task 是否仍符合

這讓 assignment 的可解釋性仍不足。

## 2. 目標

為 task detail 與 tester inbox 補上 qualification context，讓 assignment 不只是存在，而是可閱讀、可理解。

## 3. 範圍

本票只做 MVP 最小集合：

- task detail 顯示 assignment anchor 與 qualification summary
- `/my/tasks` 顯示最小 qualification context
- 若 campaign eligibility 變動導致 assignment drift，顯示最小 warning

## 4. 資料模型建議

本票優先以 derived context 為主，重用：

- `Task.device_profile_id`
- qualification evaluator baseline
- `EligibilityRule`

至少應能提供：

- `device_profile_id`
- `qualification_status`
- `matched_rule_id`
- `reason_summary`
- `qualification_drift`

## 5. API 路徑建議

可選方案：

- 擴充 `GET /api/v1/tasks/{task_id}`
- 或新增 companion read-only route

若新增 route，建議收斂在：

- `GET /api/v1/tasks/{task_id}/qualification-context`

## 6. 前端頁面 / 路由建議

涉及頁面：

- `frontend/pages/tasks/[taskId].vue`
- `frontend/pages/my/tasks.vue`

可補區塊：

- qualification context panel
- assignment anchor chips
- drift warning state

## 7. Acceptance Criteria

- tester 在 inbox / task detail 能看到 assignment anchor
- qualification summary 至少能顯示 matched baseline 或 fail summary
- 若因 eligibility 更新產生 drift，UI 會有最小提示
- 不破壞既有 feedback submit / edit / review flow

## 8. Out of Scope

- 不做 assignment history
- 不做 full audit timeline
- 不做 notifications
- 不做 candidate re-ranking

## 9. Backend Work Items

- 補 task qualification context baseline
- 若有 drift，提供最小 derived signal
- 補 pytest

## 10. Frontend Work Items

- task detail 補 qualification context panel
- `/my/tasks` 補最小 assignment context 顯示
- 保持 API 呼叫集中在 `features/tasks/` 或相鄰 feature 層

## 11. Test Items

### 11.1 Backend Tests

- qualification context happy path
- drift warning path
- missing task / not found

### 11.2 Frontend Tests

- typecheck
- build

### 11.3 E2E Tests

- task detail qualification context happy path
- tester inbox qualification context
- drift warning display
- regression：feedback flow / inbox quick action

## 12. Risk / Notes

- 這張票不要擴成 audit trail 或 workflow timeline
- drift warning 只需提供最小可讀提示，不需自動重派或阻止既有任務閱讀

## 13. 依賴關係（Dependencies）

主要依賴：

- `T045-campaign-qualification-check-api-and-current-tester-shell`
- `T046-task-assignment-eligibility-preview-and-guardrails`

後續支撐：

- `T049-qualification-aware-demo-seed-and-manual-qa-refresh`
