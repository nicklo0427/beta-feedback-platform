# T098 - Frontend Types, Registration, and Account Forms for Roles

Status: completed.

## 1. 背景

Backend 支援 `roles` 後，frontend 仍會用單選 `role` 建立帳號。這會讓新模型無法被使用者看見，也會讓 public homepage 的兩種入口仍像互斥選擇。

## 2. 目標

把 frontend account role 表單改成可選多身份：

- registration 可選 developer / tester / both
- account create/edit 可選 developer / tester / both
- query preselect 保留
- types 與 formatter 支援 roles

## 3. 範圍

- frontend account/auth types
- `/register`
- account create/edit forms
- account list/detail display
- auth/session mocks
- relevant E2E assertions

## 4. API / Route / Data 建議

- frontend payload 優先送 `roles`
- legacy `role` 可由 `roles[0]` 帶上以維持相容
- `/register?role=developer` 預選 developer
- `/register?role=tester` 預選 tester
- 未帶 query 預設選 developer + tester

## 5. Backend Work Items

- 無，依賴 `T096` 的 API compatibility

## 6. Frontend Work Items

- 新增 roles type / formatter
- registration role select 改成 checkbox group
- account form role select 改成 checkbox group
- shell/account labels 從單一角色顯示改成多身份顯示
- 更新 tests mocks 以包含 `roles`

## 7. Acceptance Criteria

- 使用者可註冊成 dual-role account
- 使用者可在 account form 選擇一個或兩個身份
- 至少一個身份必選
- query role preselect 正常
- list/detail/session 顯示可用身份，不再只顯示單一角色

## 8. Out of Scope

- 不新增 workspace role switch
- 不改 dashboard 資料載入策略
- 不改 backend role guards
- 不做全站文案重寫

## 9. Test Items

- frontend typecheck
- frontend build
- auth shell E2E for register roles
- account form E2E or component-level coverage if available
- home CTA query behavior regression

驗證結果：

- `frontend: npm run typecheck`
- `frontend: npm run build`
- `frontend: npx playwright test tests/e2e/auth-shell.spec.ts tests/e2e/accounts-shell.spec.ts --reporter=list --workers=1`
- `frontend E2E: 15 passed`
- `backend: backend/.venv/bin/python -m pytest`
- `backend tests: 306 passed`

## 10. Risk / Notes

- 註冊頁預設選 both 會改變新帳號的初始體驗，文案需清楚表達「之後可用兩種身份」
- frontend mocks 需要同步補 `roles`，避免 session tests 舊資料形狀失真

## 11. Dependencies

- `T096`
