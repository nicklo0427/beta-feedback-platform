# T027 - Feedback Review Status and Supplement Request

## 1. 背景

`Feedback` 現在已可提交與編輯，但 developer 還無法在系統中處理 feedback。

依照 `PRD.md` 的回饋處理流程，產品至少應支援：

- 待處理
- 需補充
- 已確認

目前這一段仍缺少最小資料欄位與 UI。若不補這塊，`feedback` 雖然能提交，卻仍停在單向輸入，無法形成最小的回饋處理閉環。

本票的目標，是建立最小 review workflow，而不是做完整客服工單系統。

## 2. 目標

建立 feedback 的最小 review workflow，讓 developer 能在 feedback detail 中：

- 標記 review 狀態
- 留下補充要求或處理註記

本票完成後，應具備以下結果：

- feedback detail 可顯示 review status
- developer 可更新 review status
- developer 可編輯最小 review note

## 3. 範圍

本票只做 MVP 最小集合，範圍如下：

- 擴充 feedback 最小欄位：
  - `review_status`
  - `developer_note`
- backend 補最小 patch 支援
- frontend 在 feedback detail 補 review panel
- 補 pytest 與 Playwright 測試

本票建議 review status 僅包含：

- `submitted`
- `needs_more_info`
- `reviewed`

## 4. 資料模型建議

### 4.1 Resource Shape Extension

在既有 feedback shape 上新增：

- `review_status`: `"submitted" | "needs_more_info" | "reviewed"`
- `developer_note`: `string | null`

### 4.2 Review Rules

- feedback create 時 `review_status` 預設為 `submitted`
- `developer_note` 選填
- `developer_note` 只代表最小補充要求或處理註記
- 不新增 threaded comments
- 不新增 tester / developer 雙向訊息流

### 4.3 Patch Baseline

延用既有 `PATCH /api/v1/feedback/{feedback_id}`，但允許更新：

- `review_status`
- `developer_note`

若其他既有欄位仍允許 update，應保持向後相容，不在本票中刪減既有 patch contract。

## 5. API 路徑建議

沿用既有 API：

- `PATCH /api/v1/feedback/{feedback_id}`
- `GET /api/v1/feedback/{feedback_id}`

本票不新增新 endpoint。

## 6. 前端頁面 / 路由建議

### 6.1 UI Placement

- 延用既有：
  - `frontend/pages/tasks/[taskId]/feedback/[feedbackId].vue`

### 6.2 UI Requirements

- 在 feedback detail 頁加入 review panel
- review panel 至少包含：
  - review status selector
  - developer note textarea
  - submit action
- 至少包含：
  - loading
  - submit pending
  - backend error
  - save success feedback
- 補穩定 selector，例如：
  - `data-testid="feedback-review-panel"`
  - `data-testid="feedback-review-status-field"`
  - `data-testid="feedback-developer-note-field"`
  - `data-testid="feedback-review-submit"`

### 6.3 Route Notes

- 不新增獨立 review route
- review panel 直接掛在 feedback detail 即可

## 7. Acceptance Criteria

- feedback detail 可顯示 `review_status`
- developer 可把 feedback 從 `submitted` 改為 `needs_more_info` 或 `reviewed`
- developer note 可顯示與更新
- 既有 feedback submit / edit flow 不被破壞
- backend validation / bad enum / not found path 完整
- frontend typecheck / build 可通過
- pytest 與 Playwright 已補齊最小 review workflow

## 8. Out of Scope

- 不做 threaded conversation
- 不做 notification
- 不做 moderation queue
- 不做 SLA / reviewer assignment
- 不做 attachments / screenshots
- 不做 bug 修復狀態追蹤

## 9. Backend Work Items

- 更新 feedback schema / service / API tests
- 定義 `review_status` 最小 allowed values
- `developer_note` 做最小 normalization
- 保持 in-memory strategy
- 不得順手擴成評論流或聊天系統

## 10. Frontend Work Items

- 在 feedback detail 頁新增 review panel
- 若需要，於 `frontend/features/feedback/` 補 review helper
- 明確區分：
  - tester submit / edit
  - developer review
- 保持 API 呼叫在 feature / service 層

## 11. Test Items

### 11.1 Backend Tests

- `review_status` 預設值
- review patch happy path
- bad enum validation
- not found error

### 11.2 Frontend Tests

- `npm run typecheck`
- `npm run build`

### 11.3 E2E Tests

- review happy path
- `needs_more_info` path
- backend validation / bad enum
- regression：feedback create / edit flow

## 12. Risk / Notes

- 這張票不應演變成完整客服工單系統
- `review_status` 只反映 feedback 處理狀態，不反映 bug 修復狀態
- 若需要樣式調整，應優先重用 detail 頁既有 section / form pattern

## 13. 依賴關係（Dependencies）

主要依賴：

- `T021-feedback-submit-and-edit-forms`

後續可支撐：

- `T028-local-demo-data-seeding-workflow`
- `T029-readme-and-manual-qa-docs-refresh`
