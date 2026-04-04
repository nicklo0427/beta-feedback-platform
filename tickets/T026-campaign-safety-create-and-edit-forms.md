# T026 - Campaign Safety Create and Edit Forms

## 1. 背景

`T017` 已讓 `campaign detail` 可以顯示 safety shell，但目前 safety 只能看，不能從 UI 建立或編輯。

這代表 safety 雖然已經有資料模型與顯示能力，卻仍停在工程可讀，不是產品可用。對產品定位來說，這是一個明顯缺口，因為「來源可辨識、風險可提示」不能只停留在只讀狀態。

本票的目標，是把 `Campaign Safety` 從只讀 shell 提升為可操作資料，但仍維持 MVP 最小集合，不做 moderation workflow。

## 2. 目標

讓開發者可在 campaign context 下建立或更新 `Campaign Safety`，把安全來源與風險提示從只讀 shell 提升為可操作資料。

本票完成後，應具備以下結果：

- `campaign detail` empty state 可進入 safety create
- `campaign detail` safety panel 可進入 safety edit
- create / edit 成功後可回到 `campaign detail`
- safety 顯示結果會立即反映更新後內容

## 3. 範圍

本票只做 MVP 最小集合，範圍如下：

- 新增 campaign safety create form
- 新增 campaign safety edit form
- 串接既有 nested singleton API
- create / edit 成功後回到 campaign detail
- 補 Playwright E2E

本票可操作欄位如下：

- `distribution_channel`
- `source_label`
- `source_url`
- `risk_level`
- `review_status`
- `official_channel_only`
- `risk_note`

## 4. 資料模型建議

### 4.1 Resource Shape

完全沿用 `T017` / `DATA_MODEL_DRAFT.md` 的 safety shape：

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

### 4.2 Form Baseline

- create form 不顯示可編輯的 `campaign_id`
- create / edit 皆在 campaign context 下進行
- edit form 使用 `PATCH`
- 若沒有任何欄位變更，應顯示最小提示

### 4.3 Validation Notes

- `distribution_channel` 必須為既有 enum
- `source_label` 必填
- `risk_level` 必須為既有 enum
- `review_status` 必須為既有 enum
- `official_channel_only` 使用 boolean 欄位
- `source_url` 與 `risk_note` 為選填
- backend 仍為最終 validation source of truth

### 4.4 MVP Decision

在 MVP 中允許直接編輯 `review_status`，因為目前沒有 admin / reviewer auth。

這是暫時性的產品化補強，不代表正式審核權限模型。

## 5. API 路徑建議

沿用既有 API：

- `GET /api/v1/campaigns/{campaign_id}/safety`
- `POST /api/v1/campaigns/{campaign_id}/safety`
- `PATCH /api/v1/campaigns/{campaign_id}/safety`
- `DELETE /api/v1/campaigns/{campaign_id}/safety`

本票不做 delete UI。

## 6. 前端頁面 / 路由建議

### 6.1 Feature Placement

- 延用既有：
  - `frontend/features/safety/`

### 6.2 Route Suggestion

- `frontend/pages/campaigns/[campaignId]/safety/new.vue`
- `frontend/pages/campaigns/[campaignId]/safety/edit.vue`

### 6.3 UI Requirements

- `campaign detail` 的 safety empty state 增加 `Create safety profile`
- `campaign detail` 的 safety panel 增加 `Edit safety profile`
- create / edit form 優先共用同一份 form component
- 至少包含：
  - loading
  - submit pending
  - validation / backend error
  - success redirect
- 補穩定 selector，例如：
  - `data-testid="campaign-safety-form"`
  - `data-testid="campaign-safety-submit"`
  - `data-testid="campaign-safety-form-error"`
  - `data-testid="campaign-safety-create-link"`
  - `data-testid="campaign-safety-edit-link"`

## 7. Acceptance Criteria

- campaign detail empty state 可進入 safety create
- safety create / edit 後可回到 campaign detail 並看到更新結果
- source URL、risk fields、review fields 可正常顯示與更新
- validation / conflict / not found path 完整
- frontend API 呼叫未散落在 `pages/` 中
- frontend typecheck / build 可通過
- Playwright 已補齊 safety form 的最小流程測試
- 現有 safety shell 與 reputation section 不受影響

## 8. Out of Scope

- 不做 admin review console
- 不做附件掃描
- 不做自動審核
- 不做 source URL 可用性檢查
- 不做 safety history / audit timeline UI
- 不做 delete UI

## 9. Backend Work Items

本票原則上不新增新 API，僅允許最小修補：

- 若既有 `safety` API 已足夠，backend 不應新增 endpoint
- 只允許最小修補，例如：
  - 404 / conflict message 一致性
  - payload normalization 缺口
- 不得順手擴成 moderation workflow

## 10. Frontend Work Items

- 在 `frontend/features/safety/` 中新增 form helper
- 建立共用 `CampaignSafetyForm` component
- 新增 create / edit route 與 CTA
- 共用既有 form / state pattern
- 與 `campaign detail` 既有 safety section 串接

## 11. Test Items

### 11.1 Frontend Tests

- `npm run typecheck`
- `npm run build`

### 11.2 E2E Tests

- safety create happy path
- safety edit happy path
- duplicate create / backend conflict
- not found / backend error

### 11.3 Regression Focus

- `campaign detail` safety shell 不可被破壞
- `campaign detail` 既有 reputation / eligibility / tasks section 不可被破壞

## 12. Risk / Notes

- 這張票不要擴成 moderation workflow
- `review_status` 只是 MVP 欄位，不代表正式審核權限模型
- 若需要新增樣式，應優先重用既有 form pattern；不要為 safety form 開新的全域設計語言

## 13. 依賴關係（Dependencies）

主要依賴：

- `T017-campaign-safety-source-labeling-and-risk-flags`

建議依賴：

- `T025-campaign-create-and-edit-forms`

後續可支撐：

- `T028-local-demo-data-seeding-workflow`
- `T029-readme-and-manual-qa-docs-refresh`
