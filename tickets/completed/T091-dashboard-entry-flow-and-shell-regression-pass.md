# T091 - Dashboard Entry Flow and Shell Regression Pass

## 1. 背景

`T086` 先把 auth success redirect、已登入 auth guard 與最小 `/dashboard` handoff route 接起來；接下來等 `T087` 到 `T090` 逐步完成 dashboard、app shell redesign、page template 對齊與 responsive pass 後，還需要一張專門的 regression / QA 票，把這整條入口路徑驗完整。

如果沒有把這張票獨立出來，後面很容易出現：

- public home 與 app shell 節奏已改，但 Playwright assertion 還停在舊首頁心智
- login / register / dashboard / app shell 的 handoff 各自有測，但缺少一條端到端回歸
- responsive 與 locale / theme persistence 在 public/app 之間的切換沒有被系統化驗證

## 2. 目標

建立一張專門的測試與驗收票，等 dashboard 與 shell phase 穩定後，集中完成：

- auth entry flow 回歸
- public home → auth → dashboard → app shell 的端到端驗證
- responsive / locale / theme / session-only 路徑驗收

## 3. 範圍

- 補強 Playwright E2E
- 更新必要的 smoke / shell regression
- 更新 MANUAL_QA 中與 public home / auth / dashboard 相關的驗收步驟
- 整理測試覆蓋缺口與 release 前 blocking checks
- 收斂 `T088` app shell redesign 後的新導航、topbar、page frame 與 public/app 邊界回歸
- 收斂 `T089` 高頻 workspace / queue / list pages 套用新 template 後的 header、summary cards、card grid 與 breadcrumb regression

## 4. 測試主題建議

### Auth / Entry Flow

- unauthenticated `/dashboard` -> `/login`
- login success -> `/dashboard`
- register success -> `/dashboard`
- already-signed-in `/login` -> `/dashboard`
- already-signed-in `/register` -> `/dashboard`

### Public / App Layout Boundary

- `/` 永遠是 public landing
- public layout 不顯示 app sidebar
- authenticated public header 可進 `/dashboard`
- app pages 不再出現 public auth CTA header

### Dashboard States

- developer dashboard summary / CTA
- tester dashboard summary / CTA
- session bootstrap from `/auth/me` 後正確落到 dashboard
- session-only mode 下 dashboard handoff 正常

### Shell / Persistence

- locale 在 public layout 與 app layout 間切換後仍持久化
- theme 在 public layout 與 app layout 間切換後仍持久化
- mobile nav / drawer 在 `/dashboard` 與 app 內頁都可操作
- `Dashboard` 是 app shell 第一個主導航，且 active state 正常
- app shell 側欄顯示 workspace context card、session role 與返回 public home 的入口
- app topbar 在 `/dashboard`、`/review/*`、`/projects` 這類頁面都呈現正確的 eyebrow / title / description hierarchy
- `CurrentActorSelector`、locale、theme controls 在 shell redesign 後仍可同時使用，不互相擠壓或消失
- public layout 與 app layout 之間切換後，不會出現混用 public CTA 與 app sidebar 的狀況

### Workspace / List Template Harmonization

- `/my/projects`、`/my/campaigns`、`/my/tasks` 使用一致的 `Dashboard` breadcrumb、summary cards 與 card grid 節奏
- `/my/eligible-campaigns`、`/my/participation-requests` 維持 tester workflow 的同一套 workspace template
- `/review/feedback`、`/review/participation-requests` 的 queue pages 使用一致的 filters / summary / list rhythm
- `/projects`、`/campaigns`、`/tasks` 的 resource list pages 使用一致的 header、actions、summary 與 grid layout
- `resource-state` error / loading / empty blocks 在新的 template 裡仍可正確撐滿 grid 寬度

### Responsive

- desktop `1280px`
- mobile `390px`
- public home、login、register、dashboard、至少一個 app list page、至少一個 detail page 不破版
- public header 的 auth CTA、app shell 的 topbar controls、dashboard summary cards 在手機寬度下仍可操作

## 5. API / Route 建議

不新增 API。

重點驗收 route：

- `/`
- `/login`
- `/register`
- `/dashboard`
- `/my/projects`
- `/my/tasks`
- `/review/feedback`
- `/tasks/:taskId`

## 6. 前端頁面 / 測試檔建議

優先補或調整：

- `frontend/tests/e2e/home.spec.ts`
- `frontend/tests/e2e/auth-shell.spec.ts`
- `frontend/tests/e2e/auth-session-only.spec.ts`
- `frontend/tests/e2e/ui-shell.spec.ts`
- `frontend/tests/e2e/smoke.spec.ts`
- `frontend/tests/e2e/dashboard-shell.spec.ts`
- 視需要補 `frontend/tests/e2e/review-participation-requests.spec.ts`
- 視需要補 `frontend/tests/e2e/projects-shell.spec.ts`
- 視需要補 `frontend/tests/e2e/my-tasks.spec.ts`
- 視需要補 `frontend/tests/e2e/eligible-campaigns.spec.ts`
- 視需要補 `frontend/tests/e2e/tasks-shell.spec.ts`
- 視需要補 `frontend/tests/e2e/review-feedback.spec.ts`

## 7. Acceptance Criteria

- public home / auth / dashboard / app shell 的 handoff 有完整 E2E 覆蓋
- session-only 與 fallback-enabled 環境都至少有一條核心回歸
- locale / theme persistence 在 public 與 app 兩套 layout 間有驗收
- responsive smoke 已寫進自動化或 manual QA
- 文件與測試現況一致

## 8. Out of Scope

- 不新增 backend API
- 不重做 auth flow 本身
- 不做 visual diff snapshot system 導入

## 9. Backend Work Items

- 無新的 runtime 工作

## 10. Frontend Work Items

- 補 dashboard entry flow regression
- 補 public/app shell 邊界 regression
- 補 `T088` 側欄層級、workspace context card、public-home link regression
- 補 `T088` topbar heading hierarchy 與 shell controls regression
- 補 `T089` workspace summary cards 與 breadcrumb regression
- 補 `T089` resource list card-grid / empty-state regression
- 補 responsive smoke
- 補 locale / theme persistence regression
- 補 README / MANUAL_QA 與實際 shell path 的一致性檢查

## 11. Test Items

- frontend `typecheck`
- frontend `build`
- targeted Playwright regression
- full frontend E2E
- manual QA refresh for public home / auth / dashboard
- shell redesign targeted coverage：
  - dashboard first-nav / active state
  - workspace context card copy
  - public-home footer link
  - topbar page description hierarchy
  - mobile drawer after redesign
- template harmonization targeted coverage：
  - dashboard breadcrumb on app pages
  - workspace summary cards
  - queue filters + summary alignment
  - resource list summary cards
  - grid layout keeps error/empty states full width
- docs / QA targeted coverage：
  - `/` public landing expectations
  - `/dashboard` auth gate expectations
  - MANUAL_QA step order matches new public/auth/dashboard flow

## 12. Risk / Notes

- 這張票應放在 `T087` 到 `T090` 之後做，否則測試會在 layout 尚未穩定前一直被重寫
- 目標是收斂 dashboard phase 的驗收，而不是在每一張 UI 票裡分散補測

## 13. 依賴關係（Dependencies）

- `T086`
- `T087`
- `T088`
- `T089`
- `T090`
