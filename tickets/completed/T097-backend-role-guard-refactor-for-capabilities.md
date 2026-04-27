# T097 - Backend Role Guard Refactor for Capabilities

Status: completed.

## 1. 背景

目前 backend 大量使用 `actor.role == 'developer'` 或 `actor.role == 'tester'` 做權限判斷。當帳號可以同時具備兩種身份後，單一 `role` 判斷會錯誤阻擋 dual-role account。

## 2. 目標

把 backend 授權判斷改為能力集合：

- developer-only 行為檢查 `roles` 是否包含 `developer`
- tester-only 行為檢查 `roles` 是否包含 `tester`
- dual-role account 可通過兩邊能力檢查
- legacy `role` 僅作 fallback

## 3. 範圍

- projects
- campaigns
- campaign safety
- device profiles
- eligibility
- tasks
- feedback
- participation requests
- reputation
- account summary where role-specific summaries are chosen

## 4. API / Route / Data 建議

- 不新增 route
- `forbidden_actor_role` error code 保留
- error details 增加 `actor_roles`
- `required_role` 保留，避免前端錯誤處理一次重寫

## 5. Backend Work Items

- 建立 helper，例如 `account_has_role(account, AccountRole.DEVELOPER)`
- 建立 require helper，例如 `ensure_account_has_role(actor, AccountRole.TESTER, message=...)`
- 替換直接 `actor.role` 權限判斷
- 更新 account collaboration summary，dual-role account 可同時回傳 developer / tester summaries
- 更新 service tests 與 API tests

## 6. Frontend Work Items

- 無 runtime work，前端錯誤顯示可沿用既有 code

## 7. Acceptance Criteria

- dual-role account 可建立 / 管理自己的 projects 與 campaigns
- dual-role account 可建立 device profiles、查看 eligible campaigns、送 participation requests
- dual-role account 可 review participation requests 與 feedback
- developer-only account 仍無法做 tester-only 操作
- tester-only account 仍無法做 developer-only 操作
- forbidden error details 包含 `actor_roles`

## 8. Out of Scope

- 不新增細顆粒 RBAC
- 不改 ownership 規則
- 不移除 legacy `role`
- 不改 frontend workspace switch

## 9. Test Items

- service tests for dual-role account across developer-only flows
- service tests for dual-role account across tester-only flows
- API tests for forbidden single-role cases
- account summary tests for dual summaries

驗證結果：

- `backend/.venv/bin/python -m pytest`
- `301 passed`

## 10. Risk / Notes

- 這張票會碰到最多 backend module，應避免順手改 payload shape
- 所有權判斷仍應獨立於 role capability

## 11. Dependencies

- `T095`
- `T096`
