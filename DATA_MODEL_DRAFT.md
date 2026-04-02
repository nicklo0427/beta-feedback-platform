# beta-feedback-platform Data Model Draft

## 1. Purpose

本文件定義 `beta-feedback-platform` 在 MVP 階段的 `Project` / `Campaign` 資料欄位草案，作為後續：

- `T007-projects-and-campaigns-backend-crud`
- `T008-projects-and-campaigns-frontend-shell`

的直接依據。

本文件只處理 MVP 最小資料模型，不處理：

- 資料庫 migration
- auth / ownership / RBAC
- 完整商業規則
- Task / Feedback / Reputation / Safety Layer 的詳細欄位

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
