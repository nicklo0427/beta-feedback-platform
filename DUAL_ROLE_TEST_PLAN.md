# T095-T101 Dual-Role Test Plan

## Summary

這份文件整理 `T095-T101` dual-role account 階段的測試方式與預期結果。

測試目標是確認同一個帳號可以同時是開發者與測試者，而且：

- `roles` 是 backend 授權來源
- legacy `role` 只保留作為相容與 primary fallback
- `active workspace role` 只影響 frontend 工作視角
- dual-role 不會破壞既有 developer-only / tester-only 主流程

## Test Matrix

| 測試方式 | 指令 / 路徑 | 預期結果 |
|---|---|---|
| Backend syntax check | `python3 -m py_compile scripts/seed_demo_data.py scripts/public_beta_smoke.py scripts/beta_rollout_verification.py` | 三支腳本都可編譯，沒有 Python syntax error。 |
| Backend full test | `PYTHONPATH=/Users/lowhaijer/projects/beta-feedback-platform/backend ./backend/.venv/bin/pytest -q -p no:cacheprovider` | 全部 backend tests 通過；需覆蓋 account roles validation、auth roles payload、dual-role capability guards、主要 API 權限。 |
| Frontend typecheck | `cd frontend && npm run typecheck` | Vue / Nuxt / TypeScript 型別通過；`roles`、workspace role、dashboard adaptation 沒有型別錯誤。 |
| Frontend build | `cd frontend && npm run build` | Nuxt production build 成功；public/app shell、dashboard、workspace routes 可被正常打包。 |
| Targeted Playwright | `cd frontend && npx playwright test tests/e2e/auth-shell.spec.ts tests/e2e/accounts-shell.spec.ts tests/e2e/workspace-role-switch.spec.ts tests/e2e/dashboard-shell.spec.ts tests/e2e/developer-workspace.spec.ts tests/e2e/my-tasks.spec.ts tests/e2e/eligible-campaigns.spec.ts tests/e2e/review-feedback.spec.ts tests/e2e/review-participation-requests.spec.ts --reporter=list --workers=1` | 核心 dual-role 與主流程 E2E 通過；註冊、帳號表單、workspace role switch、dashboard、developer/tester workspace 都正常。 |
| Full Playwright | `cd frontend && npx playwright test --reporter=list --workers=1` | 全量 frontend E2E 維持通過；dual-role 改動沒有破壞既有 public home、auth、resource list/detail、review flows。 |
| Demo seed 驗收 | `python3 scripts/seed_demo_data.py` | seed output 會列出 developer-only、tester-only、dual-role 三種 account IDs，以及 dual-role project / device profile。 |
| Manual QA | 依 [MANUAL_QA.md](/Users/lowhaijer/projects/beta-feedback-platform/MANUAL_QA.md) | 可手動驗證 dual-role account 看到工作視角切換器，切換後 dashboard 內容改變，重新整理後保留視角。 |
| Public beta checklist | 依 [PUBLIC_BETA_LAUNCH_CHECKLIST.md](/Users/lowhaijer/projects/beta-feedback-platform/PUBLIC_BETA_LAUNCH_CHECKLIST.md) | checklist 裡 dual-role 必驗項目都可勾選：`roles` 是權限來源、legacy `role` 保留相容、single-role mismatch 文案正確。 |
| Smoke verification | `python3 scripts/public_beta_smoke.py` | register / auth me 回傳 `roles`，dual-role payload 保留 `developer` + `tester`，基本 public beta API smoke 通過。 |
| Rollout verification | `python3 scripts/beta_rollout_verification.py` | `/dashboard`、主要 public/app pages、健康檢查與 rollout notes 通過；確認 workspace role 只是 frontend view。 |

## Manual Acceptance Scenarios

- Register 建立 dual-role account 時，表單可同時選 `developer` 與 `tester`，送出後 response/session 內有 `roles: ["developer", "tester"]`。
- `/register?role=developer` 會預選 developer，`/register?role=tester` 會預選 tester，非法 query 不會讓頁面壞掉。
- Dual-role account 登入後，在 app shell 看到 `開發者視角 / 測試者視角` 切換器。
- 切到開發者視角時，`/dashboard` 顯示 developer summary、developer queue、developer CTA。
- 切到測試者視角時，`/dashboard` 顯示 tester summary、tester queue、tester CTA。
- 重新整理後 active workspace role 仍保留，但不會改 backend account `roles`。
- Developer-only account 不會看到 tester-only 能力；tester-only account 不會看到 developer-only 能力，錯誤文案應引導正確身份或工作視角。
- Dual-role account 可以進 developer-only 與 tester-only 主流程頁，不應被要求切換帳號。

## Assumptions

- 這份測試清單對應目前 `T095-T101` 的 dual-role 階段。
- `roles` 是 backend 授權來源；legacy `role` 只保留相容與 primary fallback。
- `active workspace role` 只存在 frontend/localStorage，不送到 backend 當授權依據。
- 這份清單不包含下一階段 target environment rehearsal 的雲端部署驗收。
