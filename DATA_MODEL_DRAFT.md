# beta-feedback-platform Data Model Draft

## 1. Purpose

本文件定義 `beta-feedback-platform` 在 MVP 階段的核心資料欄位草案，先以 `Project / Campaign` 為起點，並逐步補入下一階段產品化補強所需的 `Safety Layer` 與 `Reputation` baseline，作為後續：

- `T007-projects-and-campaigns-backend-crud`
- `T008-projects-and-campaigns-frontend-shell`
- `T017-campaign-safety-source-labeling-and-risk-flags`
- `T022-reputation-baseline-and-summary-metrics`

的直接依據。

本文件只處理 MVP 最小資料模型，不處理：

- 資料庫 migration
- auth / ownership / RBAC
- 完整商業規則
- Task / Feedback 的完整資料模型細節
- Safety 的完整審核工作流
- Reputation 的完整評分公式或公開排名規則

## 2. Modeling Principles

### 2.1 Naming

- API-facing 欄位一律使用 `snake_case`
- path 使用 `kebab-case`
- backend schema 與 frontend type 先以同一組欄位名稱對齊，避免前期建立額外轉換層

### 2.2 Identifier

- `project_id`、`campaign_id` 採 API-facing opaque string
- 本文件不限制底層實作一定是 UUID、database integer 或其他格式
- 對外只要求其為穩定、可唯一識別的字串

### 2.3 Timestamp

- API response 的時間欄位一律使用 ISO 8601 字串
- MVP 階段只使用：
  - `created_at`
  - `updated_at`

### 2.4 Scope Discipline

- `Project` 代表產品或測試主體
- `Campaign` 代表某個測試批次 / 版本 / 招募活動
- `Campaign` 不能替代 `Task`
- `Campaign` 不能替代 `Feedback`

## 3. Project / Campaign Responsibility Boundary

### 3.1 Project Represents

`Project` 應承載：

- 穩定存在的產品主體
- 給開發者辨識該產品或測試主題的基本資訊
- 多個 Campaign 的共同歸屬容器

換句話說，Project 是「我們在測哪一個產品 / 服務 / 主體」。

### 3.2 Campaign Represents

`Campaign` 應承載：

- 某一次具體的測試批次
- 某個版本或 build 的招募活動
- 某一組平台範圍與活動狀態

換句話說，Campaign 是「這一輪要怎麼測、測哪個版本、現在招募是否開放」。

### 3.3 Boundary Summary Table

| 項目 | 屬於 Project | 屬於 Campaign | 判斷理由 |
| --- | --- | --- | --- |
| 產品主體名稱 | Yes | No | 穩定辨識產品主體 |
| 產品主體描述 | Yes | No | 屬於產品層資訊 |
| 測試批次名稱 | No | Yes | 屬於單次活動 |
| 版本標記 | No | Yes | 不同 Campaign 可對應不同版本 |
| 目標平台 | No | Yes | 同一 Project 可有不同平台組合的 Campaign |
| 招募狀態 | No | Yes | 活動狀態屬於 Campaign，不屬於產品主體 |
| 測試任務步驟 | No | No | 應由 Task 模組承載 |
| 結構化問題回報 | No | No | 應由 Feedback 模組承載 |

## 4. Project Schema Draft

### 4.1 Project Fields

| Field | Type | Category | Used In | MVP | Purpose / Notes |
| --- | --- | --- | --- | --- | --- |
| `id` | `string` | 系統產生 | list, detail | Yes | Project 的對外識別碼 |
| `name` | `string` | 必填 | list, detail, create, update | Yes | 產品 / 測試主體名稱 |
| `description` | `string \| null` | 選填 | list, detail, create, update | Yes | 對產品主體的簡要說明；不作為活動說明 |
| `created_at` | `string (ISO 8601)` | 系統產生 | detail | Yes | 建立時間 |
| `updated_at` | `string (ISO 8601)` | 系統產生 | list, detail | Yes | 最後更新時間 |

### 4.2 Project Create Payload

`Project` create body 最小欄位：

- `name`：required
- `description`：optional

範例：

```json
{
  "name": "HabitQuest",
  "description": "Cross-platform habit tracking app beta program."
}
```

### 4.3 Project Update Payload

`Project` update body 最小欄位：

- `name`：optional
- `description`：optional

規則：

- 採 `PATCH`
- 不要求完整資源快照

