# T055 - Developer Participation Review Queue and Decision Actions

## 1. 背景

`T054` 完成後，tester 可以送 participation request，但 developer 仍需要一個最小 queue 來查看並處理這些 requests。

## 2. 目標

建立 developer 端的 participation review queue，讓 campaign owner 能 accept / decline requests。

## 3. 範圍

本票只做最小集合：

- backend list review queue
- backend patch accept / decline
- frontend `/review/participation-requests`
- tester 端 request status 可同步更新

## 4. 資料模型建議

延用 `T053` status baseline：

- `pending`
- `accepted`
- `declined`
- `withdrawn`

本票聚焦：

- developer 只可處理 `pending`
- accept / decline 時可填 `decision_note`

## 5. API 路徑建議

- `GET /api/v1/participation-requests?review_mine=true`
- `PATCH /api/v1/participation-requests/{request_id}`

## 6. 前端頁面 / 路由建議

涉及：

- `frontend/pages/review/participation-requests.vue`
- `frontend/pages/my/participation-requests.vue`

## 7. Acceptance Criteria

- developer 可在 review queue 看到自己 owned campaigns 的 pending requests
- developer 可 accept / decline request
- tester 在自己的 request list 中能看到更新後狀態
- tester actor 不可進行 review actions

## 8. Out of Scope

- 不做 auto task creation
- 不做 chat / threaded discussion
- 不做 notifications
- 不做 bulk actions

## 9. Backend Work Items

- review queue query
- patch accept / decline
- role / ownership guard

## 10. Frontend Work Items

- review queue page
- accept / decline inline action
- tester request list status refresh

## 11. Test Items

### 11.1 Backend

- review queue happy path
- ownership guard
- accept / decline happy path
- invalid status transition

### 11.2 Frontend

- review queue load / empty / error / happy path
- accept / decline action
- tester side status reflection

## 12. Risk / Notes

- 這張票不要直接把 accepted request 轉成 task
- 先讓 decision 與 assignment 解耦，保持 MVP 範圍小

## 13. 依賴關係（Dependencies）

主要依賴：

- `T054-tester-campaign-participation-request-flow`

後續支撐：

- `T056-participation-request-detail-and-candidate-snapshot-panels`

