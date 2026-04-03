# T013 - Campaign Eligibility Filter Rules

## 1. 背景

目前專案已完成或已具備以下基礎：

- `projects / campaigns` backend CRUD 與 frontend shell 已存在
- `projects / campaigns` 的 shell-level Playwright E2E 已存在
- `Tester Device Profile` 已在 `T012` 中定義為下一步核心資料建設
- `ARCHITECTURE.md`、`API_CONVENTIONS.md` 已提供結構與 API baseline

依照 PRD，`Eligibility Filter` 的目的是讓 Developer 定義哪些 Tester / Device Profile 可以參與某個 `Campaign` 或後續 `Task`。在 `T012` 之後，系統已經有「裝置資料基礎」，下一步最合理的是讓 `Campaign` 能描述「合格裝置條件」。

本 ticket 的定位必須維持在 MVP 最小集合：

- 建立規則資料與關聯
- 讓 campaign 可以儲存與查看資格條件
- 不先做真正的 matching engine
- 不先做自動推薦 tester

本產品仍然是：

- 跨平台 Beta 測試媒合與回饋管理平台
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

建立 `Campaign` 對 `Tester Device Profile` 的最小資格條件規則（Eligibility Rule）表示方式，讓系統能先描述「什麼樣的裝置條件可參與某個 Campaign」，並提供對應的 backend CRUD / query 與 frontend shell 呈現。

本 ticket 完成後，應具備以下結果：

- backend 可管理最小 `eligibility_rules` 資源
- campaign 可關聯多筆 eligibility rules
- frontend 可在 `campaign detail` 下查看 eligibility rules shell
- 後續 `Task` 指派與條件檢查可在此基礎上延伸，但本 ticket 不先做自動篩選或推薦

## 3. 範圍

本 ticket 只做 MVP 最小集合，範圍如下：

- 建立 eligibility rules 的最小資料模型
- 建立 campaign 與 eligibility rules 的關聯
- 建立 backend CRUD / query
- 建立 frontend shell，優先掛在 `campaign detail` 下
- 建立 loading / empty / basic error state
- 建立對應 pytest 與 Playwright 測試

本 ticket 的規則表示方式固定如下：

- 一個 `Campaign` 可有 0..n 筆 eligibility rules
- 單一 rule 中，所有非空欄位採 AND 語意
- 多筆啟用中的 rules 之間只表示多個獨立條件集合，本 ticket 不實作真正匹配演算法

本 ticket 不定義：

- 複雜布林邏輯樹
- 動態規則編譯器
- 自動推薦 tester
- 自動媒合結果

## 4. 資料模型建議

### 4.1 Resource Shape

- `id`: `string`，系統產生
- `campaign_id`: `string`，required，建立後不可變
- `platform`: `"web" | "h5" | "pwa" | "ios" | "android"`，required
- `os_name`: `string | null`，optional
- `os_version_min`: `string | null`，optional
- `os_version_max`: `string | null`，optional
- `install_channel`: `string | null`，optional
- `is_active`: `boolean`，required，預設 `true`
- `created_at`: `string (ISO 8601)`，系統產生
- `updated_at`: `string (ISO 8601)`，系統產生

### 4.2 List / Detail / Create / Update Baseline

- List item：
  - `id`
  - `campaign_id`
  - `platform`
  - `os_name`
  - `install_channel`
  - `is_active`
  - `updated_at`
- Detail：
  - 使用完整 resource shape
- Create body：
  - `platform`
  - `os_name`
  - `os_version_min`
  - `os_version_max`
  - `install_channel`
  - `is_active`
- Update body：
  - 採 `PATCH`
  - 允許部分更新
  - `campaign_id` 不可更新

### 4.3 Validation Baseline

- `platform` 必填且只能是第一階段平台 enum
- `os_name`、`install_channel` 若提供，需做最小 normalization：
  - 去除前後空白
  - 空字串轉為 `null`
- `os_version_min` / `os_version_max` 在 MVP 階段先視為普通字串欄位
- 本 ticket 不實作語意化版本比較器（semantic version ordering）
- `is_active` 預設為 `true`

## 5. API 路徑建議

### 5.1 建議路徑

- `GET /api/v1/campaigns/{campaign_id}/eligibility-rules`
- `POST /api/v1/campaigns/{campaign_id}/eligibility-rules`
- `GET /api/v1/eligibility-rules/{eligibility_rule_id}`
- `PATCH /api/v1/eligibility-rules/{eligibility_rule_id}`
- `DELETE /api/v1/eligibility-rules/{eligibility_rule_id}`

### 5.2 API Baseline

- list response 使用：
  - `{ items, total }`
- detail / create / patch 成功時直接回 resource
- delete 預設回 `204 No Content`
- 錯誤格式至少包含：
  - `code`
  - `message`
  - `details`
- 找不到 `campaign_id` 或 `eligibility_rule_id` 時使用：
  - `resource_not_found`

## 6. 前端頁面 / 路由建議

### 6.1 Feature Placement

