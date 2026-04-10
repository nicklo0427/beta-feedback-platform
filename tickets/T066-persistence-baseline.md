# T066 - Persistence Baseline

## 1. 背景

目前 backend 仍是 in-memory repository。這足以支撐內部驗收，但 public beta 不能接受 restart 後整批資料消失。若沒有正式 persistence，前面的 qualification / participation / task flow 都無法進入可公開試用的狀態。

## 2. 目標

把核心產品資料移到正式 persistence，讓 public beta 至少具備：

- restart 後資料可保留
- migration / schema 可管理
- seed 可重跑

## 3. 範圍

- 導入正式資料庫與 migration baseline
- 為核心 domain 提供持久化 repository
- 保持既有 service / API contract 儘量不變

## 4. 資料模型建議

本票至少覆蓋：

- `accounts`
- `projects`
- `campaigns`
- `campaign_safety`
- `eligibility_rules`
- `device_profiles`
- `tasks`
- `feedback`
- `participation_requests`

建議採用：

- PostgreSQL
- Alembic migrations

## 5. API 路徑建議

本票不新增 public API。

重點是保持既有 routes 相容，避免 public beta 前端要同步大改。

## 6. 前端頁面 / 路由建議

本票原則上不新增前端頁面。

前端應只需要承接：

- data persistence 不再因 backend restart 消失
- 少量錯誤訊息或 loading 行為調整

## 7. Acceptance Criteria

- 核心資料在 backend restart 後仍可保留
- migration 可建立完整 schema
- 現有 seed workflow 可在 persistence mode 跑通
- 既有 frontend contract 不因 persistence 轉換而破壞
- 全量 backend / frontend 測試仍可通過

## 8. Out of Scope

- 不做 analytics warehouse
- 不做 read replica
- 不做 multi-tenant schema
- 不做大規模 domain redesign

## 9. Backend Work Items

- DB connection / settings
- migration baseline
- SQL-backed repositories
- repository wiring / env selection
- seed compatibility

## 10. Frontend Work Items

- 原則上無大規模 runtime 變更
- 如 contract 需最小調整，應控制在兼容範圍內

## 11. Test Items

- migration smoke test
- repository persistence tests
- restart persistence smoke
- seed against database mode
- regression：existing API / Playwright suite

## 12. Risk / Notes

- 這張票風險最高，建議刻意限制在「資料持久化」本身
- 不要順手重寫 service layer 或全面改 schema
- 若保留 in-memory dev mode，必須文件化並避免 production 誤用

## 13. 依賴關係（Dependencies）

主要依賴：

- `T065`

