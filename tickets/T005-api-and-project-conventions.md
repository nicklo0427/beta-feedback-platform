# Title

T005 - API and Project Conventions

## Goal

定義後續功能開發要共同遵守的 API 與專案協作規範，包含 API 路徑規則、request / response baseline、錯誤格式 baseline，以及 frontend API client 與 backend config 的最小共識，並將這些共識落成可直接引用的規範文件，作為後續功能票的前置規範。

## Background

目前專案已完成以下基礎工作：

- `frontend/` 已完成 Nuxt 3 + TypeScript 初始化
- `backend/` 已完成 FastAPI 初始化，並具備 `/api/v1/health`
- repo 根目錄已有 `ARCHITECTURE.md`，可作為前後端結構與命名規範依據

接下來若要進入第一批業務功能，例如 Project / Campaign，必須先建立 API 與跨前後端的最低共識。若沒有先定義這些 baseline，後續很容易出現：

- API 命名與路徑風格不一致
- request / response 結構漂移
- frontend API client 各自封裝，難以維護
- backend 錯誤回傳格式混亂，前端難以處理

本 ticket 應作為 `T006-projects-and-campaigns-schema-draft`、`T007-projects-and-campaigns-backend-crud`、`T008-projects-and-campaigns-frontend-shell` 的前置條件。

目前 backend 已有 `/api/v1/health`，且 `backend/app/core/config.py` 已存在 `api_v1_prefix` 設定，因此本 ticket 應優先對齊現有實作，而不是重新設計另一套 prefix 規則。

## Scope

- 定義 API versioning 與 path 命名規則
- 定義資源導向（resource-oriented）的 endpoint baseline
- 定義 request body / query / path params 的基本約定
- 定義成功 response baseline
- 定義錯誤 response baseline
- 定義 frontend API client 的最小分層與使用方式
- 定義 backend config / settings 與 API prefix 的最小共識
- 將以上共識落成根目錄文件 `API_CONVENTIONS.md`
- 明確說明後續功能票在實作時必須遵守本規範

## Out of Scope

- 不建立實際 Project / Campaign endpoint
- 不建立完整 OpenAPI 文件流程
- 不實作 auth、RBAC、session、token 或權限邏輯
- 不引入通知、聊天、支付、推薦系統等非 MVP 範圍
- 不處理部署、CI/CD、Docker 或 API gateway
- 不定義過度複雜的錯誤碼體系
- 不在這次建立完整 backend error handling framework
- 不在這次建立 frontend 實體 API client 檔案

## Acceptance Criteria

- 已明確定義 API path 規則，例如 version prefix、複數資源命名、kebab-case path 風格
- 已明確定義 request / response baseline，至少涵蓋 list、detail、create / update 基本格式
- 已明確定義錯誤格式 baseline，至少涵蓋 `code`、`message`、`details`
- 已明確定義 frontend API client 的最小共識，例如集中 base URL、集中 request helper、避免在頁面內直接散落 fetch 寫法
- 已明確定義 backend config 對 API prefix 與未來 database / environment config 的最小共識
- 根目錄存在 `API_CONVENTIONS.md`
- `API_CONVENTIONS.md` 已明確對齊現有 backend `/api/v1` 與 `Settings.api_v1_prefix`
- `API_CONVENTIONS.md` 已可直接供 `T006`、`T007`、`T008` 引用
- 已明確標示此 ticket 為後續 `T006`、`T007`、`T008` 的前置條件

## Deliverables

- 更新後的 `tickets/T005-api-and-project-conventions.md`
- 一份根目錄 API 規範文件：`API_CONVENTIONS.md`
- 一份 request / response baseline 規範
- 一份錯誤格式 baseline 規範
- 一組 frontend API client 與 backend config 的最小共識

## Notes / Constraints

- 必須與 `ARCHITECTURE.md` 的命名與分層規範一致
- API 路徑應優先採用簡單、可維護、可延伸的 REST 風格
- response baseline 應務實，不要過度包裝所有資料
- 錯誤格式應以方便 frontend 顯示與 debug 為優先
- frontend API client 規範應避免把業務呼叫散落在 `pages/` 中
- backend config 規範應與目前已存在的 `app/core/config.py` 與 `/api/v1` 路由前綴對齊
- 本 ticket 優先以文件建立共識，不預先在 runtime 中塞入過多共用框架
- 本 ticket 完成後，`T006` 才能開始定義欄位，`T007` 與 `T008` 才能開始具體實作