### 4.4 Project List vs Detail

Project list 預設欄位：

- `id`
- `name`
- `description`
- `updated_at`

Project detail 預設欄位：

- `id`
- `name`
- `description`
- `created_at`
- `updated_at`

### 4.5 Project Deferred Fields

以下欄位目前先不納入 MVP：

- `owner_id`
- `status`
- `tags`
- `default_platforms`
- `visibility`
- `website_url`
- `store_urls`

判斷理由：

- `owner_id` 與 auth / ownership 有關，目前不做
- `status` 目前不是最小必要條件，活動狀態由 Campaign 承接
- `default_platforms` 容易與 Campaign 的 `target_platforms` 重疊
- 其他欄位都不屬於現階段最小 CRUD / shell 所需資訊

## 5. Campaign Schema Draft

### 5.1 Campaign Fields

| Field | Type | Category | Used In | MVP | Purpose / Notes |
| --- | --- | --- | --- | --- | --- |
| `id` | `string` | 系統產生 | list, detail | Yes | Campaign 對外識別碼 |
| `project_id` | `string` | 必填 | list, detail, create | Yes | 所屬 Project 識別碼；建立後視為不可變 |
| `name` | `string` | 必填 | list, detail, create, update | Yes | 單次測試活動名稱 |
| `description` | `string \| null` | 選填 | detail, create, update | Yes | 活動說明或本輪測試摘要；不承載任務步驟 |
| `target_platforms` | `string[]` | 必填 | list, detail, create, update | Yes | 本輪活動要招募的目標平台集合 |
| `version_label` | `string \| null` | 選填 | list, detail, create, update | Yes | 版本 / build / milestone 標記；某些 Web 測試可留空 |
| `status` | `"draft" \| "active" \| "closed"` | 系統預設 / 可更新 | list, detail, update | Yes | 招募活動狀態；create 預設為 `draft` |
| `created_at` | `string (ISO 8601)` | 系統產生 | detail | Yes | 建立時間 |
| `updated_at` | `string (ISO 8601)` | 系統產生 | list, detail | Yes | 最後更新時間 |

### 5.2 Allowed `target_platforms`

MVP 第一階段僅允許以下值：

- `web`
- `h5`
- `pwa`
- `ios`
- `android`

註：

- 對外產品文案與前端顯示建議使用 `Mobile Web`
- 目前 internal / API value 暫維持 `h5`，以相容既有實作

### 5.3 Campaign Create Payload

`Campaign` create body 最小欄位：

- `project_id`：required
- `name`：required
- `description`：optional
- `target_platforms`：required
- `version_label`：optional

規則：

- `status` 不要求 create 時由 client 傳入
- backend 預設建立為 `draft`

範例：

```json
{
  "project_id": "proj_123",
  "name": "Closed Beta Round 1",
  "description": "Collect early usability feedback for the onboarding flow.",
  "target_platforms": ["ios", "android"],
  "version_label": "0.9.0-beta.1"
}
```

### 5.4 Campaign Update Payload

`Campaign` update body 最小欄位：

- `name`：optional
- `description`：optional
- `target_platforms`：optional
- `version_label`：optional
- `status`：optional

規則：

- 採 `PATCH`
- `project_id` 不在 update body 中提供

判斷理由：

- Campaign 一旦建立，即屬於某個 Project
- 後續若要允許跨 Project 移動 Campaign，會牽涉資料一致性與 UI 流程複雜度
- MVP 階段先不支援

### 5.5 Campaign List vs Detail

Campaign list 預設欄位：

- `id`
- `project_id`
- `name`
- `target_platforms`
- `version_label`
- `status`
- `updated_at`

Campaign detail 預設欄位：

- `id`
- `project_id`
- `name`
- `description`
- `target_platforms`
- `version_label`
- `status`
- `created_at`
- `updated_at`

### 5.6 Campaign Deferred Fields

以下欄位目前先不納入 MVP：

- `instructions`
- `task_count`
- `feedback_count`
- `eligibility_rules`
- `max_testers`
- `starts_at`
- `ends_at`
- `build_url`
- `download_url`
- `reward_description`

判斷理由：