- `frontend/features/eligibility/`
  - `types.ts`
  - `api.ts`
  - 若需要單一模組 helper，與 feature 共置

### 6.2 Pages / Route Suggestion

- 優先擴充既有：
  - `frontend/pages/campaigns/[campaignId].vue`
- 在 `campaign detail` 下新增 eligibility rules section shell
- 如需 detail shell，新增：
  - `frontend/pages/campaigns/[campaignId]/eligibility-rules/[eligibilityRuleId].vue`

### 6.3 UI Shell Requirements

- `campaign detail` 可顯示 eligibility rules list section
- 至少顯示：
  - `platform`
  - `os_name`
  - `install_channel`
  - `is_active`
- 提供：
  - loading state
  - empty state
  - basic error state
- 補上穩定 selector，例如：
  - `data-testid="campaign-eligibility-list"`
  - `data-testid="campaign-eligibility-empty"`
  - `data-testid="eligibility-rule-detail-panel"`

## 7. Acceptance Criteria

- backend 已新增 `eligibility` 模組，並對齊既有 FastAPI 結構
- `campaigns` 可查詢與建立對應的 eligibility rules
- API path、response baseline、error baseline 符合 `API_CONVENTIONS.md`
- `eligibility` 命名符合 `ARCHITECTURE.md`
- frontend 已可在 `campaign detail` 顯示 eligibility rules shell
- frontend API 呼叫未散落在 `pages/` 中
- frontend 已包含 loading / empty / basic error state
- backend pytest 已補齊 validation / service / API 三層最小測試
- frontend Playwright 已補齊 eligibility rules shell-level E2E
- 本 ticket 未實作真正的 matching engine、複雜規則編譯器或動態 rule builder UI

## 8. Out of Scope

- 不實作真正的 matching engine
- 不實作複雜規則編譯器
- 不實作布林邏輯樹
- 不實作自動推薦 tester
- 不實作 auto matching
- 不實作 advanced form
- 不實作 admin 後台
- 不做多層條件巢狀 UI
- 不做正式 PostgreSQL migration 或 production-ready persistence

## 9. Backend Work Items

- 在 `backend/app/modules/` 下新增 `eligibility` 模組
- 採既有 backend module 慣例建立：
  - `router.py`
  - `schemas.py`
  - `service.py`
  - 視需要建立 `repository.py`
  - 視需要建立 `models.py`
- 將 router 註冊到既有 API router
- 先沿用 in-memory repository 策略，並清楚標示 restart 後資料會消失
- 建立 campaign 與 eligibility rules 的最小關聯驗證
- `POST /campaigns/{campaign_id}/eligibility-rules` 時必須驗證 campaign 存在
- `PATCH` 時不可修改 `campaign_id`

## 10. Frontend Work Items

- 在 `frontend/features/eligibility/` 下建立最小必要檔案
- 擴充 `campaign detail` 頁面，加入 eligibility rules list shell
- 如有需要，建立 eligibility rule detail shell 頁面
- 補最小 navigation / link，讓使用者可從 campaign detail 進入 rule detail
- 不建立 advanced form 或 rule builder UI
- 若需新增樣式，優先依照既有 SCSS / scoped style 判斷規則處理，不做大範圍視覺重構

## 11. Test Items

### 11.1 Backend Tests

- validation tests：
  - `platform` enum 驗證
  - optional string normalization
  - empty update payload 驗證
- service tests：
  - create / list / update / delete 基本流程
  - campaign not found error
  - rule not found error
- API tests：
  - nested list / create
  - detail / patch / delete
  - response shape 與 error shape 驗證

### 11.2 Frontend Tests

- 保持既有 typecheck / build 可通過
- 新增 eligibility section 不可破壞既有 campaign shell

### 11.3 E2E Tests

- 補 campaign detail 下 eligibility shell 的 Playwright 測試
- 至少覆蓋：
  - happy path list
  - empty state
  - error state
  - 若有 detail shell，補 detail happy path
- 建議沿用既有 route mocking 方式，避免把測試綁定 backend 啟動

## 12. Risk / Notes

- 本 ticket 只建立「條件資料表示」，不代表系統已具備條件運算或自動媒合能力
- `install_channel` 的完整 taxonomy 在 MVP 階段先不做嚴格 enum，避免太早綁死不同平台的分發模式
- `os_version_min / os_version_max` 先以字串欄位保存，不在這一票實作版本解析器
- eligibility rules 是 campaign 層條件，不應在本票中直接耦合 task 指派邏輯
- 命名需對齊：
  - frontend feature：`eligibility`
  - backend module：`eligibility`
  - API resource：`eligibility-rules`

## 13. 依賴關係（Dependencies）

主要依賴：

- `T012-tester-device-profile-crud-and-shell-flows`

延續既有基礎：

- `T005-api-and-project-conventions`
- `T007-projects-and-campaigns-backend-crud`
- `T008-projects-and-campaigns-frontend-shell`
- `T010-frontend-e2e-playwright`
- `T011-projects-and-campaigns-e2e-flows`
