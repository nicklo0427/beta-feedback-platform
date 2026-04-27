# T069 - Alembic Migration and Schema Lifecycle Baseline

## 1. 背景

`T066` 已把 backend 帶到 database persistence baseline，但目前 schema lifecycle 仍停在 SQLAlchemy `create_all`。這對本地 demo 足夠，對 beta 後的長期維護則不夠，因為 schema 沒有版本化，也沒有正式 upgrade path。

## 2. 目標

把 persistence baseline 升級成 versioned migration baseline，讓 schema 變更可被追蹤、升級、回顧。

## 3. 範圍

- 導入 Alembic
- 建立目前 schema 的初始 migration
- 收斂 local / beta 的 migration 指令與流程
- 更新 deployment / ops 文件

## 4. 資料模型建議

本票不新增新的產品資料模型。

重點是把既有 schema 版本化，至少覆蓋：

- `accounts`
- `actor_sessions`
- `projects`
- `campaigns`
- `campaign_safety`
- `eligibility_rules`
- `device_profiles`
- `tasks`
- `feedback`
- `participation_requests`

## 5. API 路徑建議

本票不新增產品 API。

## 6. 前端頁面 / 路由建議

本票不新增前端頁面。

## 7. Acceptance Criteria

- repo 有可用的 Alembic baseline
- 新資料庫可透過 migration 指令完成初始化
- app 能在 migrated schema 上正常啟動
- README / OPS_RUNBOOK 有 migration 指令與啟動說明

## 8. Out of Scope

- 不做 zero-downtime migration
- 不做 multi-database vendor abstraction
- 不做複雜 rollback automation

## 9. Backend Work Items

- 新增 Alembic config
- 建立 initial revision
- 收斂 `create_all` 與 migration 的責任邊界
- 更新 beta 啟動文件

## 10. Frontend Work Items

- 無新的 runtime 工作

## 11. Test Items

- 空 sqlite DB migration upgrade smoke
- migrated DB app startup smoke
- 既有 backend full pytest regression

## 12. Risk / Notes

- 這張票的目標是建立 baseline，不是一次做完所有未來 migration 問題
- `create_all` 最後要保留在哪些模式，需要跟 `T070` 一起看

## 13. 依賴關係（Dependencies）

主要依賴：

- `T066`

