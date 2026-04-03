# T014 - Task Assignment and Task Status Flow

## 1. 背景

在 `T012` 與 `T013` 之後，系統已逐步具備：

- `Campaign` 作為測試活動容器
- `Tester Device Profile` 作為 tester 端的裝置資料基礎
- `Eligibility Rule` 作為 campaign 條件表示方式

下一步最合理的能力，是建立 `Task` 與最小狀態流轉（status flow），讓平台可以表達「某個 campaign 下有哪些測試任務、目前任務進度到哪裡、是否已指派到某個 tester-side device profile」。

本 ticket 必須維持 MVP 最小集合，不進入：

- 自動派發
- 排程器
- 通知系統
- 複雜 SLA 規則

由於目前尚未有完整 `Tester` 帳號與 ownership 綁定，本 ticket 的最小實作需採務實策略：以 `device_profile_id` 作為 task assignment 的 tester-side anchor，先讓任務能與實際裝置資料建立關聯。

## 2. 目標

建立 `Task` 的最小資料模型、campaign / device profile 關聯與狀態流轉規則，讓系統可以：

- 在 campaign 之下建立任務
- 把任務指派到某個 `Tester Device Profile`
- 追蹤任務從 draft 到 submitted / closed 的基本流程
- 提供 frontend list / detail shell 與最小狀態呈現

## 3. 範圍

本 ticket 只做 MVP 最小集合，範圍如下：

- 建立 `Task` 的最小資料模型
- 建立 task 與 campaign / device profile 的關聯
- 建立最小 status flow
- 建立 backend CRUD / status update
- 建立 frontend list / detail shell
- 建立 loading / empty / basic error state
- 建立對應 pytest 與 Playwright 測試

本 ticket 的狀態集合固定如下：

- `draft`
- `open`
- `assigned`
- `in_progress`
- `submitted`
- `closed`

本 ticket 的狀態轉移規則固定如下：

- `draft -> open`
- `draft -> closed`
- `open -> assigned`
- `open -> closed`
- `assigned -> in_progress`
- `assigned -> closed`
- `in_progress -> submitted`
- `in_progress -> closed`
- `submitted -> closed`
- `closed` 為終止狀態

本 ticket 不支援：

- 任意跳狀態
- 自動派發演算法
- 自動 reminder

## 4. 資料模型建議

### 4.1 Resource Shape

- `id`: `string`，系統產生
- `campaign_id`: `string`，required，建立後不可變
- `device_profile_id`: `string | null`，optional
- `title`: `string`，required
- `instruction_summary`: `string | null`，optional
- `status`: `"draft" | "open" | "assigned" | "in_progress" | "submitted" | "closed"`，required
- `submitted_at`: `string | null`，系統產生，當狀態進入 `submitted` 時寫入
- `created_at`: `string (ISO 8601)`，系統產生
- `updated_at`: `string (ISO 8601)`，系統產生

### 4.2 List / Detail / Create / Update Baseline

- List item：
  - `id`
  - `campaign_id`
  - `device_profile_id`
  - `title`
  - `status`
  - `updated_at`
- Detail：
  - 使用完整 resource shape
- Create body：
  - `title`
  - `instruction_summary`
  - `device_profile_id`
  - `status`
- Update body：
  - 採 `PATCH`
  - 可更新欄位：
    - `title`
    - `instruction_summary`
    - `device_profile_id`
    - `status`
  - `campaign_id` 不可更新

### 4.3 Validation / Flow Rules

- `title` 必填且不可為空白字串
- `instruction_summary` 若提供，需做最小 normalization
- create 時 `status` 預設為 `draft`
- `device_profile_id` 可在 `draft / open` 狀態下為 `null`
- 進入 `assigned / in_progress / submitted / closed` 前，必須已有 `device_profile_id`
- 若 `device_profile_id` 有值，backend 需驗證對應 device profile 存在
- 當狀態進入 `submitted` 時，backend 應自動寫入 `submitted_at`

## 5. API 路徑建議

### 5.1 建議路徑

- `GET /api/v1/tasks`
- `POST /api/v1/campaigns/{campaign_id}/tasks`
- `GET /api/v1/tasks/{task_id}`
- `PATCH /api/v1/tasks/{task_id}`
- `DELETE /api/v1/tasks/{task_id}`

### 5.2 Query Baseline

- `GET /api/v1/tasks?campaign_id=...`
- `GET /api/v1/tasks?device_profile_id=...`
- `GET /api/v1/tasks?status=...`

### 5.3 API Baseline

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

- `frontend/features/tasks/`
  - `types.ts`
  - `api.ts`

### 6.2 Pages / Route Suggestion

