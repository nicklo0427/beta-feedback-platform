# Next Phase Plan

## Status Note

目前 repo 已完成：

- `T011` 到 `T101`
- MVP 主流程閉環
- role-aware collaboration baseline
- qualification / assignment clarity baseline
- participation-to-assignment bridge baseline
- Alembic schema lifecycle baseline
- public beta ops / QA / rollout evidence baseline
- 全站 UI/UX refresh baseline
- public home、auth pages、登入後 `/dashboard` 與 app shell 分層
- public copy simplification for non-technical users
- in-product terminology simplification and helper copy
- account roles data model / migration baseline
- auth/session roles compatibility baseline
- backend role guard capability baseline
- frontend dual-role registration and account form baseline
- active workspace role switch baseline
- dashboard and workspace route adaptation baseline
- dual-role QA / docs / seed / regression baseline

剛完成的 phase：

- `Dual-Role Account and Workspace Mode`

這代表產品已從「單一角色帳號」推進到「同一帳號可同時發起試玩、也可參與試玩」的 baseline。下一輪正式進入 beta target environment rehearsal 與 post-beta hardening。

## 1. 剛完成的 Phase

### Dual-Role Account and Workspace Mode

已完成：

- 帳號可同時具備 `developer` 與 `tester`
- Account data model 已具備 `roles` 能力集合
- Backend 權限已從 legacy `role` 判斷遷到 `roles` capability helper
- Frontend 已新增 `開發者視角 / 測試者視角` 工作視角切換
- `/dashboard` 與高頻 workspace routes 已適配 active workspace role 與 roles capability
- seed、manual QA、README、launch checklist 已納入 developer-only / tester-only / dual-role 驗收路徑
- legacy `role` 暫時保留相容，避免一次打破既有 API、tests、seed 與舊資料

核心原則：

- `roles` 是新的權限來源
- `role` 是 legacy / primary fallback
- `T095` 已完成資料模型與 migration
- `T097` 已完成 backend role guard capability migration
- `T096` 已完成 auth/register 與 session payload compatibility
- `T098` 已完成 frontend roles type、registration 與 account form baseline
- `T099` 已完成 frontend-only active workspace role switch
- `T100` 已完成 dashboard 與主工作區的 dual-role route adaptation
- `T101` 已完成 QA / docs / seed / regression 收斂
- active workspace role 只影響 frontend UI，不作為 backend 授權依據
- 不在本 phase 引入完整 RBAC framework

## 2. 已完成順序

已完成：

1. `T095 - Account Roles Data Model and Migration`
2. `T096 - Auth and Account API Roles Compatibility`
3. `T097 - Backend Role Guard Refactor for Capabilities`
4. `T098 - Frontend Types, Registration, and Account Forms for Roles`
5. `T099 - Active Workspace Role Switch`
6. `T100 - Dashboard and Workspace Route Adaptation`
7. `T101 - Dual-Role QA, Docs, Seed, and Regression`

## 3. Completed Tickets

### T095 - Account Roles Data Model and Migration

- Status: completed
- 新增 `accounts.roles`
- backfill 既有 `role` 到 `roles = [role]`
- 保留 `role` 作為 legacy / primary fallback
- 建立 roles validation baseline

### T096 - Auth and Account API Roles Compatibility

- Status: completed
- `/auth/register` 優先接受 `roles`
- auth session account payload 帶 `roles`
- 收斂 account API 已落地的 `role` / `roles` precedence 行為
- legacy `role` 仍可傳入
- account response 已在 `T095` 開始同時回傳 `role` 與 `roles`

### T097 - Backend Role Guard Refactor for Capabilities

- Status: completed
- 建立 backend role capability helper
- 將 developer-only / tester-only 判斷改成檢查 `roles`
- dual-role account 可通過兩邊能力檢查
- `forbidden_actor_role` details 增加 `actor_roles`

