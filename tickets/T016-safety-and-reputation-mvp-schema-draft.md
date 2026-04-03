# T016 - Safety and Reputation MVP Schema Draft

## 1. 背景

目前專案已完成 `T011` 到 `T015`，MVP 核心主流程已形成最小閉環：

- `Project -> Campaign -> Device Profile -> Eligibility -> Task -> Feedback`

這代表專案已從「主流程骨架建立」進入「產品化補強」階段。接下來若要讓產品真正符合 PRD 中的定位，最缺的不是再開新的核心 domain，而是補足：

- 安全與來源標示（Safety Layer）
- 雙向信譽基礎（Reputation Baseline）

這兩塊都已在 `PRD.md` 中明確存在，但 repo 目前尚未有可直接落地的 MVP schema draft。若沒有先定義清楚資料邊界與責任歸屬，後續很容易發生：

- safety 欄位零散地長在 `campaigns / tasks / feedback` 中
- reputation 指標各票各自解讀，無法形成一致 contract
- frontend / backend 對安全與信譽的資料 shape 理解不一致

因此，本票的角色是文件先行：先把 `Safety` 與 `Reputation` 的 MVP 最小資料草案定清楚，讓後續功能票可以直接引用。

## 2. 目標

建立 `Safety Layer` 與 `Reputation` 的 MVP schema draft，作為後續：

- `T017-campaign-safety-source-labeling-and-risk-flags`
- `T022-reputation-baseline-and-summary-metrics`

的直接依據。

本票完成後，應具備以下結果：

- 已明確定義 `Safety` 與 `Reputation` 的最小資料模型與責任邊界
- 已定義其與既有 `Campaign / Device Profile / Task / Feedback` 的關聯方式
- 已定義未來 API path 與 frontend 掛載位置的 baseline
- 已明確指出哪些能力屬於 MVP，哪些必須延後

## 3. 範圍

本票只做文件與 schema draft，不做 runtime 實作。範圍如下：

- 定義 `Campaign Safety` 的 MVP 最小欄位
- 定義 `Tester-side Reputation Summary` 的 MVP 最小欄位
- 定義 `Campaign-side Collaboration Summary` 的 MVP 最小欄位
- 定義 `Safety` 與 `Reputation` 的資源責任邊界
- 定義建議 API 路徑與 frontend 掛載位置
- 明確標示未來實作票的前置共識

本票應優先更新或補充：

- `DATA_MODEL_DRAFT.md`
- 視需要補充 `PRD.md` 中對 safety / reputation 的措辭一致性

## 4. 資料模型建議

### 4.1 Safety Layer Boundary

`Safety` 在 MVP 階段應先掛在 `Campaign` 層，而不是 `Project` 或 `Task` 層。

判斷理由：

- 安全來源與分發方式通常跟「某一輪測試活動」直接相關
- 同一個 `Project` 可以有不同分發方式與不同風險等級的 `Campaign`
- 若把 safety 直接掛在 `Task`，會把來源資訊切得過細，造成維護成本上升

因此，MVP 階段的 `Safety` 採：

- 一個 `Campaign` 對應 0..1 筆 `Campaign Safety Profile`

### 4.2 Campaign Safety Resource Shape

- `id`: `string`，系統產生
- `campaign_id`: `string`，required，建立後不可變
- `distribution_channel`: `"web_url" | "pwa_url" | "testflight" | "google_play_testing" | "manual_invite" | "other"`，required
- `source_label`: `string`，required，用於顯示來源名稱
- `source_url`: `string | null`，optional
- `risk_level`: `"low" | "medium" | "high"`，required
- `review_status`: `"pending" | "approved" | "rejected"`，required
- `official_channel_only`: `boolean`，required，預設 `false`
- `risk_note`: `string | null`，optional
- `created_at`: `string (ISO 8601)`，系統產生
- `updated_at`: `string (ISO 8601)`，系統產生

### 4.3 Safety Interpretation Rules

- `distribution_channel` 用來描述本輪測試主要分發方式
- `source_label` 用來顯示人類可理解的來源名稱，例如 TestFlight、Google Play Closed Testing、官方測試站點
- `source_url` 為可選欄位，不要求所有平台都必須提供
- `risk_level` 用於最小風險提示，不代表完整安全審核系統
- `review_status` 用於最小人工審核狀態，不代表完整 moderation workflow
- `official_channel_only = true` 時，代表本活動預期只允許官方或官方授權的分發方式

### 4.4 Reputation Boundary

在沒有完整帳號系統與 ownership model 的前提下，MVP 階段不適合直接做完整「雙向個人信譽」。

因此，第一版 reputation baseline 應採務實 anchor：

- Tester-side reputation：先掛在 `device_profile_id`
- Developer-side collaboration summary：先掛在 `campaign_id`

這是暫時的 MVP anchor，不代表未來正式帳號模型的最終設計。

### 4.5 Tester Reputation Summary Shape

