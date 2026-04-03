# T015 - Structured Feedback Submission

## 1. 背景

在 `T014` 完成後，系統已具備：

- `Campaign` 作為活動容器
- `Tester Device Profile` 作為 tester-side device 資料基礎
- `Task` 作為任務分派與進度追蹤單位

下一步最合理的能力，是建立 `Structured Feedback`，讓 tester 能針對已執行的 task 提交具結構、可被整理與後續處理的測試回饋。

依照 PRD，本產品的核心目標之一是提升回饋可用性，因此 feedback 不應只是自由文字留言，而要有最小結構化欄位。即使在 MVP 階段，也應讓回饋具備基本分類、嚴重程度與可執行描述。

本 ticket 必須維持在 MVP 最小集合：

- 只做結構化 feedback 資料
- 只做最小 CRUD / shell
- 不做附件、富文字、AI summary、moderation workflow

## 2. 目標

建立 `Feedback` 的最小資料模型與提交流程，讓系統可以：

- 在 task 之下建立結構化回饋
- 讓 feedback 與 task / campaign / device profile 關聯
- 提供 backend CRUD 與 frontend list / detail shell
- 為後續回饋處理、狀態追蹤與信譽系統保留基礎資料

## 3. 範圍

本 ticket 只做 MVP 最小集合，範圍如下：

- 建立 feedback 基本資料模型
- 建立 feedback 與 task / campaign / device profile 的關聯
- 建立 backend CRUD
- 建立 frontend list / detail shell
- 建立 loading / empty / basic error state
- 建立對應 pytest 與 Playwright 測試

本 ticket 對 task / feedback 的關聯規則固定如下：

- feedback 必須屬於某個 task
- feedback 的 `campaign_id` 與 `device_profile_id` 由 task 關聯推導，不由 client 自行指定
- 單一 task 可有 0..n 筆 feedback
- feedback 建立成功時，若 task 狀態為 `assigned` 或 `in_progress`，可由 service 將 task 狀態更新為 `submitted`

## 4. 資料模型建議

### 4.1 Resource Shape

- `id`: `string`，系統產生
- `task_id`: `string`，required，建立後不可變
- `campaign_id`: `string`，系統推導
- `device_profile_id`: `string | null`，系統推導
- `summary`: `string`，required
- `rating`: `number | null`，optional，MVP 範圍 `1..5`
- `severity`: `"low" | "medium" | "high" | "critical"`，required
- `category`: `"bug" | "usability" | "performance" | "compatibility" | "other"`，required
- `reproduction_steps`: `string | null`，optional
- `expected_result`: `string | null`，optional
- `actual_result`: `string | null`，optional
- `note`: `string | null`，optional
- `submitted_at`: `string (ISO 8601)`，系統產生
- `updated_at`: `string (ISO 8601)`，系統產生

### 4.2 List / Detail / Create / Update Baseline

- List item：
  - `id`
  - `task_id`
  - `summary`
  - `severity`
  - `category`
  - `submitted_at`
- Detail：
  - 使用完整 resource shape
- Create body：
  - `summary`
  - `rating`
  - `severity`
  - `category`
  - `reproduction_steps`
  - `expected_result`
  - `actual_result`
  - `note`
- Update body：
  - 採 `PATCH`
  - 可更新欄位與 create body 相同
  - `task_id` / `campaign_id` / `device_profile_id` 不可更新

### 4.3 Validation Baseline

- `summary` 必填且不可為空白字串
- `rating` 若提供，必須在 `1..5`
- `severity` 與 `category` 必須為固定 enum
- optional string 欄位需做最小 normalization：
  - 去除前後空白
  - 空字串轉為 `null`
- 建立 feedback 時，backend 必須驗證 task 存在

## 5. API 路徑建議

### 5.1 建議路徑

- `GET /api/v1/tasks/{task_id}/feedback`
- `POST /api/v1/tasks/{task_id}/feedback`
- `GET /api/v1/feedback/{feedback_id}`
- `PATCH /api/v1/feedback/{feedback_id}`
- `DELETE /api/v1/feedback/{feedback_id}`

### 5.2 API Baseline

- list response 使用：
  - `{ items, total }`
- detail / create / patch 成功時直接回 resource
- delete 預設回 `204 No Content`
- 錯誤格式至少包含：
  - `code`
  - `message`
  - `details`

## 6. 前端頁面 / 路由建議

### 6.1 Feature Placement

- `frontend/features/feedback/`
  - `types.ts`
  - `api.ts`

### 6.2 Pages / Route Suggestion

- 優先擴充：
  - `frontend/pages/tasks/[taskId].vue`
