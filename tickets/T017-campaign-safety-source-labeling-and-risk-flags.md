# T017 - Campaign Safety Source Labeling and Risk Flags

## 1. 背景

`Project -> Campaign -> Device Profile -> Eligibility -> Task -> Feedback` 的核心閉環已完成，但目前產品仍缺少一個非常關鍵的產品化能力：安全與來源可辨識。

依照 `PRD.md`，本產品必須維持以下安全原則：

- 優先採用各平台官方測試 / 分發機制
- 不鼓勵來源不明安裝檔
- 不鼓勵關閉裝置安全防護
- 必須有來源標示、風險提示、審核機制

若沒有把這些原則落成真正的資料欄位與 UI 顯示，平台很容易從「測試管理平台」漂移成模糊來源的分發工具。這不只和產品定位衝突，也會讓後續 reputation 與審核流程缺乏基礎資料。

本票的目的是先把 `Campaign` 層的安全標示做出來，讓每一輪測試活動都能清楚表達：

- 來源是什麼
- 分發方式是什麼
- 風險等級如何
- 是否經過最小人工審核

## 2. 目標

建立 `Campaign Safety` 的最小資料與顯示能力，讓 `Campaign` 能表達安全來源、風險等級與基本審核狀態。

本票完成後，應具備以下結果：

- backend 可管理 campaign safety 的最小 nested resource
- frontend 可在 `campaign detail` 顯示 safety section
- 使用者可辨識來源標示與風險提示
- 後續 reputation / moderation 能在此基礎上延伸

## 3. 範圍

本票只做 MVP 最小集合，範圍如下：

- 建立 `Campaign Safety` 的最小資料模型
- 建立 campaign 與 safety 的 0..1 關聯
- 建立 backend create / read / patch / delete
- 建立 frontend `campaign detail` 內嵌 safety shell
- 建立 loading / empty / basic error / happy path
- 建立對應 pytest 與 Playwright 測試

本票固定欄位如下：

- `id`
- `campaign_id`
- `distribution_channel`
- `source_label`
- `source_url`
- `risk_level`
- `review_status`
- `official_channel_only`
- `risk_note`
- `created_at`
- `updated_at`

## 4. 資料模型建議

### 4.1 Resource Shape

- `id`: `string`，系統產生
- `campaign_id`: `string`，required，建立後不可變
- `distribution_channel`: `"web_url" | "pwa_url" | "testflight" | "google_play_testing" | "manual_invite" | "other"`，required
- `source_label`: `string`，required
- `source_url`: `string | null`，optional
- `risk_level`: `"low" | "medium" | "high"`，required
- `review_status`: `"pending" | "approved" | "rejected"`，required，create 預設為 `pending`
- `official_channel_only`: `boolean`，required，create 預設為 `false`
- `risk_note`: `string | null`，optional
- `created_at`: `string (ISO 8601)`，系統產生
- `updated_at`: `string (ISO 8601)`，系統產生

### 4.2 Validation Rules

- `distribution_channel` 必須為固定 enum
- `source_label` 必填且不可為空白字串
- `source_url` 若提供，先以普通字串處理，不在本票中做進階 URL 驗證框架
- `risk_level` 必須為固定 enum
- `review_status` 必須為固定 enum
- `risk_note` 若提供，需做最小 normalization：
  - 去除前後空白
  - 空字串轉為 `null`

### 4.3 List / Detail / Create / Update Baseline

- 本票不需要 safety list 頁
- `campaign detail` 內嵌 section 可視為 safety detail shell
- create body：
  - `distribution_channel`
  - `source_label`
  - `source_url`
  - `risk_level`
  - `review_status`
  - `official_channel_only`
  - `risk_note`
- update body 採 `PATCH`
- `campaign_id` 不可更新

## 5. API 路徑建議

- `GET /api/v1/campaigns/{campaign_id}/safety`
- `POST /api/v1/campaigns/{campaign_id}/safety`
- `PATCH /api/v1/campaigns/{campaign_id}/safety`
- `DELETE /api/v1/campaigns/{campaign_id}/safety`

API baseline：

