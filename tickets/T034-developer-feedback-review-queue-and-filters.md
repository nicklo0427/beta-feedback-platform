# T034 - Developer Feedback Review Queue and Filters

## 1. 背景

目前 `feedback detail` 已有 review panel，但 developer 仍缺少一個 role-aware queue 來管理：

- 哪些 feedback 還沒處理
- 哪些 feedback 需要補充
- 哪些 feedback 已 reviewed

若沒有 queue，review 仍只能從單筆 detail 被動進入，不利於實際協作流程。

## 2. 目標

建立 developer 的最小 feedback review queue，讓 developer 能：

- 查看屬於自己 campaign / project 的 feedback
- 依 `review_status` 做最小篩選
- 快速進入 feedback detail 進行 review

## 3. 範圍

本票只做 MVP 最小集合：

- role-aware feedback list / queue
- `review_status` filters
- campaign / task 基本摘要顯示
- 快速導到 feedback detail

## 4. 資料模型建議

優先重用既有 `Feedback` 欄位與 review baseline：

- `review_status`
- `developer_note`
- `task_id`
- `campaign_id`
- `device_profile_id`
- `submitted_at`

queue 的 ownership 應由：

- current developer actor
- 其所擁有的 project / campaign

推導。

## 5. API 路徑建議

建議補最小 query baseline，例如：

- `GET /api/v1/feedback?mine=true`
- `GET /api/v1/feedback?mine=true&review_status=submitted`
- `GET /api/v1/feedback?mine=true&review_status=needs_more_info`

detail 仍重用：

- `GET /api/v1/feedback/{feedback_id}`
- `PATCH /api/v1/feedback/{feedback_id}`

## 6. 前端頁面 / 路由建議

建議新增：

- `frontend/pages/review/feedback.vue`

頁面至少包含：

- loading
- empty
- error
- filter controls
- list cards

## 7. Acceptance Criteria

- developer 可看到屬於自己的 feedback queue
- 可依 `review_status` 篩選
- queue item 至少顯示：
  - feedback summary
  - campaign / task 基本資訊
  - review status
  - submitted_at
- 可從 queue item 進入 feedback detail
- backend / frontend / E2E 測試補齊

## 8. Out of Scope

- 不做 advanced search
- 不做 saved filters
- 不做 bulk review
- 不做 moderation queue
- 不做 analytics dashboard

## 9. Backend Work Items

- feedback list 補 `mine=true` 與 `review_status` filter baseline
- 驗證 developer ownership 推導
- 補 pytest

## 10. Frontend Work Items

- 新增 developer feedback review queue 頁
- 補 filter UI
- 保持 API / filtering logic 在 feature 層
- 重用既有 detail review flow

## 11. Test Items

### 11.1 Backend Tests

- mine query happy path
- review_status filter
- actor mismatch

### 11.2 Frontend Tests

- typecheck
- build

### 11.3 E2E Tests

- queue happy path
- submitted filter
- needs_more_info filter
- queue -> detail navigation

## 12. Risk / Notes

- 這張票不是搜尋系統
- queue 的目的是補最小 operational flow，不要擴成複雜 triage tool

## 13. 依賴關係（Dependencies）

主要依賴：

- `T032-current-actor-context-and-ownership-baseline`
- `T027-feedback-review-status-and-supplement-request`

後續支撐：

- `T035-feedback-supplement-response-and-resubmission`
- `T036-role-aware-dashboard-and-navigation-refresh`
