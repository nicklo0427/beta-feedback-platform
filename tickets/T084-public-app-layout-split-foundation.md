# T084 - Public/App Layout Split Foundation

## 1. 背景

目前 frontend 已有一套產品化 app shell，但 `首頁 / auth pages / app 內頁` 仍共享太多結構與心智。這讓登入前 public experience 和登入後 workspace 不夠清楚地分層。

如果後續要把 `/` 做成真正的 public landing，並把 `/dashboard` 做成登入後首頁，就需要先建立 layout foundation。

## 2. 目標

建立兩套清楚分層的 frontend layout：

- `public layout`
- `app layout`

並讓：

- `/`
- `/login`
- `/register`

掛到 public layout，而登入後 app 內頁掛到 app layout。

## 3. 範圍

- 建立 public layout 與 app layout 的最小骨架
- 把首頁與 auth pages 從現有 app shell 中抽離
- 保留既有 app shell 能力作為登入後基線
- 不重做首頁內容、不重做 auth form 內容，只先拆 layout

## 4. Layout 建議

### Public Layout

- 用於：
  - `/`
  - `/login`
  - `/register`
- 結構應包含：
  - public header
  - locale switch
  - theme toggle
  - login / register CTA
- 不顯示：
  - app sidebar
  - actor selector
  - app resource navigation

### App Layout

- 用於所有登入後 app pages
- 保留目前：
  - sidebar
  - slim topbar
  - locale / theme / session / actor controls

## 5. API / Route 建議

本票不新增 backend API。

本票也不改 route contract，只做 page-to-layout mapping。

## 6. 前端頁面 / 路由建議

主要修改：

- `frontend/layouts/default.vue`
- 新增 `frontend/layouts/public.vue`
- 視需要新增 `frontend/layouts/app.vue`
- `frontend/pages/index.vue`
- `frontend/pages/login.vue`
- `frontend/pages/register.vue`

## 7. Acceptance Criteria

- `/`、`/login`、`/register` 看不到 app sidebar
- public 頁仍可使用 locale / theme
- app 頁仍保有現有 sidebar/topbar/shell 能力
- route 不變
- backend API 不變

## 8. Out of Scope

- 不重做首頁資訊架構
- 不重做 auth page 視覺
- 不新增 `/dashboard`
- 不改 backend auth/session

## 9. Backend Work Items

- 無新的 runtime 工作

## 10. Frontend Work Items

- 建立 public layout
- 抽離 public header
- 保留 app shell 為登入後 layout
- 將首頁與 auth pages 掛到 public layout
- 補 shell regression 測試

## 11. Test Items

- frontend `typecheck`
- frontend `build`
- `/` 使用 public layout smoke
- `/login`、`/register` 使用 public layout smoke
- app 內頁仍有 sidebar / topbar smoke

## 12. Risk / Notes

- 這張票的關鍵是 layout 分層，不是視覺重做
- 如果在這張票就開始改首頁內容，後續 `T085` 會和 foundation 混在一起

## 13. 依賴關係（Dependencies）

- 無
- 作為 `T085` 到 `T090` 的 phase foundation
