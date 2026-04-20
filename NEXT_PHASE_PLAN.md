# Next Phase Plan

## Status Note

目前 repo 已完成：

- `T011` 到 `T094`
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
- `T091` dashboard entry flow / shell regression pass
- `T092` public homepage conversion and product-flow polish
- `T093` public copy simplification for non-technical users
- `T094` in-product terminology simplification and helper copy

這代表：

- **功能型 MVP 已完成**
- **repo 內的 public beta readiness baseline 已完成**
- **public home、auth pages、登入後 `/dashboard` 與 app shell 已完成分層**
- **下一步最值得先做的是決定要往 public trust/visual 深化，還是全站 i18n / terminology 擴張**

## 1. 現在先做哪一件事

如果你的目標是：

- 讓 public landing 更像可對外展示的正式產品首頁
- 把目前只覆蓋到主流程的 i18n / terminology 再往更多頁面擴張
- 或開始補 launch 前最後一段 public beta hardening / release decision

那下一個 phase 比較合理的方向會是三選一：

- `Public landing trust / proof / visual system` 深化
- `Full-site i18n and terminology expansion`
- `Public beta rollout decision and post-beta hardening`

目前不需要再重做 `T093 / T094` 的方向，因為這一批已完成：

- public 面的人話化重寫
- app 內主流程頁的術語降噪
- CTA、state copy、helper text 與 i18n 對齊

## 2. 剛完成的 Phase

剛完成的 phase 為：

- public layout 與 app layout 分離
- public landing / auth pages 重設計
- 新增登入後 `/dashboard`
- app shell 比例、導覽層級、page frame 重設計
- 高頻 app page template 對齊
- responsive / QA / docs refresh
- public homepage conversion 與 product-flow polish
- public copy simplification for non-technical users
- in-product terminology simplification and helper copy

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

### T092 - Public Homepage Conversion and Product-Flow Polish

- 把首頁首屏改成 conversion-first 的雙目標 hero
- 把 public landing section 重排成 trust / flow / role value / final CTA
- 升級首頁品牌視覺與 `zh-TW / en` 文案
- 保持 route 與 backend API 不變

### T093 - Public Copy Simplification for Non-Technical Users

- 把 `/`、`/login`、`/register` 與 public header 的語言改成沒有開發背景也看得懂的產品語言
- 降低 `campaign`、`qualification`、`participation request` 等術語在登入前的理解成本
- 對齊首頁、auth pages 與 public CTA 的 `zh-TW / en` 文案

### T094 - In-Product Terminology Simplification and Helper Copy

- 把 `/dashboard`、`/my/*`、`/review/*` 與高頻 detail 頁的主要標題、CTA、狀態文案改得更口語
- 透過 helper copy 保留流程精準度，但降低理解門檻
- 對齊主流程頁的狀態 label、錯誤訊息與中英文 i18n

## 4. 下一個 Phase

下一個 phase 建議先在下面三條裡選一條：

- `Public Landing Trust and Visual Proof`
- `Full-Site i18n and Terminology Expansion`
- `Public Beta Launch Decision and Hardening`

目標不再是回頭收同一批 copy，而是決定要：

- 繼續強化 public 面的信任感、案例感與品牌視覺
- 把目前已完成的 i18n / 非技術詞彙基線擴到剩下的 resource/detail/form 頁
- 或回到 launch / rollout 角度，準備真正的 public beta 發佈決策

## 5. 建議順序

1. 決定下一輪是偏 `public marketing polish`、`full-site product language`，還是 `launch hardening`
2. 再依選定方向拆成 `T095+`

## 6. 為什麼這樣排

- `T093 / T094` 已先把對非技術背景最重要的理解門檻降下來
- 下一步如果還留在同一層 copy 微調，收益會開始變小
- 比較值得的是選擇一條新的主線，避免 roadmap 只剩零碎修飾

## 7. 這一輪先不要做的事

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
- backend-side i18n
- 全站一次性文案大重寫
- 資料模型重新命名

## 8. 一句話結論

`T084` 到 `T094` 已把 public landing、auth pages、登入後 `/dashboard`、app shell 與高頻主流程頁的語言收斂到非技術背景也較容易理解；下一步該做的不是重做同一批文案，而是決定要往 `public trust`、`full-site i18n`，還是 `launch hardening` 前進。