- 在 `task detail` 下新增 feedback list shell
- 如需 detail shell，新增：
  - `frontend/pages/tasks/[taskId]/feedback/[feedbackId].vue`

### 6.3 UI Shell Requirements

- `task detail` 頁面可顯示 feedback list section
- List 至少顯示：
  - `summary`
  - `severity`
  - `category`
  - `submitted_at`
- Detail 至少顯示完整欄位
- 提供：
  - loading state
  - empty state
  - basic error state
- 補上穩定 selector，例如：
  - `data-testid="task-feedback-list"`
  - `data-testid="task-feedback-empty"`
  - `data-testid="feedback-detail-panel"`

## 7. Acceptance Criteria

- backend 已新增 `feedback` 模組，並對齊既有 FastAPI 結構
- backend 已可完成 feedback 的最小 CRUD
- feedback 與 task / campaign / device profile 的關聯已在 service 層建立
- 建立 feedback 時，task 存在性驗證已落地
- frontend 已可在 `task detail` 顯示 feedback shell
- frontend API 呼叫未散落在 `pages/` 中
- frontend 已包含 loading / empty / basic error state
- backend pytest 已補齊 validation / service / API 三層最小測試
- frontend Playwright 已補齊 feedback shell-level E2E
- 本 ticket 未實作檔案上傳、rich text editor、AI summary、duplicate detection、moderation workflow

## 8. Out of Scope

- 不實作檔案上傳
- 不實作截圖 / 錄影管理
- 不實作 rich text editor
- 不實作 AI summary
- 不實作 duplicate detection
- 不實作 moderation workflow
- 不實作 advanced form
- 不實作 admin 後台
- 不做正式 PostgreSQL migration 或 production-ready persistence

## 9. Backend Work Items

- 在 `backend/app/modules/` 下新增 `feedback` 模組
- 採既有 backend module 慣例建立：
  - `router.py`
  - `schemas.py`
  - `service.py`
  - 視需要建立 `repository.py`
  - 視需要建立 `models.py`
- 將 router 註冊到既有 API router
- 先沿用 in-memory repository 策略，並清楚標示 restart 後資料會消失
- `POST /tasks/{task_id}/feedback` 時驗證 task 存在
- feedback 建立時由 task 推導：
  - `campaign_id`
  - `device_profile_id`
- 視需要在 service 層把 task 狀態更新為 `submitted`

## 10. Frontend Work Items

- 在 `frontend/features/feedback/` 下建立最小必要檔案
- 擴充 `task detail` 頁面，加入 feedback list shell
- 如有需要，建立 feedback detail shell 頁面
- 補最小 navigation / link，讓使用者可從 task detail 進入 feedback detail
- 不建立 rich text / upload / advanced submission UI

## 11. Test Items

### 11.1 Backend Tests

- validation tests：
  - required field 驗證
  - `rating` range 驗證
  - `severity` enum 驗證
  - `category` enum 驗證
  - optional string normalization
- service tests：
  - create / list / update / delete 基本流程
  - task not found error
  - `campaign_id` / `device_profile_id` 推導驗證
  - 視需要驗證 task status 更新為 `submitted`
- API tests：
  - nested list / create
  - detail / patch / delete
  - response shape 與 error shape 驗證

### 11.2 Frontend Tests

- 保持既有 typecheck / build 可通過
- 新增 feedback shell 不可破壞既有 task / campaign / device profile shell

### 11.3 E2E Tests

- 補 feedback shell-level Playwright 測試
- 至少覆蓋：
  - task detail 下的 feedback list happy path
  - empty state
  - error state
  - 若有 detail shell，補 detail happy path
- 建議沿用既有 route mocking 方式

## 12. Risk / Notes

- `Feedback` 不等於 moderation case；本票只處理 tester 提交的結構化資料本體
- 本 ticket 不處理附件與多媒體證據，因此 `reproduction_steps / expected_result / actual_result` 仍以純文字欄位為主
- `rating` 在 MVP 階段只作為最小量化欄位，不代表完整評分系統
- 若後續需要 developer review status、feedback triage 或 duplicate merge，應另開 ticket
- feedback 與 task 的狀態關聯應保持最小，避免在本票中偷做完整 workflow engine
- 命名需對齊：
  - frontend feature：`feedback`
  - backend module：`feedback`
  - API resource：`feedback`

## 13. 依賴關係（Dependencies）

主要依賴：

- `T014-task-assignment-and-task-status-flow`

延續既有基礎：

- `T005-api-and-project-conventions`
- `T010-frontend-e2e-playwright`
- `T011-projects-and-campaigns-e2e-flows`
- `T012-tester-device-profile-crud-and-shell-flows`
- `T013-campaign-eligibility-filter-rules`