- `instructions` 應由 Task 模組承接，避免 Campaign 變成任務容器
- `feedback_count`、`task_count` 屬於衍生資訊，可後補
- `eligibility_rules` 屬於 Eligibility Filter 模組，不應塞進 Campaign 基礎模型
- `max_testers`、`starts_at`、`ends_at` 雖然合理，但不是目前最小 CRUD / shell 的必要欄位
- `build_url`、`download_url` 牽涉平台分發與安全標示，後續應與 Safety Layer 一起設計
- `reward_description` 不屬於現階段 MVP 最小需求

## 6. API Field Subsets for T007 / T008

### 6.1 Project

#### List Item

```json
{
  "id": "proj_123",
  "name": "HabitQuest",
  "description": "Cross-platform habit tracking app beta program.",
  "updated_at": "2026-04-03T10:00:00Z"
}
```

#### Detail

```json
{
  "id": "proj_123",
  "name": "HabitQuest",
  "description": "Cross-platform habit tracking app beta program.",
  "created_at": "2026-04-01T09:00:00Z",
  "updated_at": "2026-04-03T10:00:00Z"
}
```

#### Create Body

```json
{
  "name": "HabitQuest",
  "description": "Cross-platform habit tracking app beta program."
}
```

#### Update Body

```json
{
  "description": "Updated project summary."
}
```

### 6.2 Campaign

#### List Item

```json
{
  "id": "camp_123",
  "project_id": "proj_123",
  "name": "Closed Beta Round 1",
  "target_platforms": ["ios", "android"],
  "version_label": "0.9.0-beta.1",
  "status": "active",
  "updated_at": "2026-04-03T10:00:00Z"
}
```

#### Detail

```json
{
  "id": "camp_123",
  "project_id": "proj_123",
  "name": "Closed Beta Round 1",
  "description": "Collect early usability feedback for the onboarding flow.",
  "target_platforms": ["ios", "android"],
  "version_label": "0.9.0-beta.1",
  "status": "active",
  "created_at": "2026-04-02T09:00:00Z",
  "updated_at": "2026-04-03T10:00:00Z"
}
```

#### Create Body

```json
{
  "project_id": "proj_123",
  "name": "Closed Beta Round 1",
  "description": "Collect early usability feedback for the onboarding flow.",
  "target_platforms": ["ios", "android"],
  "version_label": "0.9.0-beta.1"
}
```

#### Update Body

```json
{
  "status": "closed"
}
```

## 7. Ambiguous Field Decisions

### 7.1 Why `target_platforms` Belongs to Campaign

判斷：

- 同一個 Project 在不同階段可以只測 `ios`
- 也可以下一輪改測 `web + pwa`

因此 `target_platforms` 是活動層欄位，不是產品主體欄位。

### 7.2 Why `version_label` Belongs to Campaign

判斷：

- Project 是長期存在的產品主體
- `version_label` 對應某次測試批次或某版 build

因此應放在 Campaign。

### 7.3 Why Project Does Not Have `status` in MVP

判斷：

- 目前最需要管理狀態的是招募活動本身，而不是產品主體
- Campaign 的 `status` 已能支持招募開放 / 關閉等最小流程
- 若 Project 也同時有 `status`，容易提早引入兩層狀態管理複雜度

因此 Project 的 `status` 暫不納入 MVP。

### 7.4 Why Campaign Does Not Carry Task Instructions

判斷：

- Campaign 只描述本輪活動
- 測試步驟、驗收項目、提交要求應由 Task 模組承接

若把詳細測試說明直接放入 Campaign，會讓 Campaign 演變成 Task 替代模型，因此不納入。

## 8. Usage Notes for Next Tickets

### 8.1 For T007 Backend CRUD

- request / response 欄位應直接對齊本文件
- API-facing 欄位名稱維持 `snake_case`
- `project_id` 在 Campaign create 時必填，在 update 時不可修改
- `status` 可先採簡單 enum 驗證

### 8.2 For T008 Frontend Shell

- frontend type 應直接對齊本文件欄位命名
- mock data / placeholder API 應使用與本文件一致的 field shape
- list 頁與 detail 頁應依本文件的欄位子集呈現，不要自行擴欄

### 8.3 For T017 Campaign Safety

- `Campaign Safety` 應視為 campaign 的 0..1 nested resource
- safety 欄位應直接對齊本文件的 `snake_case` 命名
- `distribution_channel`、`risk_level`、`review_status` 應先採固定 enum 驗證
- `source_label` 與 `risk_note` 應做最小 normalization，但不要在 T017 擴成完整 moderation workflow

