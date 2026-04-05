# T035 - Feedback Supplement Response and Resubmission

## 1. 背景

`T027` 已讓 developer 可以把 feedback 標成：

- `submitted`
- `needs_more_info`
- `reviewed`

但目前 tester 端還缺少一個明確的「補件 / 回應補充要求」流程。

雖然既有 feedback edit flow 可以更新內容，但缺少：

- 明確的 supplement request 呈現
- resubmission baseline
- 補件後狀態如何回到 `submitted`

## 2. 目標

建立最小的 supplement response / resubmission 流程，讓 tester 在 `needs_more_info` 時，能：

- 清楚看到 developer note
- 更新 feedback
- 將該 feedback 重新送回待 review 狀態

## 3. 範圍

本票只做 MVP 最小集合：

- feedback detail 顯示 supplement request state
- tester 對 `needs_more_info` feedback 做 resubmission
- 最小 resubmission timestamp baseline
- 補 pytest / Playwright

## 4. 資料模型建議

建議在既有 feedback shape 上補：

- `resubmitted_at: string | null`

規則建議：

- 當 feedback 目前為 `needs_more_info`
- 且 tester 更新 feedback 內容後
- backend 自動：
  - 將 `review_status` 改回 `submitted`
  - 設定 `resubmitted_at`

## 5. API 路徑建議

優先重用既有：

- `PATCH /api/v1/feedback/{feedback_id}`
- `GET /api/v1/feedback/{feedback_id}`

本票不新增新 endpoint。

## 6. 前端頁面 / 路由建議

延用既有：

- `frontend/pages/tasks/[taskId]/feedback/[feedbackId].vue`
- `frontend/pages/tasks/feedback-edit-[taskId]-[feedbackId].vue`

detail 頁需補：

- supplement request banner / state
- developer note 顯示強化
- resubmit CTA

## 7. Acceptance Criteria

- `needs_more_info` feedback 在 tester side 可明顯辨識
- tester 可從 detail 直接進入補件 / edit flow
- 成功 resubmit 後：
  - `review_status` 變回 `submitted`
  - `resubmitted_at` 已存在
- developer note 可保留顯示
- backend / frontend / E2E 測試補齊

## 8. Out of Scope

- 不做 threaded conversation
- 不做 notification
- 不做 version diff viewer
- 不做多輪補件歷史 timeline

## 9. Backend Work Items

- feedback schema / service 補 `resubmitted_at`
- 定義 `needs_more_info -> submitted` 的 resubmission rule
- 補 pytest

## 10. Frontend Work Items

- feedback detail 強化 supplement request 呈現
- edit flow 補 resubmit context
- 保持 submit / edit / review 邏輯清楚分工

## 11. Test Items

### 11.1 Backend Tests

- resubmission happy path
- wrong status path
- `resubmitted_at` update

### 11.2 Frontend Tests

- typecheck
- build

### 11.3 E2E Tests

- needs_more_info -> resubmit happy path
- detail banner / note visible
- regression：既有 feedback submit / edit / review flow

## 12. Risk / Notes

- 這張票只補最小補件閉環，不應變成完整對話系統
- `resubmitted_at` 是 workflow timestamp，不等於一般 `updated_at`

## 13. 依賴關係（Dependencies）

主要依賴：

- `T027-feedback-review-status-and-supplement-request`
- `T032-current-actor-context-and-ownership-baseline`

後續支撐：

- `T036-role-aware-dashboard-and-navigation-refresh`
