# T064 - Actor-Aware Read Visibility Expansion

## 1. 背景

`T062` 已先收斂 participation-linked task detail 的 read visibility，但對 public beta 來說還不夠。現在仍有部分 summary / detail / queue 會暴露 collaboration footprint 或 owned resource context，需要補上更一致的 actor-aware read 邊界。

## 2. 目標

把 public beta 最關鍵的 read routes 收斂成：

- self-only
- ownership-scoped
- 或明確保留 public read

避免 implementer 在各條 route 各自猜規則。

## 3. 範圍

- 收斂 account-related read visibility
- 收斂 feedback-related read visibility
- 收斂 task / participation / campaign summary 相關的敏感 read visibility
- 對 frontend 補一致的 read-guard error state

## 4. 資料模型建議

本票不新增新資料模型。

但需沿用既有錯誤碼 baseline：

- `missing_actor_context`
- `forbidden_actor_role`
- `ownership_mismatch`

## 5. API 路徑建議

本票至少覆蓋：

- `GET /api/v1/accounts/{account_id}`
- `GET /api/v1/accounts/{account_id}/summary`
- `GET /api/v1/feedback`
- `GET /api/v1/feedback/{feedback_id}`
- `GET /api/v1/tasks/{task_id}`

補充原則：

- `campaign detail` 仍保留 public / tester discovery 能力，不在這張票全面封鎖
- `mine=true` 與 `review_mine=true` 既有 actor-aware query 需保持相容

## 6. 前端頁面 / 路由建議

重點驗證頁面：

- `/accounts/:accountId`
- `/review/feedback`
- `/tasks/:taskId`
- `/tasks/:taskId/feedback/:feedbackId`
- 已存在的 participation request 相關頁面 regression

## 7. Acceptance Criteria

- 帳號 detail / summary 不再可被匿名直接讀取
- tester 只能讀自己的 feedback / collaboration footprint
- developer 只能讀自己 owned campaigns 底下的 feedback / task collaboration context
- 現有 public campaign discovery flow 不被意外封死
- 錯誤碼與 actor-aware mutation guards 對齊

## 8. Out of Scope

- 不做正式 auth
- 不做 organization scope
- 不做 fine-grained permission matrix
- 不改 campaign qualification / participation mutation 行為

## 9. Backend Work Items

- 補 read-side actor / ownership guard
- 明確標記哪些 routes 保持 public read
- 補 API tests 與 service tests

## 10. Frontend Work Items

- 補 read-guard 錯誤提示
- 補空狀態 / error state
- 保持既有 MVP 手測路徑可走

## 11. Test Items

- actor-aware read guard API tests
- self / ownership mismatch / missing actor cases
- feedback queue / detail regression
- account detail / summary regression
- Playwright：task / feedback / account / participation read flows

## 12. Risk / Notes

- 這張票要刻意避免把 campaign discovery 類頁面也全面鎖死
- 若 read visibility 規則需要新增文件說明，請同步更新 `README.md` 與 `NEXT_PHASE_PLAN.md`

## 13. 依賴關係（Dependencies）

主要依賴：

- `T061`
- `T062`

