# T100 - Dashboard and Workspace Route Adaptation

Status: completed.

## 1. 背景

新增 active workspace role 後，dashboard 與主工作區頁面需要從「帳號是什麼 role」改成「目前工作視角是什麼」。同時 dual-role account 不應再看到要求切換帳號的錯誤文案。

## 2. 目標

讓登入後主流程適配 dual-role account：

- `/dashboard` 根據 active workspace role 顯示 developer 或 tester summary
- route mismatch 文案改成引導切換工作視角
- capability 仍以 account roles 判斷
- single-role account 行為維持清楚

## 3. 範圍

- `/dashboard`
- `/my/projects`
- `/my/campaigns`
- `/my/tasks`
- `/my/eligible-campaigns`
- `/my/participation-requests`
- `/review/feedback`
- `/review/participation-requests`
- high-frequency role mismatch states

## 4. API / Route / Data 建議

- 不改 route contract
- 不新增 backend API
- frontend 使用 `roles` 判斷 capability
- frontend 使用 active workspace role 決定 dashboard default view

## 5. Backend Work Items

- 無，依賴 `T097` 完成 capability guard

## 6. Frontend Work Items

- dashboard data key 改用 active workspace role
- dashboard data fetch 根據 active workspace role 分流
- route guard / mismatch state 改查 account roles
- role mismatch copy 改為「切換工作視角」或「此帳號尚未啟用此身份」
- 更新 i18n copy

## 7. Acceptance Criteria

- dual-role account 可在同一登入 session 切換 developer / tester dashboard
- dual-role account 可進 developer-only 與 tester-only 頁面
- single-role account 缺少 capability 時仍看到清楚提示
- 不再要求 dual-role account 切換帳號
- public/auth/dashboard handoff 不破

## 8. Out of Scope

- 不新增混合 dashboard
- 不重做 app navigation IA
- 不新增 backend endpoint
- 不改 ownership visibility

## 9. Test Items

- dashboard shell E2E for dual-role switch
- `/my/*` role capability regression
- `/review/*` role capability regression
- frontend typecheck
- frontend build
- targeted Playwright for developer and tester views

## 10. Risk / Notes

- dashboard 目前直接依 `sessionAccount.role` 分流，這是本票最重要的替換點
- route mismatch copy 要避免把 capability 與 active view 混成同一件事

## 11. Dependencies

- `T097`
- `T099`
