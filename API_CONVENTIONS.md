# beta-feedback-platform API Conventions

## 1. Purpose

本文件定義 `beta-feedback-platform` 在 MVP 階段的 API 與前後端協作基準，提供後續 `T006-projects-and-campaigns-schema-draft`、`T007-projects-and-campaigns-backend-crud`、`T008-projects-and-campaigns-frontend-shell` 直接引用。

本文件的目標是建立共識，而不是預先建立完整框架。若未來實作發現某條規範不合理，應先更新本文件，再修改實作。

## 2. Current Baseline

目前已知且必須對齊的現況如下：

- backend 目前以 `FastAPI` 作為服務框架
- backend 目前的 API version prefix 由 `backend/app/core/config.py` 中的 `api_v1_prefix` 控制
- 目前預設值為 `/api/v1`
- backend 已存在 `/api/v1/health`
- frontend 已完成 `Nuxt 3 + TypeScript` 初始化
- `ARCHITECTURE.md` 已規定：
  - path 使用小寫
  - 資源名稱優先使用複數
  - path segment 採 `kebab-case`
  - frontend 不應把 API 呼叫散落在 `pages/`

本文件是 repo 層級的 API 規範來源；若與單一 ticket 衝突，以本文件更新後的版本為準。

## 3. API Path Rules

### 3.1 Versioning

- 所有業務 API 一律掛在 version prefix 之下。
- MVP 階段統一使用 `/api/v1`。
- version prefix 的 backend source of truth 為 `Settings.api_v1_prefix`。
- router 不應在各模組中重複硬寫 `/api/v1`；模組只負責資源自己的 prefix。

### 3.2 Path Naming

- path 一律使用小寫。
- path segment 一律使用 `kebab-case`。
- 資源名稱優先使用複數，例如：
  - `/projects`
  - `/campaigns`
  - `/device-profiles`
- path parameter 名稱使用可讀且穩定的 identifier 命名，建議採 `snake_case`：
  - `/projects/{project_id}`
  - `/campaigns/{campaign_id}`

### 3.3 REST Style

MVP 階段採簡單 REST 風格：

- `GET /resources`：取得列表
- `GET /resources/{resource_id}`：取得單筆
- `POST /resources`：建立
- `PATCH /resources/{resource_id}`：部分更新
- `DELETE /resources/{resource_id}`：刪除

### 3.4 Nested Resources

- 只有在父子關係本身就是路由語意的一部分時，才使用 nested resources。
- 若只是查詢過濾，優先使用 query params，而不是深層巢狀路徑。
- 例如：
  - 可接受：`GET /projects/{project_id}/campaigns`
  - 優先避免：`/projects/{project_id}/campaigns/{campaign_id}/something`

### 3.5 Query Parameters

- list/filter/search/sort/pagination 一律使用 query params。
- query parameter 名稱使用 `snake_case`。
- 不在 path 中混入查詢語意。

## 4. Request Baseline

### 4.1 General Rules

- `GET` request 不使用 request body。
- `POST` 用於建立資源。
- `PATCH` 用於部分更新，不要求呼叫端傳完整資源。
- request body 採 JSON。
- 時間欄位使用 ISO 8601 字串格式。
- 布林值必須使用真正的 boolean，不以字串 `"true"` / `"false"` 代替。

### 4.2 Create Request

建立資源時：

- request body 只包含可由使用者或呼叫端提供的欄位
- 不包含系統產生欄位，例如 `id`、`created_at`、`updated_at`
- 不包含由 backend 計算的衍生欄位

範例：

```json
{
  "name": "Closed Beta Round 1",
  "description": "Initial feedback collection"
}
```

### 4.3 Update Request

更新資源時：

- 採 `PATCH`
- 允許只提交要變更的欄位
- 不要求完整資源快照

範例：

```json
{
  "name": "Closed Beta Round 1 - Updated"
}
```

### 4.4 List Query Request

列表查詢的 baseline：

- filter、keyword、status、parent id 等都走 query params
- pagination 若需要，先採簡單模型，不提前導入複雜 cursor 規則

範例：

```text
GET /api/v1/campaigns?project_id=proj_123&status=active
```

## 5. Response Baseline

### 5.1 Principles

- response baseline 以務實為優先，不做過度包裝。
- detail / create / update 成功時，預設直接回傳資源本身。
- delete 成功時，預設回傳 `204 No Content`。
- 只有 list response 需要最低限度的集合包裝。

### 5.2 Detail / Create / Update Response

單筆成功 response baseline：

```json
{
  "id": "proj_123",
  "name": "Example Project",
  "created_at": "2026-04-03T10:00:00Z",
  "updated_at": "2026-04-03T10:00:00Z"
}
```

### 5.3 List Response

列表成功 response baseline：

```json
{
  "items": [
    {
      "id": "proj_123",
      "name": "Example Project"
    }
  ],
  "total": 1
}
```

