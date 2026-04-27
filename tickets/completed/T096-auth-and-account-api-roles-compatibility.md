# T096 - Auth and Account API Roles Compatibility

Status: completed.

## 1. 背景

`T095` 已讓 account data model、account create/update schema、account list/detail response 具備 `roles` 能力集合，但 auth register、auth session response 與既有前端仍主要使用單一 `role`。需要一張相容票，把 auth 與 session 層補齊成同時支援新舊 payload，讓後續 frontend 可以逐步遷移。

## 2. 目標

讓 auth / session API 支援 dual-role payload，同時不破壞既有 client：

- register 優先接受 `roles`
- legacy `role` 仍可傳入
- auth response 同時回傳 `account.role` 與 `account.roles`
- auth session account payload 帶 `roles`

## 3. 範圍

- `/auth/register`
- `/auth/login`
- `/auth/me`
- auth session response schema
- backend API tests
- account API compatibility review for `role` / `roles` precedence already introduced in `T095`

## 4. API / Route / Data 建議

- `roles?: AccountRole[]`
- `role?: AccountRole`
- 若 request 同時帶 `roles` 與 `role`，以 `roles` 為準
- 若 request 只帶 `role`，backend normalize 成 `roles = [role]`
- account response 已在 `T095` 開始包含：
  - `role`
  - `roles`
- auth session response 在本票後也應包含：
  - `account.role`
  - `account.roles`
- `role` 預設使用 `roles[0]`，或沿用既有 primary role 欄位

## 5. Backend Work Items

- 更新 auth schemas
- 更新 register service normalization
- 更新 session serialization
- 補 account API compatibility regression，確認 `T095` 已落地的 list/detail/create/update shape 沒退回單一 `role`
- 更新 auth API tests 以覆蓋 legacy `role` 與新 `roles`

## 6. Frontend Work Items

- 只需視測試 mock 是否需要補 `roles`
- 不在本票改 UI

## 7. Acceptance Criteria

- legacy register payload `{ role: 'developer' }` 仍可成功
- new register payload `{ roles: ['developer', 'tester'] }` 可成功
- account response 持續同時包含 `role` 與 `roles`
- auth session response 同時包含 `account.role` 與 `account.roles`
- invalid roles payload 回傳 validation error

## 8. Out of Scope

- 不改 frontend register form
- 不改 dashboard role behavior
- 不重構 backend role guards
- 不移除 `role`

## 9. Test Items

- backend account API tests
- backend auth API tests
- auth service tests
- validation tests for payload precedence

驗證結果：

- `backend/.venv/bin/pytest tests/test_auth_api.py tests/service/test_auth_service.py tests/validation/test_auth_validation.py tests/test_accounts_api.py tests/service/test_accounts_service.py tests/validation/test_accounts_validation.py`
- `targeted backend tests: 43 passed`
- `backend/.venv/bin/python -m pytest`
- `full backend tests: 306 passed`

## 10. Risk / Notes

- 這張票是相容層，應保持改動收斂
- 後續 `T097` 才把 backend 授權來源從 `role` 遷到 `roles`

## 11. Dependencies

- `T095`