- `frontend/pages/tasks/index.vue`
- `frontend/pages/tasks/[taskId].vue`

可選的頁面關聯方式：

- 從 `campaign detail` 連到 `/tasks?campaign_id=...`
- 從 `task detail` 顯示最小 assignment 與 status 區塊

### 6.3 UI Shell Requirements

- List 頁面至少顯示：
  - `title`
  - `campaign_id`
  - `device_profile_id`
  - `status`
  - `updated_at`
- Detail 頁面至少顯示完整欄位
- 提供：
  - loading state
  - empty state
  - basic error state
- 補上穩定 selector，例如：
  - `data-testid="tasks-list"`
  - `data-testid="tasks-empty"`
  - `data-testid="task-detail-panel"`

## 7. Acceptance Criteria

- backend 已新增 `tasks` 模組，並對齊既有 FastAPI 結構
- backend 已可完成 task 的最小 CRUD 與 status update
- task 與 `campaign`、`device_profile` 的最小關聯驗證已存在
- status flow 驗證已在 service 層落地，不允許非法跳轉
- frontend 已新增 `tasks` feature 與 list / detail shell
- frontend API 呼叫未散落在 `pages/` 中
- frontend 已包含 loading / empty / basic error state
- backend pytest 已補齊 validation / service / API 三層最小測試
- frontend Playwright 已補齊 task shell-level E2E
- 本 ticket 未實作排程器、自動派發、notification system、reward system

## 8. Out of Scope

- 不實作排程器
- 不實作自動派發演算法
- 不實作 reminder / notification system
- 不實作任務獎勵機制
- 不實作複雜 SLA 規則
- 不實作 advanced form
- 不實作 admin 後台
- 不做正式 PostgreSQL migration 或 production-ready persistence

## 9. Backend Work Items

- 在 `backend/app/modules/` 下新增 `tasks` 模組
- 採既有 backend module 慣例建立：
  - `router.py`
  - `schemas.py`
  - `service.py`
  - 視需要建立 `repository.py`
  - 視需要建立 `models.py`
- 將 router 註冊到既有 API router
- 先沿用 in-memory repository 策略，並清楚標示 restart 後資料會消失
- `POST /campaigns/{campaign_id}/tasks` 時驗證 campaign 存在
- `device_profile_id` 若提供，驗證對應 device profile 存在
- 在 service 層實作狀態轉移驗證與 `submitted_at` 寫入邏輯

## 10. Frontend Work Items

- 在 `frontend/features/tasks/` 下建立最小必要檔案
- 建立 `tasks` list / detail shell
- 在 task detail 中清楚呈現：
  - status
  - assignment target (`device_profile_id`)
  - campaign relation
- 視需要在 campaign detail 補最小 navigation link 到 task list
- 不建立 create / edit advanced form

## 11. Test Items

### 11.1 Backend Tests

- validation tests：
  - required field 驗證
  - `status` enum 驗證
  - empty update payload 驗證
- service tests：
  - create / list / update / delete 基本流程
  - campaign not found error
  - device profile not found error
  - illegal status transition error
  - `submitted_at` 寫入驗證
- API tests：
  - nested create
  - list / detail / patch / delete
  - query by `campaign_id` / `device_profile_id` / `status`
  - response shape 與 error shape 驗證

### 11.2 Frontend Tests

- 保持既有 typecheck / build 可通過
- 新增 tasks shell 不可破壞既有 project / campaign / device profile shell

### 11.3 E2E Tests

- 補 `tasks` shell-level Playwright 測試
- 至少覆蓋：
  - list happy path
  - detail happy path
  - empty state
  - error state
  - 基本 status 顯示
- 建議沿用既有 route mocking 方式

## 12. Risk / Notes

- 目前尚未有完整 `Tester` 帳號，本 ticket 先以 `device_profile_id` 作為 assignment anchor
- 這是 MVP 階段的務實做法，目的是先建立任務流，而不是完成完整 tester identity domain
- `Task` 不應在本票中承接回饋內容本身；結構化回饋應由後續 `Feedback` 模組處理
- `Task` 也不應在本票中實作 eligibility checking engine；是否符合條件由後續流程判斷
- 若未來需要更細的任務 SLA / reminder / escalation，應另開 ticket，而非在本票擴張

## 13. 依賴關係（Dependencies）

主要依賴：

- `T012-tester-device-profile-crud-and-shell-flows`
- `T013-campaign-eligibility-filter-rules`

延續既有基礎：

- `T005-api-and-project-conventions`
- `T007-projects-and-campaigns-backend-crud`
- `T008-projects-and-campaigns-frontend-shell`
- `T010-frontend-e2e-playwright`
- `T011-projects-and-campaigns-e2e-flows`
