# T059 - Participation Request to Task Traceability and Status Panels

## 1. 背景

當 `T058` 完成後，request 與 task 雖然會被橋接，但 UI 還需要明確顯示：

- 哪一筆 request 已經對應到哪一個 task
- tester 與 developer 現在處於哪個 participation / assignment 階段

## 2. 目標

讓 request、task、workspace 之間的關聯可被看懂。

## 3. 範圍

- 在 participation request list / detail 顯示 linked task 與 assignment context
- 在 task detail 顯示它來自哪一筆 participation request
- tester 的 `/my/participation-requests` 也能看懂 accepted 後是否已被轉成 task

## 4. 資料模型建議

沿用 `T058` 的欄位：

- `linked_task_id`
- `assignment_created_at`

並可補一個 derived 顯示欄位：

- `assignment_status`
  - `not_assigned`
  - `task_created`

## 5. API 路徑建議

優先沿用既有 routes：

- `GET /api/v1/participation-requests?mine=true`
- `GET /api/v1/participation-requests?review_mine=true`
- `GET /api/v1/participation-requests/{request_id}`
- `GET /api/v1/tasks/{task_id}`

必要時只補 derived read-only fields，不新增新 domain endpoint。

## 6. 前端頁面 / 路由建議

- `frontend/pages/my/participation-requests.vue`
- `frontend/pages/review/participation-requests.vue`
- `frontend/pages/review/review-participation-request-[requestId].vue`
- `frontend/pages/tasks/[taskId].vue`

## 7. Acceptance Criteria

- tester 可在 `/my/participation-requests` 看出 request 是否已變成 task
- developer queue / detail 可看見 linked task
- task detail 可反查來源 request
- accepted 但尚未建 task 與已建 task 的狀態有清楚差異

## 8. Out of Scope

- 不做 timeline
- 不做通知
- 不做 request/task 多輪歷史

## 9. Backend Work Items

- participation request list/detail response 補 linkage fields
- task detail response 補 request reference

## 10. Frontend Work Items

- request / task detail panels
- linked task CTA
- tester workspace 狀態顯示

## 11. Test Items

- request detail shows linked task
- my participation requests shows assignment status
- task detail shows request anchor
- regression：review queue / task detail / my requests

## 12. Risk / Notes

- 這張票重點是 traceability，不是再加新 workflow

## 13. 依賴關係（Dependencies）

主要依賴：

- `T058`

