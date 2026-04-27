# T099 - Active Workspace Role Switch

Status: completed.

## 1. 背景

Dual-role account 可以同時做 developer 與 tester 操作，但如果 app shell 一次顯示所有入口，dashboard 與導航會變得太滿。需要一個 frontend-only 的工作視角，讓同一帳號能在兩種模式間切換。

## 2. 目標

新增 active workspace role switch：

- `開發者視角`
- `測試者視角`
- 只影響 frontend UI
- 不作為 backend 授權依據

## 3. 範圍

- app shell
- dashboard entry context
- current actor/session display
- localStorage persistence
- i18n copy
- E2E coverage

## 4. API / Route / Data 建議

- 不新增 backend API
- localStorage key：`beta-feedback-platform.active-workspace-role`
- value：`developer` 或 `tester`
- 若 account 不具備 stored role，回退到第一個可用 role

## 5. Backend Work Items

- 無

## 6. Frontend Work Items

- 新增 active workspace role composable
- app shell 顯示 role switch
- 單身份帳號可不顯示切換器，只顯示目前身份
- dual-role account 可切換視角
- locale / theme / session change 後維持合理狀態

## 7. Acceptance Criteria

- dual-role account 看到工作視角切換器
- developer-only / tester-only account 不出現無用切換器
- active role reload 後持久化
- 不具備的 stored role 會自動回退
- 切換視角不呼叫 backend mutation

## 8. Out of Scope

- 不改 backend authorization
- 不改 account roles API
- 不重做 navigation IA
- 不改 public homepage

## 9. Test Items

- frontend typecheck
- frontend build
- app shell E2E for role switch visibility
- persistence E2E for active workspace role
- single-role account regression

驗證結果：

- `frontend: npm run typecheck`
- `frontend: npm run build`
- `frontend: npx playwright test tests/e2e/workspace-role-switch.spec.ts --reporter=list --workers=1`
- `frontend role switch E2E: 2 passed`
- `frontend: npx playwright test tests/e2e/ui-shell.spec.ts tests/e2e/auth-shell.spec.ts --reporter=list --workers=1`
- `frontend shell/auth regression: 9 passed`

## 10. Risk / Notes

- active workspace role 是 UI lens，不是安全模型
- 文案要避免讓使用者以為切換視角會修改帳號資料

## 11. Dependencies

- `T098`
