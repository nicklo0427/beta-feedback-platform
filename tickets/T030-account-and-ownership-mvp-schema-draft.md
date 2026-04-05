# T030 - Account and Ownership MVP Schema Draft

## 1. 背景

目前 repo 已完成 `Project / Campaign / Device Profile / Eligibility / Task / Feedback / Safety / Reputation` 的 MVP 流程，但系統仍缺少：

- 帳號資源（Account）
- 角色（Developer / Tester）的正式資料表示
- resource ownership baseline
- current actor 的最小運作規則

沒有這層基礎時，後續的：

- role-aware task inbox
- developer review queue
- ownership-based list filtering
- collaboration-oriented reputation

都缺少穩定 anchor。

本票的定位是文件先行票，用來定義下一階段實作邊界，而不是直接做 auth。

## 2. 目標

建立 `Account / Ownership` 的 MVP schema draft，作為後續：

- `T031-account-crud-and-role-shell`
- `T032-current-actor-context-and-ownership-baseline`
- `T033-tester-task-inbox-and-assigned-task-actions`
- `T034-developer-feedback-review-queue-and-filters`

的直接依據。

## 3. 範圍

本票只做文件層面的 MVP 定義，範圍如下：

- 定義 `Account` 最小欄位
- 定義 `role` 最小集合
- 定義 `owner_account_id` 的 baseline
- 定義 current actor 的本地開發策略
- 定義哪些資源直接持有 owner，哪些由關聯資源推導

## 4. 資料模型建議

### 4.1 Account 最小欄位

建議至少定義：

- `id`
- `display_name`
- `role`
- `bio`
- `locale`
- `created_at`
- `updated_at`

### 4.2 Role Baseline

MVP 只允許：

- `developer`
- `tester`

### 4.3 Ownership Baseline

建議區分：

- 直接 owner：
  - `Project.owner_account_id`
  - `DeviceProfile.owner_account_id`
- 推導 owner：
  - `Campaign` 由 `Project` 推導 developer owner
  - `Task` 由 `Campaign` 推導 developer owner，並由 `device_profile_id` 推導 tester side anchor
  - `Feedback` 由 `Task` 推導 `campaign_id / device_profile_id`

### 4.4 Current Actor Baseline

MVP 不做正式登入，先定義：

- frontend 可切換 current actor
- backend 透過最小 request context 讀取 current actor
- 作為 create ownership 與 role-aware filtering 的依據

## 5. API 路徑建議

本票主要是 schema draft，但建議先在文件中明確預留：

- `GET /api/v1/accounts`
- `POST /api/v1/accounts`
- `GET /api/v1/accounts/{account_id}`
- `PATCH /api/v1/accounts/{account_id}`

以及 current actor 相關策略，例如：

- request header
- local actor selector

本票不需要定死成 production auth contract。

## 6. 前端頁面 / 路由建議

建議先在文件中預留：

- `/accounts`
- `/accounts/:accountId`

以及 current actor 的 placement 原則，例如：

- homepage
- global header
- local dev-only selector

## 7. Acceptance Criteria

- `DATA_MODEL_DRAFT.md` 已補入 `Account / Ownership` 的 MVP schema draft
- 必須明確寫出：
  - `Account` 欄位
  - `role` baseline
  - `owner_account_id` baseline
  - current actor baseline
- 文件需標明：
  - 哪些屬於 MVP
  - 哪些先延後
- 後續 `T031`、`T032` 可直接引用，不需再重新定義基礎概念

## 8. Out of Scope

- 不做正式 auth
- 不做 password / email login
- 不做 OAuth / third-party login
- 不做 RBAC framework
- 不做 organization / team model

## 9. Backend Work Items

- 無 runtime code
- 視需要更新文件中的 backend model baseline

## 10. Frontend Work Items

- 無 runtime code
- 視需要更新文件中的 actor handling baseline

## 11. Test Items

- 無 runtime test
- 文件需能被後續 ticket 直接引用
- 文件術語需與 `PRD.md`、`ARCHITECTURE.md` 一致

## 12. Risk / Notes

- 這張票最重要的是「不要把 auth 設計過頭」
- 只需定出 MVP 階段最小 actor 與 ownership 邊界

## 13. 依賴關係（Dependencies）

主要依賴：

- 既有 `T016-safety-and-reputation-mvp-schema-draft`

後續支撐：

- `T031-account-crud-and-role-shell`
- `T032-current-actor-context-and-ownership-baseline`