### 8.4 For T022 Reputation

- 第一版 reputation 應採 derived summary，而不是手動寫入型評分紀錄
- tester-side reputation anchor 應先使用 `device_profile_id`
- campaign-side collaboration summary anchor 應先使用 `campaign_id`
- 若分母為 `0`，所有 rate 欄位應回 `0`，避免在 MVP 階段引入額外 null-state 複雜度

## 9. Safety Layer Schema Draft

### 9.1 Safety Boundary

`Safety` 在 MVP 階段應先掛在 `Campaign` 層，而不是 `Project` 或 `Task` 層。

判斷理由：

- 安全來源與分發方式通常跟某一輪測試活動直接相關
- 同一個 `Project` 可以有不同分發方式與不同風險等級的 `Campaign`
- 若把來源與風險資訊切到 `Task`，資料粒度會過細，增加維護成本

因此，MVP 階段採：

- 一個 `Campaign` 對應 `0..1` 筆 `Campaign Safety Profile`

### 9.2 Campaign Safety Fields

| Field | Type | Category | Used In | MVP | Purpose / Notes |
| --- | --- | --- | --- | --- | --- |
| `id` | `string` | 系統產生 | detail | Yes | Safety profile 的對外識別碼 |
| `campaign_id` | `string` | 必填 | detail, create | Yes | 所屬 Campaign 識別碼；建立後不可變 |
| `distribution_channel` | `"web_url" \| "pwa_url" \| "testflight" \| "google_play_testing" \| "manual_invite" \| "other"` | 必填 | detail, create, update | Yes | 本輪測試的主要分發方式 |
| `source_label` | `string` | 必填 | detail, create, update | Yes | 顯示給使用者的來源名稱 |
| `source_url` | `string \| null` | 選填 | detail, create, update | Yes | 來源網址或入口連結；不是所有平台都必填 |
| `risk_level` | `"low" \| "medium" \| "high"` | 必填 | detail, create, update | Yes | 最小風險標示，不代表完整安全保證 |
| `review_status` | `"pending" \| "approved" \| "rejected"` | 系統預設 / 可更新 | detail, create, update | Yes | 最小人工審核狀態；create 預設為 `pending` |
| `official_channel_only` | `boolean` | 系統預設 / 可更新 | detail, create, update | Yes | 是否限定官方或官方授權分發方式；create 預設為 `false` |
| `risk_note` | `string \| null` | 選填 | detail, create, update | Yes | 額外風險提示或人工註記 |
| `created_at` | `string (ISO 8601)` | 系統產生 | detail | Yes | 建立時間 |
| `updated_at` | `string (ISO 8601)` | 系統產生 | detail | Yes | 最後更新時間 |

### 9.3 Campaign Safety Create / Update Baseline

create body 最小欄位：

- `distribution_channel`
- `source_label`
- `source_url`
- `risk_level`
- `review_status`
- `official_channel_only`
- `risk_note`

update body 最小欄位：

- `distribution_channel`
- `source_label`
- `source_url`
- `risk_level`
- `review_status`
- `official_channel_only`
- `risk_note`

規則：

- 採 `PATCH`
- `campaign_id` 不在 update body 中提供
- `review_status` create 時可不傳，由 backend 預設為 `pending`
- `official_channel_only` create 時可不傳，由 backend 預設為 `false`

### 9.4 Campaign Safety API Baseline

後續 T017 建議對齊以下路徑：

- `GET /api/v1/campaigns/{campaign_id}/safety`
- `POST /api/v1/campaigns/{campaign_id}/safety`
- `PATCH /api/v1/campaigns/{campaign_id}/safety`
- `DELETE /api/v1/campaigns/{campaign_id}/safety`

規則：

- `Safety` 應視為 campaign 的 nested singleton resource
- 成功 response 預設直接回傳 resource
- `DELETE` 成功時回 `204 No Content`

### 9.5 Campaign Safety Deferred Fields

以下欄位目前先不納入 MVP：

- `attachment_scan_status`
- `reviewed_by`
- `reviewed_at`
- `safety_checklist`
- `incident_history`
- `platform_policy_reference`

判斷理由：

- 這些欄位都會把第一版 `Safety` 從「可辨識、可提示」推向「完整審核系統」
- MVP 階段的重點是先讓來源、風險、審核狀態可被看見，而不是一次完成整套 moderation infrastructure

