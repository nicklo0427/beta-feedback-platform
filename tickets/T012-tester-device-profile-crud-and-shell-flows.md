# T012 - Tester Device Profile CRUD and Shell Flows

## 1. 背景

目前專案已完成以下基礎能力：

- `projects / campaigns` backend CRUD 已存在
- `projects / campaigns` frontend shell 已存在
- Playwright E2E baseline 與 shell-level E2E 流程已存在
- `ARCHITECTURE.md`、`API_CONVENTIONS.md` 已提供前後端結構與 API baseline

依照 PRD，`Tester Device Profile` 是 MVP 第一階段的核心模組之一，用於記錄 Tester 可用裝置與平台資訊，並作為後續 Eligibility Filter、Task 指派與回饋上下文的基礎資料來源。

在目前狀態下，`projects / campaigns` 已能代表「測什麼」與「哪一輪活動」，下一步最合理的核心資料建設是補上「誰用什麼裝置參與測試」。這能讓後續測試流程逐步從活動管理進入實際測試者資料建設，但仍維持在 MVP 最小集合內。

本 ticket 的方向必須維持產品定位：

- 這是一個跨平台 Beta 測試媒合與回饋管理平台
- 不是互刷平台
- 不是評論交換平台
- 不是灌量工具

MVP 第一階段平台只考慮：

- Web
- H5
- PWA
- iOS
- Android

## 2. 目標

建立 `Tester Device Profile` 的 MVP 最小 CRUD 與 frontend shell flows，讓系統能先記錄 Tester 可用裝置資料，並以一致的 list / detail 殼層頁面呈現。

本 ticket 完成後，應具備以下結果：

- backend 可管理最小 `device_profiles` 資源
- frontend 可查看 `device_profiles` 的 list / detail shell
- 前後端資料 shape 與 API baseline 保持一致
- 後續 Eligibility Filter、Task、Feedback 可以在這個基礎上延伸，但本 ticket 不先實作那些能力

## 3. 範圍

本 ticket 只做 MVP 最小集合，範圍如下：

- 建立 `Tester Device Profile` 的最小資料欄位與 CRUD 契約
- 建立 backend `device_profiles` 模組的最小 CRUD
- 建立 frontend `device-profiles` feature 與 list / detail shell 頁面
- 建立 loading / empty / basic error state
- 建立對應 pytest 與 Playwright 測試

本 ticket 的 MVP 最小欄位固定如下，後續實作不得自行擴欄：

### Resource Shape

- `id`: `string`，系統產生
- `name`: `string`，required
- `platform`: `"web" | "h5" | "pwa" | "ios" | "android"`，required
- `device_model`: `string`，required
- `os_name`: `string`，required
- `os_version`: `string | null`，optional
- `browser_name`: `string | null`，optional
- `browser_version`: `string | null`，optional
- `locale`: `string | null`，optional
- `notes`: `string | null`，optional
- `created_at`: `string (ISO 8601)`，系統產生
- `updated_at`: `string (ISO 8601)`，系統產生

### List / Detail / Create / Update Baseline

- List item：
  - `id`
  - `name`
  - `platform`
  - `device_model`
  - `os_name`
  - `updated_at`
- Detail：
  - 使用完整 resource shape
- Create body：
  - `name`
  - `platform`
  - `device_model`
  - `os_name`
  - `os_version`
  - `browser_name`
  - `browser_version`
  - `locale`
  - `notes`
- Update body：
  - 採 `PATCH`
  - 允許部分更新
  - 可更新欄位與 create body 相同

### API 路徑固定如下

- `GET /api/v1/device-profiles`
- `POST /api/v1/device-profiles`
- `GET /api/v1/device-profiles/{device_profile_id}`
- `PATCH /api/v1/device-profiles/{device_profile_id}`
- `DELETE /api/v1/device-profiles/{device_profile_id}`

### Frontend 頁面路由固定如下

- `/device-profiles`
- `/device-profiles/[deviceProfileId]`

### Frontend shell 呈現範圍

- list 頁面顯示最小清單資料
- detail 頁面顯示完整欄位資料
- 可從首頁新增一個最小 navigation entry 到 `/device-profiles`
- 不做 create / update 表單頁

## 4. Acceptance Criteria

- backend 已新增 `device_profiles` 模組，並對齊既有 FastAPI 結構
- API path、response baseline、error baseline 符合 `API_CONVENTIONS.md`
- `device_profiles` 命名符合 `ARCHITECTURE.md`
- backend 已可完成 `Tester Device Profile` 的最小 CRUD
- frontend 已新增 `device-profiles` feature 與 list / detail shell
- frontend API 呼叫未散落在 `pages/` 中
- frontend 已包含 loading / empty / basic error state
- frontend 頁面已提供穩定 selector，例如 `data-testid`
- backend pytest 已補齊 validation / service / API 三層最小測試
- frontend Playwright 已補齊 `device-profiles` shell-level E2E
- 本 ticket 未實作 eligibility engine、auto matching、advanced form、admin 後台

