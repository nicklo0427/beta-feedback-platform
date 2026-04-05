# T033 - Tester Task Inbox and Assigned Task Actions

## 1. 背景

目前 `Task` 已能建立、指派與更新狀態，但系統還沒有真正的 tester-side inbox。

這代表 tester 雖然理論上可被指派任務，卻還沒有一個 role-aware 入口可以看到：

- 哪些任務是指派給自己的
- 哪些任務需要開始處理
- 哪些任務已提交或已結束

本票的目標，是補上最小 tester inbox，而不是做完整任務工作台。

## 2. 目標

建立 tester 的最小 task inbox 與 assigned-task action baseline，讓 tester 能：

- 看到屬於自己的任務
- 快速進入 task detail
- 對已指派任務做最小狀態推進

## 3. 範圍

本票只做 MVP 最小集合：

- role-aware tester task list
- assigned / in_progress / submitted / closed 的基本分組或篩選
- 最小 quick action，例如：
  - start task：`assigned -> in_progress`
- task detail 與既有 feedback flow 保持串接

## 4. 資料模型建議

本票優先重用既有 `Task` 欄位，不新增新 domain。

必要前提：

- `Task.device_profile_id`
- `DeviceProfile.owner_account_id`
- current actor context

tester inbox 的「我的任務」應由：

- current tester account
- 其所擁有的 device profiles
- 被指派到這些 device profiles 的 tasks

共同推導。

## 5. API 路徑建議

建議補最小 query baseline，例如：

- `GET /api/v1/tasks?mine=true`
- `GET /api/v1/tasks?mine=true&status=assigned`

若既有 `PATCH /api/v1/tasks/{task_id}` 已能處理狀態流轉，應直接重用。

## 6. 前端頁面 / 路由建議

建議新增：

- `frontend/pages/my/tasks.vue`

頁面至少包含：

- loading
- empty
- error
- list grouped by status or filtered by status

可重用既有：

- `/tasks/:taskId`

## 7. Acceptance Criteria

- tester 可在一個 role-aware 頁面看到自己的 tasks
- 至少可區分：
  - `assigned`
  - `in_progress`
  - `submitted`
  - `closed`
- tester 可從 inbox 快速進入 task detail
- tester 可對 `assigned` task 做最小 start action
- backend / frontend / E2E 測試補齊

## 8. Out of Scope

- 不做 notifications
- 不做 reminder
- 不做任務聊天室
- 不做 batch actions
- 不做 acceptance workflow history

## 9. Backend Work Items

- tasks list 補 `mine=true` 或同等 baseline
- 驗證 current actor 與 owned device profiles 的推導邏輯
- 保持既有 status rules
- 補 pytest

## 10. Frontend Work Items

- 新增 tester inbox route
- 新增 role-aware task list UI
- 補最小 quick action
- 保持 API 呼叫集中在 `features/tasks/`

## 11. Test Items

### 11.1 Backend Tests

- mine query happy path
- actor without owned device profiles
- status filter

### 11.2 Frontend Tests

- typecheck
- build

### 11.3 E2E Tests

- tester inbox happy path
- empty state
- assigned -> in_progress quick action
- regression：task detail / feedback flow

## 12. Risk / Notes

- 這張票不要擴成任務排程或提醒系統
- mine query 的定義要清楚依 current actor 與 owned device profiles 推導

## 13. 依賴關係（Dependencies）

主要依賴：

- `T032-current-actor-context-and-ownership-baseline`

後續支撐：

- `T036-role-aware-dashboard-and-navigation-refresh`
