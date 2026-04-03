# Title

T006 - Projects and Campaigns Schema Draft

## Goal

定義 Project / Campaign 在 MVP 階段的最小資料欄位草案，為後續 backend CRUD 與 frontend shell 提供一致的資料模型基礎，並將欄位草案落成可直接引用的資料模型文件，但不進入完整 migration、權限與商業規則細節。

## Background

依照 PRD，目前 Project / Campaign 是核心模組之一：

- Project 用於承載產品或測試主體
- Campaign 用於承載特定階段、版本或目標的測試活動

目前專案已完成 frontend / backend 初始化，且已有 `ARCHITECTURE.md` 可作為結構依據。進入 CRUD 與頁面骨架前，應先定義最小資料欄位草案，避免：

- backend 與 frontend 各自想像資料結構
- Project 與 Campaign 的責任邊界重疊
- 後續 API contract 與 UI 欄位不一致

本 ticket 依賴 `T005-api-and-project-conventions`。本 ticket 的輸出將作為 `T007-projects-and-campaigns-backend-crud` 與 `T008-projects-and-campaigns-frontend-shell` 的直接輸入。

由於 `T005` 已將 API 共識落成 `API_CONVENTIONS.md`，本 ticket 應沿用其 request / response 命名與欄位風格，並將資料模型草案集中寫入 `DATA_MODEL_DRAFT.md`。

## Scope

- 定義 Project 的 MVP 最小欄位草案
- 定義 Campaign 的 MVP 最小欄位草案
- 定義 Project 與 Campaign 之間的基本關聯
- 定義 list / detail / create / update 情境下需要的主要欄位
- 區分必填欄位、選填欄位與系統產生欄位
- 說明欄位用途與預期型別
- 說明哪些欄位是 MVP 必要，哪些欄位先不納入
- 將 Project / Campaign 欄位草案落成根目錄文件 `DATA_MODEL_DRAFT.md`
- 明確記錄有歧義欄位的歸屬判斷理由

## Out of Scope

- 不建立實際資料庫 migration
- 不實作 SQLAlchemy models 或完整 ORM 關聯
- 不定義 auth、ownership、role-based access control
- 不定義完整狀態機或審批流程
- 不擴張到 Task、Feedback、Reputation、Safety Layer 詳細欄位
- 不設計過細的商業規則與驗證規則
- 不建立 backend CRUD
- 不建立 frontend 頁面骨架

## Acceptance Criteria

- 已清楚定義 Project 與 Campaign 的責任邊界
- 已列出 Project 的 MVP 最小欄位，包含型別、用途與是否必填
- 已列出 Campaign 的 MVP 最小欄位，包含型別、用途與是否必填
- 已說明 Project 與 Campaign 的關聯方式
- 已指出 list / detail / create / update 需要暴露或接收的欄位差異
- 已明確標示哪些欄位先不納入 MVP
- 根目錄存在 `DATA_MODEL_DRAFT.md`
- `DATA_MODEL_DRAFT.md` 已對齊 `API_CONVENTIONS.md` 的欄位命名與 API baseline
- 已對有歧義的欄位歸屬寫出判斷理由
- 內容可直接作為 `T007` backend CRUD 與 `T008` frontend shell 的資料契約草案

## Deliverables

- 更新後的 `tickets/T006-projects-and-campaigns-schema-draft.md`
- 一份根目錄資料模型草案文件：`DATA_MODEL_DRAFT.md`
- 一份 Project schema draft
- 一份 Campaign schema draft
- 一份 Project / Campaign 關聯說明
- 一份後續 API schema 與前端型別可直接參考的欄位清單

## Notes / Constraints

- 必須以前置 ticket `T005-api-and-project-conventions` 的 API baseline 為準
- 必須維持在 MVP 最小欄位範圍，不要預先加大量未確認欄位
- 欄位設計應優先支持第一階段平台：Web / Mobile Web / PWA、iOS、Android
- 欄位命名要能對齊 backend schema 與 frontend type 的未來實作
- 需要特別避免把 Campaign 做成 Task 或 Feedback 的替代模型
- 若某個欄位是否屬於 Project 或 Campaign 有歧義，需在本 ticket 中明確註記判斷理由
- 本 ticket 以文件建立資料契約，不在這次直接進入 backend / frontend 實作
