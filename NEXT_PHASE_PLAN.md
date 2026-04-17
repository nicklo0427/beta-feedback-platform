# Next Phase Plan

## Status Note

目前 repo 已完成：

- `T011` 到 `T090`
- MVP 主流程閉環
- role-aware collaboration baseline
- qualification / assignment clarity baseline
- participation-to-assignment bridge baseline
- Alembic schema lifecycle baseline
- public beta ops / QA / rollout evidence baseline
- 全站 UI/UX refresh baseline
- `T082` 首頁登入前 / 登入後入口節奏調整
- `T083` 首頁品牌視覺與 supporting visual panels
- `T084` public / app layout split foundation
- `T085` public homepage redesign
- `T086` auth page 與 dashboard entry flow alignment
- `T087` role-aware dashboard home
- `T088` app shell redesign
- `T089` high-frequency app template harmonization
- `T090` responsive / docs / QA refresh baseline

這代表：

- **功能型 MVP 已完成**
- **repo 內的 public beta readiness baseline 已完成**
- **public home、auth pages、登入後 `/dashboard` 與 app shell 已完成分層**
- **下一步最值得先做的是把 dashboard/home/auth/shell 的回歸驗收集中收斂**

## 1. 現在先做哪一件事

如果你的目標是：

- 確認 public home、auth、dashboard、app shell 的 handoff 沒有漏網回歸
- 把 `T088` / `T089` 之後的 shell 與 page template regression 一次收斂
- 把 desktop / mobile / locale / theme / session-only 的驗收補完整

那下一張最合理的票應改為：

- `T091 - Dashboard Entry Flow and Shell Regression Pass`

這張票仍以前端驗收為主，不改 backend API，只做：

- regression 收斂
- responsive smoke 補驗
- locale / theme persistence 補驗
- public/app shell handoff 補驗

## 2. 剛完成的 Phase

剛完成的 phase 為：

- public layout 與 app layout 分離
- public landing / auth pages 重設計
- 新增登入後 `/dashboard`
- app shell 比例、導覽層級、page frame 重設計
- 高頻 app page template 對齊
- responsive / QA / docs refresh

## 3. 已完成 Tickets

### T084 - Public/App Layout Split Foundation

- 建立 `public layout` 與 `app layout`
- `/`、`/login`、`/register` 掛到 public layout
- 其他 app 內頁掛到 app layout
- 保留既有 sidebar + topbar app shell 作為登入後基線

### T085 - Public Homepage Redesign

- 把 `/` 重做成純 public landing
- 保留 `T083` 視覺資產
- 移除首頁上的內部模組入口卡
- 聚焦產品介紹、角色價值、流程與 auth CTA

### T086 - Auth Page and Entry Flow Alignment

- `/login`、`/register` 對齊 public brand language
- auth success redirect 統一進 `/dashboard`
- 已登入進 auth 頁時自動導回 `/dashboard`

### T087 - Dashboard Home Build

- 新增 `/dashboard`
- 成為登入後首頁
- developer / tester 顯示不同 summary、queue、CTA

### T088 - App Shell Redesign

- 重新設計登入後 app shell
- `Dashboard` 成為第一個主導航入口
- sidebar、topbar、page frame 比例與密度收斂

### T089 - Core App Template Harmonization

- 高頻 app 頁面對齊新的 template 節奏
- 聚焦 `/my/*`、`/review/*`、`/projects`、`/campaigns`、`/tasks`
- 收斂 list / detail / workspace / context rail 結構

### T090 - Layout Responsive, QA, and Docs Refresh

- 做 desktop-first responsive pass
- 更新 README / MANUAL_QA / Playwright 驗收
- 驗 public/home/auth/dashboard/app shell 路徑

### T091 - Dashboard Entry Flow and Shell Regression Pass

- 等 `T087` 到 `T090` 穩定後，集中補 dashboard / auth / shell 的 regression
- 收斂 public home → auth → dashboard → app shell 的端到端驗收
- 補 locale / theme persistence 與 responsive smoke

## 4. 建議順序

1. `T091`

## 5. 為什麼這樣排

- `T084` 到 `T090` 已把 layout phase 的實作面收完
- 現在最需要的是把新的 public/app 邊界、dashboard 入口與 shell/page template 變更集中回歸
- `T091` 應該在 UI 結構相對穩定後做，這樣測試才不會一直被重寫

## 6. 這一輪先不要做的事

以下項目仍暫不建議在這個 phase 啟動：

- backend auth redesign
- RBAC framework 擴張
- notification system
- 搜尋 overhaul
- auto matching
- developer candidate ranking
- organization / team model
- locale-prefixed i18n routing
- 全站插畫系統 overhaul
- landing 頁以外的大型 marketing site 擴張

## 7. 一句話結論

`T084` 到 `T090` 已把 public landing、auth pages、登入後 `/dashboard`、app shell 與高頻頁模板拆清楚；下一步最合理的是直接進 `T091`，把這整條入口與 shell regression 一次驗完整。
