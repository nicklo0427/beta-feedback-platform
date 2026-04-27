# Title

T011 - Projects and Campaigns E2E Flows

## Goal

在既有的 Playwright E2E baseline 之上，為 `Project` / `Campaign` shell 補上最小但有價值的端對端流程（End-to-End Flows），覆蓋 list、detail、empty、error、happy path 中最重要的狀態，驗證頁面跳轉、基本資料呈現與頁面穩定性。

## Background

目前專案已有以下基礎：

- frontend 已完成 Nuxt 3 + TypeScript 初始化
- frontend 已完成 Playwright E2E baseline
- frontend 已完成 `projects / campaigns` shell 頁面
- backend 已完成 `projects / campaigns` API 與 pytest baseline
- shell 頁面已提供 `data-testid`，便於穩定選取元素

目前前端頁面仍以 shell-level 為主，尚未進入複雜表單、登入或完整互動流程，因此這一階段最適合補：

- 頁面是否可進入
- 頁面是否能正確顯示 API 回傳資料
- list 到 detail 的導頁是否正常
- empty / error 狀態是否能穩定呈現

本 ticket 應建立可持續擴充的 E2E 寫法，讓後續在不破壞 MVP 簡潔度的前提下，逐步增加更完整的頁面驗證。

前置條件：

- `T008-projects-and-campaigns-frontend-shell` 已完成
- `T010-frontend-e2e-playwright` 已完成

## Scope

- 延續既有 `frontend` 的 Playwright 設定與測試目錄慣例
- 為 `Project` 頁面補上最小 E2E flows
- 為 `Campaign` 頁面補上最小 E2E flows
- 驗證首頁到 `projects` / `campaigns` 的頁面跳轉
- 驗證 list 頁面在 happy path 下可正確顯示資料
- 驗證 detail 頁面在 happy path 下可正確顯示資料
- 驗證至少一個 empty state
- 驗證至少一個 error state
- 驗證 `Project detail` 內嵌的 related campaigns 區塊
- 使用既有 `data-testid` 作為主要 selector
- 測試資料 shape 必須對齊 `API_CONVENTIONS.md` 與 `DATA_MODEL_DRAFT.md`

建議測試策略：

- 以 Playwright route mocking 為主，攔截 frontend 對 backend API 的請求
- mock payload 必須對齊既有 backend contract
- 讓測試聚焦在 shell-level UI flow，而不是 backend 啟動、資料 seed 或跨程序協調

建議優先覆蓋的頁面與流程：

- `/projects`
- `/projects/{project_id}`
- `/campaigns`
- `/campaigns/{campaign_id}`
- `/projects/{project_id}` 中的 related campaigns 區塊

## Out of Scope

- 不做 visual regression
- 不做 screenshot 大量比對
- 不做登入、權限、RBAC
- 不做 create / update / delete 表單流程
- 不做 notification、chat、payment、recommendation 等非 MVP 功能
- 不建立 frontend unit test
- 不建立複雜 test factory framework
- 不導入正式 backend seed / fixture server
- 不驗證完整資料寫入流程

## Acceptance Criteria

- `frontend/tests/e2e/` 下已新增 Project / Campaign shell 專用的 Playwright 測試檔案
- 已覆蓋首頁到 `/projects` 的跳轉流程
- 已覆蓋首頁到 `/campaigns` 的跳轉流程
- 已覆蓋 `Project list` happy path，能驗證 list item 與關鍵欄位顯示
- 已覆蓋 `Project detail` happy path，能驗證 detail 欄位顯示
- 已覆蓋 `Project detail` 內 related campaigns 區塊的基本呈現
- 已覆蓋 `Campaign list` happy path，能驗證 list item 與關鍵欄位顯示
- 已覆蓋 `Campaign detail` happy path，能驗證 detail 欄位顯示
- 已覆蓋至少一個 `empty state` 測試
- 已覆蓋至少一個 `error state` 測試
- 所有新增測試都優先使用既有 `data-testid` 或穩定 heading / link selector
- mock response 的欄位 shape 已對齊 backend contract，不自行發明欄位
- `npm run test:e2e` 可在 frontend 專案中執行通過
- 不新增 visual snapshot、登入流程或表單送出流程

## Deliverables

- `frontend/tests/e2e/` 下的 Project shell E2E 測試
- `frontend/tests/e2e/` 下的 Campaign shell E2E 測試
- 最小必要的 mock response helper 或測試資料常數（若有需要）
- 一套可供後續擴充的 shell-level E2E 寫法

## Notes / Constraints

- 必須延續 `T010` 已建立的 Playwright baseline，不另起一套測試結構
- 必須遵守 `ARCHITECTURE.md` 的 frontend 結構與命名原則
- 必須遵守 `API_CONVENTIONS.md` 的 response / error baseline
- 必須遵守 `DATA_MODEL_DRAFT.md` 的 `Project / Campaign` 欄位 shape 與責任邊界
- 建議預設使用 Playwright route mocking，而不是要求 backend 一起啟動；原因是本 ticket 重點在 shell-level E2E，不是前後端整合驗證
- 若需建立 mock payload，欄位至少應包含：
  - Project list / detail：`id`、`name`、`description`、`created_at`、`updated_at`
  - Campaign list / detail：`id`、`project_id`、`name`、`description`、`target_platforms`、`version_label`、`status`、`created_at`、`updated_at`
- error mock 必須對齊既有 baseline：
  - `code`
  - `message`
  - `details`
- 測試檔命名應清楚表達目標，例如：
  - `projects-shell.spec.ts`
  - `campaigns-shell.spec.ts`
- 若需要建立共用 helper，應保持最小且只服務 E2E 測試，不要提早抽成大型測試框架
- 斷言應優先驗證：
  - 頁面是否成功進入
  - 關鍵資料是否出現在預期位置
  - empty / error state 是否可見
  - list 到 detail 的導頁是否正確
- 不要因為補測試而大改產品頁面；只有在 coverage 被既有 selector 阻塞時，才允許最小幅度補 selector
