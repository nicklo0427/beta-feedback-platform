# T058 - Participation Accepted Request to Task Assignment Bridge

## 1. 背景

目前 participation request 可以被 `accepted`，但流程會停在 request 狀態本身，尚未真正進入 task execution。

這會造成：

- developer 已完成 review，但還要手動回到 campaign / task flow 重新建立任務
- tester 看不出 accepted request 的下一步
- request 與 task 之間沒有正式 bridge

## 2. 目標

建立 accepted participation request 到 task assignment 的最小橋接流程。

## 3. 範圍

本票聚焦在：

- backend 支援從 accepted participation request 建立 task
- participation request 補最小 linkage 欄位
- frontend 在 developer review queue 與 request detail 提供 `Create task from request` 入口
- 建立成功後可直接導向 task detail

## 4. 資料模型建議

Participation request 建議補最小 linkage 欄位：

- `linked_task_id: string | null`
- `assignment_created_at: string | null`

限制：

- 只有 `accepted` request 可建立 task
- 同一筆 request 只允許建立一筆 linked task

## 5. API 路徑建議

建議新增：

- `POST /api/v1/participation-requests/{request_id}/tasks`

行為建議：

- 使用 request 內既有的 `campaign_id`
- 使用 request 內既有的 `device_profile_id`
- 由 developer 提供 task 最小表單欄位，例如：
  - `title`
  - `instruction_summary`
  - `status`

## 6. 前端頁面 / 路由建議

沿用既有頁面：

- `frontend/pages/review/participation-requests.vue`
- `frontend/pages/review/review-participation-request-[requestId].vue`

可視需要新增一個輕量 form route：

- `frontend/pages/review/participation-request-task-new-[requestId].vue`

## 7. Acceptance Criteria

- developer 可從 accepted participation request 建立 task
- 建立出的 task 自動帶入 request 的 campaign / device profile
- 同一 request 不能重複建立多筆 linked task
- 建立成功後 request 會記住 `linked_task_id`
- frontend 可從 queue 或 detail 進入這個 flow

## 8. Out of Scope

- 不做 auto assignment
- 不做 batch create
- 不做通知
- 不做 request 與 task 的多對多關聯

## 9. Backend Work Items

- participation request schema / service / API 補 linkage 欄位
- 新增 bridge endpoint
- actor / ownership guard：
  - 必須是 developer
  - 必須擁有該 campaign
  - request 必須已 accepted

## 10. Frontend Work Items

- 新增 minimal create-task-from-request flow
- 在 participation review queue / detail 補入口
- 成功後導向新 task detail

## 11. Test Items

- accepted request -> create task happy path
- pending / declined / withdrawn request 不可建立 task
- duplicate linked task guard
- regression：existing task create / edit flow

## 12. Risk / Notes

- 這張票的目的是 bridge，不是重做 task form
- 若 task form 已有欄位可重用，應優先共用既有 form logic

## 13. 依賴關係（Dependencies）

主要依賴：

- `T054`
- `T055`
- `T056`

