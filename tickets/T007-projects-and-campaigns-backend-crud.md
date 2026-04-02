# Title

T007 - Projects and Campaigns Backend CRUD

## Goal

在 `backend/` 中建立 Project / Campaign 的最小 CRUD 骨架，對齊既有 FastAPI 結構與 API 規範，並採用明確標示限制的暫時資料層實作，作為後續接入真實資料庫前的可驗證 backend 基礎。

## Background

目前 backend 已完成：

- FastAPI 專案初始化
- `app/main.py` 應用入口
- `/api/v1/health` health check
- `app/core/config.py`、`app/api/router.py`、`app/db/session.py` 等基礎骨架

接下來需要開始建立第一批業務能力，而 Project / Campaign 是最合理的切入點。不過在目前階段，PostgreSQL 僅保留整合方向，尚未建立 migration 與正式模型，因此本 ticket 可採用 in-memory 或暫時資料層，但必須清楚標示限制，避免誤認為可直接進入正式環境。

本 ticket 依賴：

- `T005-api-and-project-conventions`
- `T006-projects-and-campaigns-schema-draft`

## Scope

- 在 `backend/app/modules/` 下建立 `projects` 與 `campaigns` 模組的最小骨架
- 建立對應 `router.py`、`schemas.py`、`service.py`，必要時建立暫時資料層檔案
- 建立 Project 的 list / detail / create / update / delete 基本 API
- 建立 Campaign 的 list / detail / create / update / delete 基本 API
- 建立 Project 與 Campaign 的基本關聯驗證，例如 Campaign 必須屬於某個 Project
- 將新 router 註冊進既有 API router
- 補充最小測試，驗證主要 CRUD 流程

## Out of Scope

- 不實作 auth、ownership、permission 控制
- 不建立正式 PostgreSQL schema、migration 或 ORM 關聯
- 不實作複雜搜尋、排序、分頁策略
- 不實作 Task、Feedback、Reputation、Safety Layer 的業務邏輯
- 不引入 background jobs、notification、payment、chat、recommendation
- 不處理正式資料持久化保證

## Acceptance Criteria

- `backend/` 已新增 `projects` 與 `campaigns` 的最小模組骨架
- API path、request / response、錯誤格式符合 `T005` 規範
- 欄位結構符合 `T006` 的 schema draft
- 已可透過 API 完成 Project / Campaign 的最小 CRUD
- Campaign 與 Project 的關聯有最小驗證，不允許無父 Project 的 Campaign
- 暫時資料層的限制已在 ticket 或實作說明中明確標示
- 已新增最小測試，且測試可通過

## Deliverables

- `backend` 中可運作的 Project CRUD API
- `backend` 中可運作的 Campaign CRUD API
- 一個暫時資料層實作，作為正式 DB 前的過渡方案
- 一組最小測試，驗證 CRUD 與基本關聯

## Notes / Constraints

- 必須遵守 `ARCHITECTURE.md` 定義的 backend 結構與命名規則
- 必須以前置 ticket `T005` 與 `T006` 為準，不可自行重定義欄位與回傳格式
- 暫時資料層若採 in-memory，必須明確說明其資料在 process restart 後會消失
- service 層需承接基本業務流程，router 不應直接管理資料狀態
- 若目前階段還不適合導入 `repository.py`，可採更簡潔的資料層檔案，但需在 ticket 中說明原因
- 本 ticket 的目的是建立可驗證骨架，不是建立 production-ready data layer
- 後續若要接 PostgreSQL，應以替換資料層為主，而不是重寫整個 module interface