## 5. Out of Scope

- 不實作 Eligibility Filter / eligibility engine
- 不實作 auto matching / auto recommendation
- 不實作 tester ranking 或信譽邏輯
- 不實作登入、權限、RBAC、ownership 綁定
- 不實作 create / update 的 advanced form
- 不做 bulk import、CSV upload、批次編輯
- 不做 admin 後台
- 不做多條件搜尋、排序、分頁的進階策略
- 不做正式 PostgreSQL migration 或 production-ready persistence

## 6. Backend Work Items

### 6.1 Module and API

- 在 `backend/app/modules/` 下新增 `device_profiles` 模組
- 採既有 backend module 慣例建立：
  - `router.py`
  - `schemas.py`
  - `service.py`
  - 視需要建立 `repository.py`
  - 視需要建立 `models.py`
- 將 router 註冊到既有 API router

### 6.2 CRUD Baseline

- 實作 list / detail / create / patch / delete
- list response 使用：
  - `{ items, total }`
- detail / create / patch 成功時直接回 resource
- delete 預設回 `204 No Content`

### 6.3 Validation

- `platform` 只允許：
  - `web`
  - `h5`
  - `pwa`
  - `ios`
  - `android`
- `name`、`device_model`、`os_name` 為必填且不可為空白字串
- optional string 欄位應做最小 normalization：
  - 去除前後空白
  - 空字串轉為 `null`
- update body 若沒有任何可更新欄位，應回 validation error

### 6.4 Temporary Data Layer

- 先沿用與 `projects / campaigns` 相同的簡潔策略，可使用 in-memory repository
- 必須明確標示限制：
  - process restart 後資料會消失
  - 不適用多 instance / 正式持久化場景

### 6.5 Error Handling

- 錯誤格式至少包含：
  - `code`
  - `message`
  - `details`
- 找不到 `device_profile_id` 時使用：
  - `resource_not_found`

## 7. Frontend Work Items

### 7.1 Feature and Service Placement

- 在 `frontend/features/device-profiles/` 下建立最小必要檔案：
  - `types.ts`
  - `api.ts`
- 如有單一模組專屬 helper，優先與 feature 共置
- 不要把 API 呼叫直接寫在 `pages/`

### 7.2 Pages

- 建立：
  - `frontend/pages/device-profiles/index.vue`
  - `frontend/pages/device-profiles/[deviceProfileId].vue`
- 首頁可新增一個最小 navigation link 到 `/device-profiles`
- 不建立 create / edit 表單頁

### 7.3 UI Shell Requirements

- List 頁面至少顯示：
  - `name`
  - `platform`
  - `device_model`
  - `os_name`
  - `updated_at`
- Detail 頁面至少顯示完整欄位
- 提供：
  - loading state
  - empty state
  - basic error state
- 補上穩定 selector，例如：
  - `data-testid="device-profiles-list"`
  - `data-testid="device-profiles-empty"`
  - `data-testid="device-profile-detail-panel"`

### 7.4 API Usage

- 若 backend CRUD 已完成，frontend 應優先接真實 API
- 頁面資料 shape 必須與 backend contract 一致
- 不自行發明未定義欄位

## 8. Test Items

### 8.1 Backend Tests

- validation tests：
  - required field 驗證
  - `platform` enum 驗證
  - optional string normalization
  - empty update payload 驗證
- service tests：
  - create / list / update / delete 基本流程
  - not found error
- API tests：
  - list / detail / create / patch / delete
  - response shape 與 error shape 驗證

### 8.2 Frontend Tests

- 保持既有 typecheck / build 可通過
- 若有新增型別或 API 呼叫，不可破壞既有 shell

### 8.3 E2E Tests

- 補 `device-profiles` 的 shell-level Playwright 測試
- 至少覆蓋：
  - 首頁導到 `/device-profiles`
  - list happy path
  - detail happy path
  - empty state
  - error state
- 建議沿用 `T011` 的 route mocking 方式，讓測試穩定且不綁定 backend 啟動

## 9. Risk / Notes

- 目前尚未有完整 `Tester` 帳號與 ownership，本 ticket 的 `Tester Device Profile` 先作為獨立資源處理，不綁定真實 tester 身分
- 這個做法是 MVP 階段的暫時設計，目的是先建立裝置資料基礎，而不是完成完整 tester domain
- `browser_name` / `browser_version` 對行動平台不一定必要，但先作為通用 optional 欄位保留，避免過早拆分平台專屬模型
- 本 ticket 只建立「資料建設 + shell flows」，不進一步實作 eligibility engine、matching、task dispatch
- 後續若要導入 `Eligibility Filter`，應以這個模組作為資料來源，而不是在本 ticket 內偷做條件比對邏輯
- 命名必須對齊：
  - frontend：`device-profiles`
  - backend：`device_profiles`
- 若首頁 navigation link 會影響既有 E2E，需同步更新對應 Playwright 測試，但不得破壞既有 `projects / campaigns` 測試
