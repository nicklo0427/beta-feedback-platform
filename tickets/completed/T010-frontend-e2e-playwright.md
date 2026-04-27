# Title

T010 - Frontend E2E Playwright

## Goal

在 `frontend/` 導入 Playwright End-to-End（E2E）測試基線，建立最小 `playwright.config`、測試目錄與可執行的首頁 / Project / Campaign shell 測試，讓 frontend 後續能以真實瀏覽器流程驗證頁面可用性與基本資料流。

## Background

目前 frontend 已完成 Nuxt 3 + TypeScript 初始化，但尚未建立正式自動化測試基線。隨著後續會逐步建立：

- 專案首頁
- Project / Campaign shell
- frontend 與 backend 的接軌流程

單靠手動開頁檢查很快會出現回歸風險，因此需要先建立一套簡潔、可直接執行的 E2E baseline。

現階段 frontend 測試方向以 E2E 為主，原因如下：

- frontend 目前以頁面骨架與流程驗證優先
- 尚未有足夠穩定的元件層與 shared UI 可支撐 unit test 優先策略
- 真實瀏覽器流程更能驗證 Nuxt 啟動、routing、頁面顯示與 mock / placeholder data 行為

本 ticket 不負責導入過度複雜的測試框架組合，也不在這次補 frontend unit test。

前置條件與依賴：

- `T002-frontend-init` 已完成
- 首頁 E2E 可直接基於目前 Nuxt 初始化結果建立
- `Project / Campaign shell` E2E 依賴 `T008-projects-and-campaigns-frontend-shell`
- 若 shell 已接真實 backend，則可選擇額外參考 `T007-projects-and-campaigns-backend-crud`；若仍為 mock data，則不強制依賴 `T007`

## Scope

- 在 `frontend/` 導入 Playwright
- 建立最小 `playwright.config` 與測試目錄
- 定義 E2E 測試檔案命名與放置規則
- 建立首頁（home / landing）最小 E2E 測試
- 建立 Project / Campaign shell 的最小 E2E 測試
- 定義本地啟動與 Playwright 執行的 baseline 流程
- 補最小等待策略與 selector 使用原則，降低 flaky test 機率

## Out of Scope

- 不導入 frontend unit test 或 component test
- 不導入 visual regression
- 不建立 screenshot baseline approval 流程
- 不擴張到 auth、RBAC、登入、通知、聊天、支付、推薦系統
- 不建立跨瀏覽器 matrix 的複雜並行策略
- 不建立過度複雜的 test data orchestration

## Acceptance Criteria

- `frontend/` 已可使用 Playwright 執行 E2E 測試
- 已存在最小 `playwright.config` 與 E2E 測試目錄
- 已定義首頁 E2E baseline，至少驗證：
  - 頁面可成功載入
  - 關鍵標題或主要內容可見
- 已定義 Project / Campaign shell 的最小 E2E baseline，至少驗證：
  - 對應頁面或主要 shell 區塊可載入
  - list / detail 基本區塊、empty / loading / placeholder 狀態中的至少一種可被驗證
- E2E 執行方式與本地啟動方式已清楚定義
- 不依賴 visual snapshot 才能完成驗證
- 本 ticket 不引入 frontend unit test

## Deliverables

- `frontend/` 內的 Playwright 基礎設定
- 最小 E2E 測試目錄
- 首頁 E2E 測試
- Project / Campaign shell E2E 測試
- 一套可供後續頁面與流程延續使用的 E2E 慣例

## Notes / Constraints

- 必須遵守 `ARCHITECTURE.md` 的 frontend 結構與命名原則
- 建議採簡潔結構，例如：
  - `frontend/playwright.config.ts`
  - `frontend/tests/e2e/`
- 若目前 shell 頁面尚未存在，應先完成 `T008`，再補對應 E2E；不要在這張票中為了測試而反向發明 UI
- 首頁 E2E 可先落地，作為 Playwright 接入驗證
- Project / Campaign shell 的 E2E 建議優先驗證：
  - 進入頁面成功
  - 關鍵 heading / 區塊存在
  - mock / placeholder data 或 empty state 呈現正常
  - 基本路由跳轉正常
- selector 原則：
  - 優先使用角色（role）、heading、label、data-testid 等穩定 selector
  - 避免依賴脆弱的樣式 class 或過深 DOM 結構
- 執行原則：
  - 優先用 Playwright 啟動或掛接本地 Nuxt dev server
  - base URL、port 與等待策略應集中於 config，不散落在各測試檔
- 命名原則：
  - test file：`home.spec.ts`、`projects.spec.ts`、`campaigns.spec.ts` 等
  - test case：`should ...` 或 `renders ...` 風格，保持語意清楚即可
- 本 ticket 的目標是建立可持續擴充的 E2E baseline，不是建立完整 QA 自動化平台