規則如下：

- `items` 為陣列
- `total` 為目前回傳結果總數
- 若未實作分頁，也可先回傳 `total`
- 不預先加入複雜 meta block

### 5.4 Delete Response

- `DELETE` 成功時，預設回傳 `204 No Content`
- 若因實作限制暫時需要回傳 JSON，必須在對應 ticket 中明確說明原因

## 6. Error Response Baseline

### 6.1 Required Shape

錯誤 response 至少必須包含：

- `code`
- `message`
- `details`

baseline 格式如下：

```json
{
  "code": "resource_not_found",
  "message": "Project not found.",
  "details": {
    "resource": "project",
    "id": "proj_123"
  }
}
```

### 6.2 Field Meaning

- `code`：穩定、可程式判斷的錯誤代碼，使用 `snake_case`
- `message`：給開發與前端顯示的可讀文字
- `details`：補充資訊，可為 object、array，或 `null`

### 6.3 Recommended Error Codes

MVP 階段先使用簡單錯誤碼集合：

- `validation_error`
- `bad_request`
- `resource_not_found`
- `conflict`
- `internal_error`

### 6.4 Status Mapping

建議對應如下：

- `400 Bad Request` -> `bad_request`
- `404 Not Found` -> `resource_not_found`
- `409 Conflict` -> `conflict`
- `422 Unprocessable Entity` -> `validation_error`
- `500 Internal Server Error` -> `internal_error`

### 6.5 Validation Error Example

```json
{
  "code": "validation_error",
  "message": "Request validation failed.",
  "details": {
    "fields": [
      {
        "field": "name",
        "message": "This field is required."
      }
    ]
  }
}
```

## 7. Frontend API Client Minimal Consensus

### 7.1 Placement

依照 `ARCHITECTURE.md`：

- frontend 的 API 呼叫應集中在 `services/api/` 或 feature 內的 service layer
- 不要把 `fetch` / `$fetch` 直接散落在 `pages/`
- 若某 API 呼叫只服務單一 feature，可先留在該 feature 內
- 若已被多個 feature 共用，再抽到共享 API client

### 7.2 Minimum Structure

後續前端若開始接 API，最低共識如下：

- 建立一個 shared request helper，例如 `services/api/client.ts`
- 每個資源建立對應 service，例如：
  - `services/api/projects.ts`
  - `services/api/campaigns.ts`
- `pages/` 只負責頁面層組裝與觸發 service，不直接組裝 endpoint 字串

### 7.3 Base URL

frontend 應透過 runtime config 或等效方式管理 API base URL。

最低共識：

- frontend 只持有一個 API base URL 設定
- 該 base URL 應已包含 backend version prefix，例如：
  - `http://localhost:8000/api/v1`
- page / component 不應自行硬寫 `/api/v1`

## 8. Backend Config and API Prefix Consensus

### 8.1 Source of Truth

backend API prefix 的 source of truth 為：

- `backend/app/core/config.py`
- `Settings.api_v1_prefix`

目前預設值：

```python
api_v1_prefix = "/api/v1"
```

### 8.2 Config Rules

- 新增業務 router 時，應透過 `app/api/router.py` 統一註冊
- app 層在 `main.py` 以 `settings.api_v1_prefix` 掛載 API router
- 模組 router 僅定義自己的資源 prefix，例如 `/projects`
- 不要在各模組重複硬寫 `/api/v1/projects`

### 8.3 Environment Variable Rules

backend config 目前使用：

- `BFP_` 作為 env prefix

後續若需要透過環境變數覆寫 API prefix，應沿用：

- `BFP_API_V1_PREFIX`

PostgreSQL 保留方向維持：

- `BFP_DATABASE_URL`

### 8.4 Health Endpoint Exception

- `/api/v1/health` 為既有健康檢查 endpoint
- 後續業務 API 規範應與它保持同一 version prefix

## 9. Usage for Next Tickets

### 9.1 T006

`T006-projects-and-campaigns-schema-draft` 應依本文件決定：

- endpoint 命名方向
- list / detail / create / update 的資料暴露方式
- error code baseline 的對應欄位

### 9.2 T007

`T007-projects-and-campaigns-backend-crud` 應依本文件決定：

- `/projects`、`/campaigns` 的 route 風格
- list / detail / create / patch / delete 的 response baseline
- backend 錯誤格式與 status mapping

### 9.3 T008

`T008-projects-and-campaigns-frontend-shell` 應依本文件決定：

- frontend API client 放置位置
- page 與 service 的責任邊界
- mock data / placeholder API 的資料形狀

## 10. Non-Goals

本文件目前不處理以下內容：

- auth、RBAC、登入流程
- payment、chat、notification、recommendation
- 完整 API SDK 生成
- 完整 OpenAPI governance
- 分頁、排序、搜尋的進階策略
- production-ready error framework