- `device_profile_id`: `string`
- `tasks_assigned_count`: `number`
- `tasks_submitted_count`: `number`
- `feedback_submitted_count`: `number`
- `submission_rate`: `number`，0..1
- `last_feedback_at`: `string | null`
- `updated_at`: `string (ISO 8601)`

### 4.6 Campaign Collaboration Summary Shape

- `campaign_id`: `string`
- `tasks_total_count`: `number`
- `tasks_closed_count`: `number`
- `feedback_received_count`: `number`
- `closure_rate`: `number`，0..1
- `last_feedback_at`: `string | null`
- `updated_at`: `string (ISO 8601)`

### 4.7 Deferred Fields

以下欄位在 MVP 階段先不納入：

- 安全附件掃描結果
- 惡意來源歷史紀錄
- 人工審核人員資訊
- 詳細 reputation score formula
- badge / tier / ranking
- dispute / arbitration workflow
- public profile reputation feed

## 5. API 路徑建議

本票不實作 API，但應先定義後續路徑 baseline。

### 5.1 Safety

- `GET /api/v1/campaigns/{campaign_id}/safety`
- `POST /api/v1/campaigns/{campaign_id}/safety`
- `PATCH /api/v1/campaigns/{campaign_id}/safety`
- `DELETE /api/v1/campaigns/{campaign_id}/safety`

### 5.2 Reputation

- `GET /api/v1/device-profiles/{device_profile_id}/reputation`
- `GET /api/v1/campaigns/{campaign_id}/reputation`

### 5.3 API Notes

- `Safety` 可視為 campaign 的 0..1 nested resource
- `Reputation` 第一版採 read-only summary，不提供 create / patch
- response / error format 仍需遵守 `API_CONVENTIONS.md`

## 6. 前端頁面 / 路由建議

本票不建立新頁面，但應先定義掛載位置，避免後續漂移。

### 6.1 Safety

- 優先掛在 `frontend/pages/campaigns/[campaignId].vue`
- 不需要先建立獨立 list 頁
- 若後續需要 detail/edit flow，可考慮：
  - `/campaigns/[campaignId]/safety`
  - `/campaigns/[campaignId]/safety/edit`

### 6.2 Reputation

- `Tester-side reputation` 優先掛在 `frontend/pages/device-profiles/[deviceProfileId].vue`
- `Campaign-side collaboration summary` 優先掛在 `frontend/pages/campaigns/[campaignId].vue`
- 第一版不需要獨立 reputation dashboard

## 7. Acceptance Criteria

- 已明確定義 `Campaign Safety` 的 MVP 欄位與責任邊界
- 已明確定義 `Tester Reputation Summary` 與 `Campaign Collaboration Summary` 的 MVP 欄位
- 已明確指出第一版 reputation 的 anchor 為 `device_profile_id` 與 `campaign_id`
- 已定義建議 API path baseline
- 已定義 frontend 掛載位置 baseline
- 已明確列出哪些能力不屬於 MVP
- 文件內容足以讓 `T017` 與 `T022` 直接依據本票實作

## 8. Out of Scope

- 不實作 backend module
- 不實作 frontend shell
- 不實作 moderation workflow
- 不實作完整審核工作台
- 不實作完整雙向個人 reputation 系統
- 不實作 badge / ranking / score engine
- 不實作附件掃描或安全檢測整合

## 9. Backend Work Items

本票不直接實作 backend runtime，但需為後續 backend work 提供清楚依據：

- 定義 `safety` module 的最小資源邊界
- 定義 `reputation` module 的 read-only summary 邊界
- 明確指出 `Safety` 與 `Campaign` 的一對一關聯
- 明確指出 `Reputation` 第一版使用 derived metrics，而非獨立手動寫入資料

## 10. Frontend Work Items

本票不直接實作 frontend runtime，但需為後續 frontend work 提供清楚依據：

- `campaign detail` 應承接 safety section
- `device profile detail` 與 `campaign detail` 應承接 reputation summary section
- 第一版不建立獨立 safety / reputation app 區域

## 11. Test Items

本票不新增 runtime 測試，但文件應明確指出後續測試方向：

- `T017` 應補 backend validation / service / API tests 與 frontend shell E2E
- `T022` 應補 derived metrics correctness tests 與 summary shell E2E

## 12. Risk / Notes

- 若先不定義 safety / reputation 邊界，後續實作極容易分散在多個模組內，造成責任模糊
- 第一版 reputation anchor 採 `device_profile_id` 與 `campaign_id` 只是 MVP 務實策略，未來若帳號系統完成，可能需要重新映射
- `Safety` 與 `Reputation` 都應保持最小集合，避免過早變成獨立的大型子系統

## 13. 依賴關係（Dependencies）

主要依賴：

- `T012-tester-device-profile-crud-and-shell-flows`
- `T013-campaign-eligibility-filter-rules`
- `T014-task-assignment-and-task-status-flow`
- `T015-structured-feedback-submission`

後續直接依賴本票的實作票：

- `T017-campaign-safety-source-labeling-and-risk-flags`
- `T022-reputation-baseline-and-summary-metrics`
