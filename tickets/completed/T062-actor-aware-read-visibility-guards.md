# T062 - Actor-Aware Read Visibility Guards

## 1. 背景

目前 mutation guard 已有 baseline，但 read routes 仍偏寬鬆。當 participation / assignment flow 更完整後，read visibility 也需要逐步收斂。

## 2. 目標

補最小 actor-aware read visibility guards，降低目前任何人可直接讀部分 detail / queue 的風險。

## 3. 範圍

- 收斂 participation request read routes
- 收斂 candidate-related read-only summary
- 維持 MVP 可驗收，但避免過度暴露不屬於 current actor 的資料

## 4. 資料模型建議

本票不新增新資料模型。

## 5. API 路徑建議

優先處理：

- `GET /api/v1/participation-requests/{request_id}`
- candidate / participation summary 相關 routes

必要時可擴到：

- 部分 account summary read visibility

## 6. 前端頁面 / 路由建議

重點驗證頁面：

- `/my/participation-requests`
- `/review/participation-requests`
- `/review/participation-requests/:requestId`

## 7. Acceptance Criteria

- tester 只能讀自己的 participation requests
- developer 只能讀自己 owned campaigns 底下的 request / candidate summaries
- 錯誤碼與 actor-aware mutation guards 對齊

## 8. Out of Scope

- 不做正式 auth
- 不做 organization scope
- 不做 fine-grained permissions matrix

## 9. Backend Work Items

- read guards
- ownership / actor mismatch error baseline

## 10. Frontend Work Items

- 補 read-guard 錯誤提示
- 補空狀態 / error state

## 11. Test Items

- actor-aware read guard API tests
- workspace / detail role mismatch and ownership mismatch E2E

## 12. Risk / Notes

- 這張票應小心不要把 UX 變成全面封鎖；仍要維持目前 MVP 手測路徑可走

## 13. 依賴關係（Dependencies）

主要依賴：

- `T061`

