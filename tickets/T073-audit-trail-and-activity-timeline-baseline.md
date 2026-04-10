# T073 - Audit Trail and Activity Timeline Baseline

## 1. 背景

現在 participation request、task bridge、feedback review、resubmission、未來的 task resolution 都已經有關鍵操作，但系統還缺少可回顧的事件時間線。

## 2. 目標

建立最小 audit trail / activity timeline baseline，讓營運與 beta support 看得懂「事情是怎麼發生的」。

## 3. 範圍

- backend activity event baseline
- request / task / feedback detail timeline
- 不同 actor 的關鍵行為記錄

## 4. 資料模型建議

建議新增最小 event model：

- `id`
- `entity_type`
- `entity_id`
- `event_type`
- `actor_account_id`
- `summary`
- `created_at`

事件至少涵蓋：

- participation request created
- participation request accepted / declined / withdrawn
- task created from participation request
- feedback submitted / reviewed / needs_more_info / resubmitted
- task resolved

## 5. API 路徑建議

可選兩種做法：

- detail response 直接夾帶 timeline
- 或補 companion read-only endpoint

優先建議：

- `GET /api/v1/participation-requests/{request_id}/timeline`
- `GET /api/v1/tasks/{task_id}/timeline`
- `GET /api/v1/feedback/{feedback_id}/timeline`

## 6. 前端頁面 / 路由建議

沿用既有 detail 頁：

- `/review/participation-requests/:requestId`
- `/tasks/:taskId`
- `/tasks/:taskId/feedback/:feedbackId`

## 7. Acceptance Criteria

- request / task / feedback detail 至少有一條可讀時間線
- 使用者可看見關鍵 event 與 actor
- audit trail 不會暴露不該看的 actor / entity

## 8. Out of Scope

- 不做完整 diff viewer
- 不做 analytics dashboard
- 不做 export / external audit package

## 9. Backend Work Items

- 建 event persistence baseline
- 在既有關鍵 service action 寫入 events
- 補 read-side timeline API

## 10. Frontend Work Items

- detail timeline panel
- loading / empty / error state

## 11. Test Items

- backend event creation regression
- timeline read API tests
- frontend detail timeline smoke

## 12. Risk / Notes

- 這張票會跨多個 domain，範圍很容易膨脹
- MVP 版只需要可讀、可信，不需要做得像完整 audit system

## 13. 依賴關係（Dependencies）

主要依賴：

- `T072`

