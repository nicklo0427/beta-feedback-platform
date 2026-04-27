# T095 - Account Roles Data Model and Migration

Status: completed.

## 1. 背景

目前 account 只有單一 `role` 欄位，使用者一旦被建立成 `developer` 或 `tester`，後續權限、dashboard、workspace 與可見性都會以單一角色判斷。

這和產品正在靠近的使用情境不一致：同一個 vibe coder 可能會發起自己的試玩，也可能想參與別人的網站、App 或小遊戲試用。因此帳號不應被永久鎖成單一角色。

## 2. 目標

建立多身份資料模型 baseline：

- 帳號可同時具備 `developer` 與 `tester`
- `roles` 成為新的能力集合
- legacy `role` 暫時保留作為相容與 primary fallback
- 既有資料可被 migration 安全 backfill

## 3. 範圍

- Account DB schema
- Alembic migration
- account domain schema validation
- account repository / model mapping
- 最小 backend tests

## 4. API / Route / Data 建議

- 新增 `accounts.roles` 欄位，型態建議使用 JSON array
- migration 將既有 `accounts.role` 轉為 `accounts.roles = [accounts.role]`
- `accounts.role` 暫時不移除
- `roles` 僅允許 `developer` / `tester`
- `roles` 至少一個、不允許重複
- `role` 繼續作為 legacy primary role / display fallback

## 5. Backend Work Items

- 更新 SQLAlchemy account entity
- 新增 Alembic migration
- 更新 account record / repository mapping
- 更新 `AccountCreate` / `AccountUpdate` / `AccountDetail` / `AccountListItem`
- 增加 role list normalization / validation helper
- 保持舊單一 `role` 資料可正常讀取

## 6. Frontend Work Items

- 無 runtime work，僅等待後續 ticket 使用新 response shape

## 7. Acceptance Criteria

- migration 後既有 account 都具備 `roles`
- 舊有 `role` 欄位仍存在且可讀
- 新 schema 可表示 `['developer', 'tester']`
- 空 roles、重複 roles、未知 role 會被拒絕
- 既有單身份帳號行為不變

## 8. Out of Scope

- 不移除 legacy `role`
- 不改 auth register 行為
- 不改 frontend registration UI
- 不改 backend role guard
- 不新增 RBAC / permission matrix

## 9. Test Items

- backend validation tests for roles
- migration test for `role` to `roles` backfill
- account create/update schema tests
- account list/detail serialization tests

驗證結果：

- `backend/.venv/bin/python -m pytest`
- `297 passed`

## 10. Risk / Notes

- `role` 和 `roles` 會短期共存，實作時需要明確定義同步策略
- 第一階段不要把所有 `actor.role` 判斷一起替換，避免 migration 與權限重構混在同一票

## 11. Dependencies

- 無
