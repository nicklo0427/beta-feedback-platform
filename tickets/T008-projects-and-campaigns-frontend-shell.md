# Title

T008 - Projects and Campaigns Frontend Shell

## Goal

在 `frontend/` 中建立 Project / Campaign 的最小頁面骨架與資料流入口，先用 mock data 或 placeholder API 完成基礎 shell，讓後續可逐步接上真實 backend，而不在這次進入完整 UI 設計系統或登入流程。

## Background

目前 frontend 已完成 Nuxt 3 + TypeScript 初始化，具備最小首頁與後續可擴充骨架。下一步需要把第一批核心模組轉成實際可承接的前端頁面結構，而 Project / Campaign 是目前最合理的首批功能入口。

由於 backend 的正式資料層與 auth 尚未完成，本 ticket 可以使用 mock data 或 placeholder API，但必須保持：

- 與 `T005` 的 API baseline 對齊
- 與 `T006` 的 schema draft 對齊
- 與 `ARCHITECTURE.md` 的 frontend 結構規範對齊

本 ticket 依賴：

- `T005-api-and-project-conventions`
- `T006-projects-and-campaigns-schema-draft`

與 `T007-projects-and-campaigns-backend-crud` 的關係：

- 可先以 mock data / placeholder API 進行 shell 建立
- 若 `T007` 已完成，應優先設計成可平滑切換到真實 API

## Scope

- 在 `frontend/` 中建立 Project / Campaign 的最小頁面骨架
- 建立對應的 feature 結構或最小必要目錄，前提是不建立大量空殼
- 建立 Project list / detail 的最小頁面 shell
- 建立 Campaign list / detail 或嵌入式區塊的最小頁面 shell
- 建立最小型別、API 呼叫占位層或 mock data 入口
- 建立 loading / empty / basic error placeholder 狀態
- 保持頁面可在未登入前提下作為開發骨架驗證

## Out of Scope

- 不實作登入、註冊、權限、使用者角色切換
- 不建立完整設計系統或大型元件庫
- 不實作複雜互動，例如拖拉排序、批次操作、多人協作
- 不實作 Task、Feedback、Reputation、Safety Layer 頁面
- 不接支付、聊天、通知、推薦系統
- 不進入像素級 UI polish

## Acceptance Criteria

- `frontend/` 已新增 Project / Campaign 的最小頁面骨架
- 目錄分層符合 `ARCHITECTURE.md`，但沒有為了完整感建立大量空資料夾
- 頁面命名、feature 命名、型別命名可對齊 `T006` 的 schema draft
- 資料取得方式已可支援 mock data 或 placeholder API，且後續可切換到 `T007` 的真實 backend
- 至少具備 list / detail 的基本展示結構
- 已包含 loading / empty / basic error 的最小狀態處理
- 不包含登入與任何非 MVP 系統功能

## Deliverables

- Project 頁面骨架
- Campaign 頁面骨架
- 一組最小前端型別與資料入口
- 一套可逐步切換為真實 API 的 shell 架構

## Notes / Constraints

- 必須遵守 `ARCHITECTURE.md` 的 frontend 結構與命名規則
- 必須以前置 ticket `T005` 與 `T006` 為準
- 若 `T007` 尚未完成，可先使用 mock data / placeholder API，但資料形狀必須與未來 backend contract 對齊
- 不要把 API 呼叫直接散落在 `pages/` 中，應保留清楚的 feature / service 邊界
- 不要預先建立整套 `accounts`、`tasks`、`feedback` 等空 feature
- 視覺呈現以「能清楚承接資料與流程」為主，不追求完整品牌化設計
- 若需建立共用元件，必須有明確重用理由，否則應優先留在 Project / Campaign feature 內
