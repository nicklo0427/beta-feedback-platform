# T040 - Actor-Aware Task and Feedback Action Guards

## 1. 背景

目前 `Task` 與 `Feedback` 已能做：

- create / edit
- status transition
- tester inbox
- developer review queue
- supplement / resubmission

但這些 action 還沒有完整驗證：

- 是否由正確角色觸發
- 是否真的屬於當前 actor

這會讓 role-aware collaboration 的最後一段還不夠可信。

## 2. 目標

為 task 與 feedback 的核心 action 補上 actor-aware guardrails，讓 developer / tester 的互動流程有一致的角色與 ownership 邊界。

## 3. 範圍

本票只做 MVP 最小集合：

- developer 建立 / 編輯 task 的 actor-aware guard
- tester `assigned -> in_progress` quick action 的 actor-aware guard
- tester submit / edit / resubmit feedback 的 actor-aware guard
- developer review feedback 的 actor-aware guard
- frontend 補最小錯誤處理

## 4. 資料模型建議

本票不新增新 domain。

需重用：

- `Task.device_profile_id`
- `DeviceProfile.owner_account_id`
- `Project.owner_account_id`
- `Feedback.review_status`
- `Feedback.resubmitted_at`

## 5. API 路徑建議

需納入 guardrails 的 routes：

- `POST /api/v1/campaigns/{campaign_id}/tasks`
- `PATCH /api/v1/tasks/{task_id}`
- `POST /api/v1/tasks/{task_id}/feedback`
- `PATCH /api/v1/feedback/{feedback_id}`

其中至少要明確限制：

- developer 才能建立 / 編輯 task
- tester 只能推進自己被指派的 task
- tester 只能提交 / 更新屬於自己 assignment anchor 的 feedback
- developer 只能 review 自己擁有 campaign / project 下的 feedback

## 6. 前端頁面 / 路由建議

涉及頁面：

- `frontend/pages/campaigns/task-new-[campaignId].vue`
- `frontend/pages/tasks/edit-[taskId].vue`
- `frontend/pages/my/tasks.vue`
- `frontend/pages/tasks/feedback-new-[taskId].vue`
- `frontend/pages/tasks/feedback-edit-[taskId]-[feedbackId].vue`
- `frontend/pages/tasks/[taskId]/feedback/[feedbackId].vue`
- `frontend/pages/review/feedback.vue`

## 7. Acceptance Criteria

- developer 不能操作不屬於自己的 task mutation
- tester 不能操作不屬於自己的 task / feedback action
- developer 不能 review 不屬於自己的 feedback
- missing actor / role mismatch / ownership mismatch 都會回一致錯誤
- frontend 會顯示可理解的錯誤狀態
- 現有 tester inbox / developer review queue 不被破壞

## 8. Out of Scope

- 不做 formal approval flow
- 不做 notification
- 不做 threaded discussion
- 不做 reviewer assignment system

## 9. Backend Work Items

- 補 task mutation 的 actor-aware guards
- 補 feedback submit / edit / review / resubmit 的 actor-aware guards
- 補 pytest

## 10. Frontend Work Items

- 所有相關 action 帶 current actor header
- 顯示 role mismatch / ownership mismatch 錯誤
- 保持既有 shell 與 form flow 不被破壞

## 11. Test Items

### 11.1 Backend Tests

- developer task mutation happy path
- tester task quick action happy path
- feedback submit / edit / review / resubmit happy path
- missing actor / role mismatch / ownership mismatch

### 11.2 Frontend Tests

- typecheck
- build

### 11.3 E2E Tests

- tester inbox quick action guarded happy path
- tester feedback submit / resubmit guarded path
- developer review guarded path
- regression：task / feedback / review queue

## 12. Risk / Notes

- 這張票不要擴成 auth system
- 只補目前已經存在的 action guard

## 13. 依賴關係（Dependencies）

主要依賴：

- `T038-actor-aware-workflow-guardrails-draft`

後續支撐：

- `T042-role-aware-demo-seed-and-owned-fixtures`
- `T043-account-collaboration-summary-and-owned-resource-panels`
