# T024 - Project Create and Edit Forms

## 1. 背景

`projects` 目前已有 backend CRUD 與 frontend list / detail shell，但還沒有 create / edit form。

這使得目前產品雖然已能顯示 `Project` 清單與 detail，卻仍缺少最上游的可操作入口。若沒有這張票，使用者就無法從 UI 正常開始建立第一筆上游資料，仍需要：

- 手動打 API
- 使用本地 seed
- 依賴工程階段的暫時資料

在 `T011` 到 `T023` 之後，專案已完成主流程與第一輪產品化補強，下一步最合理的是補上最上游的表單流程，讓整條流程真正從 UI 可操作。

## 2. 目標

讓使用者可從 frontend 建立與編輯 `Project`，形成最小可操作 flow：

- `/projects`
- create
- detail
- edit
- detail

本票完成後，應具備以下結果：

- 可從 `projects list` 建立新 project
- 可從 `project detail` 編輯既有 project
- frontend 表單已串接既有 backend CRUD
- create / edit 成功後可回到對應 detail 頁

## 3. 範圍

本票只做 MVP 最小集合，範圍如下：

- 建立 `Project` create form
- 建立 `Project` edit form
- 串接既有 `POST /api/v1/projects`
- 串接既有 `PATCH /api/v1/projects/{project_id}`
- 補 create / edit 成功後的 redirect
- 補最小 validation / backend error 顯示
- 補 Playwright form-level E2E

本票不新增新欄位，完全沿用既有 `Project` 欄位：

- `name`
- `description`

## 4. 資料模型建議

### 4.1 Resource Shape

沿用既有 `Project` contract：

- `id`
- `name`
- `description`
- `created_at`
- `updated_at`

### 4.2 Form Baseline

- create form 使用：
  - `name`
  - `description`
- edit form 使用 `PATCH`
- edit form 只送出有變更的欄位
- 若沒有任何欄位變更，應顯示最小提示，例如：
  - `No changes to save yet.`

### 4.3 Validation Notes

- `name` 必填
- `description` 選填
- 前端只做最小欄位層級驗證
- backend 仍為最終 validation source of truth

## 5. API 路徑建議

沿用既有 API：

- `POST /api/v1/projects`
- `PATCH /api/v1/projects/{project_id}`
- `GET /api/v1/projects/{project_id}`

本票不新增新 API。

## 6. 前端頁面 / 路由建議

### 6.1 Feature Placement

- 延用既有：
  - `frontend/features/projects/`

### 6.2 Route Suggestion

- `frontend/pages/projects/new.vue`
- `frontend/pages/projects/[projectId]/edit.vue`

### 6.3 UI Requirements

- `projects list` 增加 `Create project` CTA
- `project detail` 增加 `Edit project` CTA
- create / edit form 優先重用同一份 form component
- 至少包含：
  - loading
  - submit pending
  - validation / backend error
  - success redirect
- 補穩定 selector，例如：
  - `data-testid="project-form"`
  - `data-testid="project-submit"`
  - `data-testid="project-form-error"`
  - `data-testid="project-create-link"`
  - `data-testid="project-edit-link"`

## 7. Acceptance Criteria

- 可從 `/projects` 進入 create flow
- create 成功後導到新建的 project detail
- 可從 `project detail` 進入 edit flow
- edit 成功後回到 project detail
- backend validation / not found 錯誤可在 form 中顯示
- frontend API 呼叫未散落在 `pages/` 中
- frontend typecheck / build 可通過
- Playwright 已補齊 project form 的最小流程測試
- 不新增新 backend API

## 8. Out of Scope

- 不做 delete UI
- 不做 advanced form
- 不做 autosave
- 不做 project status
- 不做 tags
- 不做 owner fields
- 不做 batch create

## 9. Backend Work Items

本票原則上不擴 backend domain，僅允許極小必要配合：

- 若既有 CRUD 已足夠，backend 不應新增新 API
- 若 form flow 遇到 payload 或錯誤訊息缺口，只允許最小修補
- 不得順手重構 `projects` module

## 10. Frontend Work Items

- 在 `frontend/features/projects/` 中新增最小 form helper
- 建立共用 `ProjectForm` component
- 新增 create / edit route
- 將 API 呼叫維持在 feature / service 層
- 讓 list / detail 頁面提供清楚入口
- 重用既有共用 SCSS form pattern，不新開大型樣式系統

## 11. Test Items

### 11.1 Frontend Tests

- `npm run typecheck`
- `npm run build`

### 11.2 E2E Tests

- create happy path
- create validation error
- create backend error
- edit happy path
- edit not found / backend error

### 11.3 Regression Focus

- 既有 `/projects` list / detail shell 不可被破壞
- 首頁進入 `Projects` 的入口需持續可用

## 12. Risk / Notes

- 這張票不應順手補 `Campaign` create / edit
- create / edit form 應共享同一組欄位與互動規則
- 若需要新增樣式，必須先判斷：
  - 有跨頁共用價值的 form / action pattern 才放 `assets/scss`
  - 只屬於 project form 的局部微調才放 `.vue` scoped style

## 13. 依賴關係（Dependencies）

主要依賴：

- `T007-projects-and-campaigns-backend-crud`
- `T008-projects-and-campaigns-frontend-shell`

後續可支撐：

- `T025-campaign-create-and-edit-forms`
- `T028-local-demo-data-seeding-workflow`
- `T029-readme-and-manual-qa-docs-refresh`