- `GET` 成功時直接回 resource
- `POST` 成功時直接回 resource
- `PATCH` 成功時直接回 resource
- `DELETE` 成功時回 `204 No Content`
- 若 campaign 不存在或 safety 不存在，錯誤格式需符合 `API_CONVENTIONS.md`

## 6. 前端頁面 / 路由建議

### 6.1 Feature Placement

- `frontend/features/safety/`
  - `types.ts`
  - `api.ts`

### 6.2 Pages / Route Suggestion

- 優先擴充：
  - `frontend/pages/campaigns/[campaignId].vue`

### 6.3 UI Shell Requirements

- `campaign detail` 顯示 safety section
- 至少呈現：
  - `distribution_channel`
  - `source_label`
  - `risk_level`
  - `review_status`
  - `official_channel_only`
  - `risk_note`
- 提供：
  - loading state
  - empty state（尚未設定 safety）
  - basic error state
- 補穩定 selector，例如：
  - `data-testid="campaign-safety-panel"`
  - `data-testid="campaign-safety-empty"`
  - `data-testid="campaign-safety-error"`

## 7. Acceptance Criteria

- backend 已新增 `safety` 模組，並對齊既有 FastAPI 結構
- campaign 已可對應 0..1 筆 safety resource
- API path、response baseline、error baseline 符合 `API_CONVENTIONS.md`
- frontend 已可在 `campaign detail` 顯示 safety shell
- frontend API 呼叫未散落在 `pages/` 中
- frontend 已包含 loading / empty / basic error state
- backend pytest 已補齊 validation / service / API 三層最小測試
- frontend Playwright 已補齊 campaign safety shell-level E2E
- 本票未實作自動審核、檔案掃描、admin 審核工作台

## 8. Out of Scope

- 不實作自動審核流程
- 不實作檔案安全掃描
- 不實作 admin 後台
- 不實作附件上傳
- 不實作平台政策比對引擎
- 不實作通知或封鎖流程
- 不做正式 PostgreSQL migration 或 production-ready persistence

## 9. Backend Work Items

- 在 `backend/app/modules/` 下新增 `safety` 模組
- 建立：
  - `router.py`
  - `schemas.py`
  - `service.py`
  - `repository.py`
  - `models.py`
- 將 router 註冊到既有 API router
- 建立 campaign 與 safety 的一對一關聯驗證
- `POST /campaigns/{campaign_id}/safety` 時驗證 campaign 存在
- 若同一 campaign 已有 safety resource，重複建立應回 `conflict`
- 先沿用 in-memory repository 策略

## 10. Frontend Work Items

- 在 `frontend/features/safety/` 下建立最小必要檔案
- 擴充 `campaign detail` 頁面，加入 safety section
- 不建立獨立 safety list 頁
- 若需要簡單 CTA，可只提供：
  - 查看已設定 safety
  - 顯示尚未設定 safety 的 placeholder
- 本票不做 create / edit 表單，僅建立 shell 顯示

## 11. Test Items

### 11.1 Backend Tests

- validation tests：
  - enum 驗證
  - required field 驗證
  - optional string normalization
- service tests：
  - create / get / patch / delete 基本流程
  - campaign not found error
  - duplicate safety conflict
- API tests：
  - nested get / create / patch / delete
  - error shape 驗證

### 11.2 Frontend Tests

- 保持既有 typecheck / build 可通過
- safety section 不可破壞既有 campaign detail shell

### 11.3 E2E Tests

- 補 campaign detail 下 safety section 的 Playwright 測試
- 至少覆蓋：
  - happy path
  - empty state
  - error state

## 12. Risk / Notes

- `distribution_channel` 的 enum 應保持務實，不要為了完整感一次列出所有平台所有測試方案
- `source_url` 在 MVP 階段只作為顯示用欄位，不要偷做連線驗證服務
- safety 先做「可辨識」，不是做「全自動安全保證」

## 13. 依賴關係（Dependencies）

主要依賴：

- `T016-safety-and-reputation-mvp-schema-draft`
- `T013-campaign-eligibility-filter-rules`
- `T014-task-assignment-and-task-status-flow`

後續可支撐：

- `T022-reputation-baseline-and-summary-metrics`
- `T023-homepage-ia-and-overview-shell-refresh`
