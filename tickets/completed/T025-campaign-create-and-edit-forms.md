# T025 - Campaign Create and Edit Forms

## 1. 背景

`Campaign` 已有 backend CRUD、frontend shell 與 detail 內嵌區塊，但目前仍無法從 UI 真正建立或修改。

相較於 `Project`，`Campaign` 是測試流程的真正操作核心。若沒有這張票，開發者雖然能看到 campaign shell，卻仍無法從產品入口建立一輪實際活動，也無法調整目標平台、版本與活動狀態。

本票的定位，是把 `Project -> Campaign` 這段上游主流程真正接通，但仍維持 MVP 最小集合，不做 global wizard 或複雜多步驟表單。

## 2. 目標

建立 `Campaign` create / edit flow，讓 `Project -> Campaign` 的上游主流程可被實際操作。

本票完成後，應具備以下結果：

- 可從 `project detail` 建立 campaign
- 可從 `campaign detail` 編輯 campaign
- target platforms 可透過 UI 設定
- 成功建立或更新後可回到對應 detail 頁

## 3. 範圍

本票只做 MVP 最小集合，範圍如下：

- 新增 campaign create form
- 新增 campaign edit form
- create flow 固定從 `project context` 進入
- 串接既有 `POST /api/v1/campaigns`
- 串接既有 `PATCH /api/v1/campaigns/{campaign_id}`
- 補 Playwright form-level E2E

本票可操作欄位如下：

- `name`
- `description`
- `target_platforms`
- `version_label`
- `status`

`project_id` 由 route context 提供，不手填。

## 4. 資料模型建議

### 4.1 Resource Shape

沿用既有 `Campaign` contract：

- `id`
- `project_id`
- `name`
- `description`
- `target_platforms`
- `version_label`
- `status`
- `created_at`
- `updated_at`

### 4.2 Form Baseline

- create form 不顯示可編輯的 `project_id`
- create form 由 route context 固定 `project_id`
- edit form 使用 `PATCH`
- edit form 不允許修改 `project_id`
- 若沒有任何欄位變更，應顯示最小提示

### 4.3 Platform Display Rules

- backend / API value 維持：
  - `web`
  - `h5`
  - `pwa`
  - `ios`
  - `android`
- frontend 顯示層應使用：
  - `Web`
  - `Mobile Web`
  - `PWA`
  - `iOS`
  - `Android`

### 4.4 Validation Notes

- `name` 必填
- `target_platforms` 至少需有一個值
- `status` create 時若 backend 已有預設，frontend 可顯示預設值說明
- backend 仍為最終 validation source of truth

## 5. API 路徑建議

沿用既有 API：

- `POST /api/v1/campaigns`
- `PATCH /api/v1/campaigns/{campaign_id}`
- `GET /api/v1/campaigns/{campaign_id}`

本票不新增新 API。

## 6. 前端頁面 / 路由建議

### 6.1 Feature Placement

- 延用既有：
  - `frontend/features/campaigns/`

### 6.2 Route Suggestion

- `frontend/pages/projects/[projectId]/campaigns/new.vue`
- `frontend/pages/campaigns/[campaignId]/edit.vue`

### 6.3 UI Requirements

- `project detail` 增加 `Create campaign` CTA
- `campaign detail` 增加 `Edit campaign` CTA
- create / edit form 優先共用同一份 form component
- 至少包含：
  - loading
  - submit pending
  - validation / backend error
  - success redirect
- 補穩定 selector，例如：
  - `data-testid="campaign-form"`
  - `data-testid="campaign-submit"`
  - `data-testid="campaign-form-error"`
  - `data-testid="campaign-create-link"`
  - `data-testid="campaign-edit-link"`

## 7. Acceptance Criteria

- 可從 `project detail` 建立 campaign
- create 成功後可導到 campaign detail
- 可從 `campaign detail` 編輯 campaign
- edit 成功後可回到 campaign detail
- target platforms 顯示文案使用 `Mobile Web`
- backend validation / not found 錯誤可顯示
- frontend API 呼叫未散落在 `pages/` 中
- frontend typecheck / build 可通過
- Playwright 已補齊 campaign form 的最小流程測試
- 既有 campaign detail 內嵌 safety / eligibility / tasks / reputation section 不被破壞

## 8. Out of Scope

- 不做 global campaign wizard
- 不做 project selector 搜尋
- 不做 scheduling / launch planner
- 不做 advanced multi-step form
- 不做 safety 欄位編輯
- 不做 task create

## 9. Backend Work Items

本票原則上不擴 backend domain，僅允許極小必要配合：

- 若既有 campaign API 已足夠，backend 不應新增 endpoint
- 若表單 flow 發現 contract 缺口，只允許最小修補
- 不得順手重構 `campaigns` module

## 10. Frontend Work Items

- 在 `frontend/features/campaigns/` 中新增 form helper
- 建立共用 `CampaignForm` component
- 新增 create / edit route
- create flow 中固定吃 `projectId`
- 使用既有 `formatPlatformLabel` 做顯示層 mapping
- 重用既有共用 SCSS form pattern

## 11. Test Items

### 11.1 Frontend Tests

- `npm run typecheck`
- `npm run build`

### 11.2 E2E Tests

- create happy path
- target_platforms validation / backend error
- edit happy path
- edit not found / backend error

### 11.3 Regression Focus

- 既有 campaign shell 不可被破壞
- 既有 project detail related campaigns 區塊不可被破壞

## 12. Risk / Notes

- 這張票的 create 入口必須只走 project context，避免 MVP 太早做全域選擇器
- 表單欄位不新增 `Safety`，那是下一張票
- 若需要新增樣式，需先判斷是共用表單樣式還是單頁微調，不可無理由擴大全域 SCSS

## 13. 依賴關係（Dependencies）

建議依賴：

- `T024-project-create-and-edit-forms`
- 既有 `T007-projects-and-campaigns-backend-crud`
- 既有 `T008-projects-and-campaigns-frontend-shell`

後續可支撐：

- `T026-campaign-safety-create-and-edit-forms`
- `T028-local-demo-data-seeding-workflow`