## 10. Reputation Schema Draft

### 10.1 Reputation Boundary

在沒有完整帳號系統與 ownership model 的前提下，MVP 階段不適合直接做完整「雙向個人信譽」。

因此，第一版 reputation baseline 應採務實 anchor：

- tester-side reputation：先掛在 `device_profile_id`
- developer-side collaboration summary：先掛在 `campaign_id`

這是暫時的 MVP anchor，不代表未來正式帳號模型的最終設計。

### 10.2 Tester Reputation Summary Fields

| Field | Type | Category | Used In | MVP | Purpose / Notes |
| --- | --- | --- | --- | --- | --- |
| `device_profile_id` | `string` | 系統推導 | detail | Yes | Reputation summary 的 tester-side anchor |
| `tasks_assigned_count` | `number` | 系統推導 | detail | Yes | 已指派到該 device profile 的 task 數 |
| `tasks_submitted_count` | `number` | 系統推導 | detail | Yes | 已提交或完成的 task 數 |
| `feedback_submitted_count` | `number` | 系統推導 | detail | Yes | 該 device profile 已提交的 feedback 數 |
| `submission_rate` | `number` | 系統推導 | detail | Yes | `tasks_submitted_count / tasks_assigned_count`，0..1 |
| `last_feedback_at` | `string \| null` | 系統推導 | detail | Yes | 最近一次提交 feedback 的時間 |
| `updated_at` | `string (ISO 8601)` | 系統推導 | detail | Yes | summary 計算時間或最後更新時間 |

### 10.3 Campaign Collaboration Summary Fields

| Field | Type | Category | Used In | MVP | Purpose / Notes |
| --- | --- | --- | --- | --- | --- |
| `campaign_id` | `string` | 系統推導 | detail | Yes | Collaboration summary 的 campaign-side anchor |
| `tasks_total_count` | `number` | 系統推導 | detail | Yes | 屬於該 campaign 的 task 總數 |
| `tasks_closed_count` | `number` | 系統推導 | detail | Yes | 狀態為 `closed` 的 task 數 |
| `feedback_received_count` | `number` | 系統推導 | detail | Yes | 屬於該 campaign 的 feedback 數 |
| `closure_rate` | `number` | 系統推導 | detail | Yes | `tasks_closed_count / tasks_total_count`，0..1 |
| `last_feedback_at` | `string \| null` | 系統推導 | detail | Yes | 最近一次收到 feedback 的時間 |
| `updated_at` | `string (ISO 8601)` | 系統推導 | detail | Yes | summary 計算時間或最後更新時間 |

### 10.4 Reputation Derivation Rules

Tester-side reputation：

- `tasks_assigned_count`：`device_profile_id` 相符且狀態進入 `assigned` 之後的 task 數
- `tasks_submitted_count`：狀態為 `submitted` 或 `closed`，且已完成提交流程的 task 數
- `feedback_submitted_count`：由該 `device_profile_id` 推導出的 feedback 數
- `submission_rate = tasks_submitted_count / tasks_assigned_count`

Campaign-side collaboration summary：

- `tasks_total_count`：屬於該 `campaign_id` 的 task 數
- `tasks_closed_count`：屬於該 `campaign_id` 且狀態為 `closed` 的 task 數
- `feedback_received_count`：屬於該 `campaign_id` 的 feedback 數
- `closure_rate = tasks_closed_count / tasks_total_count`

共同規則：

- 若分母為 `0`，rate 一律回 `0`
- 第一版 reputation 採 read-only derived summary，不接受前端手動寫入

### 10.5 Reputation API Baseline

後續 T022 建議對齊以下路徑：

- `GET /api/v1/device-profiles/{device_profile_id}/reputation`
- `GET /api/v1/campaigns/{campaign_id}/reputation`

規則：

- 第一版只做 read-only summary
- 不提供 `POST` / `PATCH` / `DELETE`
- 若 anchor resource 不存在，回 `resource_not_found`

### 10.6 Reputation Deferred Fields

以下欄位目前先不納入 MVP：

- `score`
- `tier`
- `badge`
- `public_reviews`
- `dispute_count`
- `quality_label_history`
- `developer_response_rate`

判斷理由：

- 這些欄位都需要更成熟的帳號系統、審核流程或統計口徑
- 第一版 `Reputation` 的目的，是提供最小可用 summary，而不是建立公開排名或複雜評分系統
