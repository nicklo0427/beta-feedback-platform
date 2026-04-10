# T072 - Task Resolution and Outcome Workflow Baseline

## 1. 背景

目前 task 可以被建立、指派、收到 feedback，也能在 qualification / participation 流程中被追蹤，但 developer 對 task 的最終處理結果還沒有正式表達方式。

## 2. 目標

補上 task resolution baseline，讓 developer 能對任務做正式收尾，tester 也能看見結果。

## 3. 範圍

- task outcome / resolution 欄位
- developer-side resolution action
- tester-side resolution display
- 與 feedback / participation traceability 共存

## 4. 資料模型建議

建議補最小欄位：

- `resolution_outcome`
- `resolution_note`
- `resolved_at`
- `resolved_by_account_id`

建議 outcome 最小集合：

- `confirmed_issue`
- `needs_follow_up`
- `not_reproducible`
- `cancelled`

## 5. API 路徑建議

沿用既有：

- `PATCH /api/v1/tasks/{task_id}`

必要時可補 companion action route，但優先用既有 task patch。

## 6. 前端頁面 / 路由建議

沿用既有：

- `/tasks/:taskId`
- `/my/tasks`

## 7. Acceptance Criteria

- developer 可在 task detail 對任務做 resolution
- tester 可在 task detail / inbox 看見 resolution outcome
- resolution 不會破壞既有 feedback flow
- linked participation request context 仍可共存

## 8. Out of Scope

- 不做 bug tracker integration
- 不做 issue sync
- 不做 SLA / assignee workload

## 9. Backend Work Items

- 補 task resolution schema / service / API
- 定義 allowed transitions 與最小 guardrails

## 10. Frontend Work Items

- task detail resolution panel
- tester inbox resolution summary

## 11. Test Items

- backend resolution happy path / invalid transition
- frontend task detail resolution flow
- Playwright regression：task detail / inbox / feedback

## 12. Risk / Notes

- resolution outcome 是 task-level 運營結果，不是正式 bug lifecycle
- 需要小心不要和既有 `status = closed` 混成同一件事

## 13. 依賴關係（Dependencies）

主要依賴：

- `T059`
- `T060`