### T098 - Frontend Types, Registration, and Account Forms for Roles

- Status: completed
- frontend 新增 roles 型別與 formatter
- `/register` 改成身份多選
- account create/edit form 改成身份多選
- query preselect 保留

### T099 - Active Workspace Role Switch

- Status: completed
- app shell 新增 `開發者視角 / 測試者視角` 切換
- active role 存 localStorage
- 單身份帳號不顯示無用切換器
- active role 不送 backend 作授權

### T100 - Dashboard and Workspace Route Adaptation

- Status: completed
- `/dashboard` 依 active workspace role 顯示不同工作區
- dual-role account 不再被要求切換帳號
- route mismatch 文案改成引導切換工作視角
- developer-only / tester-only 頁面改看 capability

### T101 - Dual-Role QA, Docs, Seed, and Regression

- Status: completed
- seed 新增 dual-role、developer-only、tester-only 帳號
- 更新 README / MANUAL_QA / PUBLIC_BETA_LAUNCH_CHECKLIST
- 補 backend migration / API tests
- 補 frontend E2E for dual-role login、workspace switch、developer flow、tester flow

## 4. Next Planned Tickets

### T102 - Target Beta Environment Rehearsal

- Status: active
- 在接近 public beta 的環境設定下跑 migration、session-only auth、health、smoke 與 rollout evidence
- 驗證 `/`、`/login`、`/register`、`/dashboard` 在 target env 可用
- 產出 go / no-go evidence pack

### T103 - Launch Blocker Fix Pass

- Status: active
- 修復 `T102` rehearsal 暴露出的 blocker
- 補對應 backend / frontend tests
- 重跑 smoke、rollout verification 與 regression

### T104 - Beta Onboarding Polish

- Status: active
- 優化首次註冊後 dashboard 與 empty state 引導
- 讓 developer / tester / dual-role 使用者更快知道下一步
- 強化 workspace role switch helper copy

### T105 - Operational Safety Baseline

- Status: active
- 補齊 beta 期間最小 runbook、seed safety、migration / backup 注意事項
- 確認 health、smoke、evidence pack 與故障排查流程可直接使用

## 5. 下一步建議

下一輪建議不要再擴角色模型，而是回到 public beta readiness 的最後現場驗證：

1. 在目標 beta 環境跑一次完整 `public_beta_smoke.py`
2. 跑 `beta_rollout_verification.py` 產出 evidence pack
3. 用 [MANUAL_QA.md](/Users/lowhaijer/projects/beta-feedback-platform/MANUAL_QA.md) 的 dual-role 與主流程清單做人工驗收
4. 把 rehearsal 暴露出的 blocker 拆成 post-beta hardening tickets

## 6. 為什麼這樣排

- 先做資料模型，讓後續 API 和權限有穩定基礎
- 再做 API compatibility，避免 frontend 與 tests 必須一次全部改完
- backend capability guard 應在 frontend workspace switch 前完成，確保安全模型先穩
- frontend registration / forms 再接上新模型
- active workspace role 最後接 dashboard / routes，避免 UI 視角和 backend 權限互相混淆
- 最後用 QA / docs / seed 收斂整個 phase
- 接著先做 target environment rehearsal，避免繼續新增功能卻不知道 beta 環境是否真的可承載
- blocker fix 應接在 rehearsal 後，onboarding polish 和 operational safety 再跟上

## 7. 這一輪先不要做的事

- 不移除 legacy `role`
- 不新增完整 RBAC framework
- 不新增 organization / team model
- 不新增 notification system
- 不新增 auto matching
- 不重做 app navigation IA
- 不做 backend-side i18n
- 不做全站文案大重寫

## 8. 一句話結論

`T095-T101` 已把產品從「單一角色帳號」推進到「同一帳號可同時發起試玩、也可參與試玩」；`T102-T105` 會把重點轉向目標環境 rehearsal、blocker 修復、onboarding polish 與 operational safety。
