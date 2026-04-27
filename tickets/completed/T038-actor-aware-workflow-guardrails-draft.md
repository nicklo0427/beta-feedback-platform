# T038 - Actor-Aware Workflow Guardrails Draft

## 1. 背景

目前 repo 已完成：

- `T030` 到 `T037`
- `Account / Ownership / Current Actor` baseline
- tester inbox
- developer review queue
- role-aware homepage

但 current actor 與 ownership 目前還沒有完整貫穿到所有 mutation。

這代表系統雖然已能表達：

- 誰是 developer
- 誰是 tester
- 哪些資源可能屬於誰

卻還沒有一份正式文件明確定義：

- 哪些 route 必須帶 actor
- 哪些 action 必須驗證 actor role
- 哪些 action 必須驗證 ownership
- 應該回什麼錯誤代碼與錯誤結構

## 2. 目標

建立 `Actor-Aware Workflow Guardrails` 的文件基線，作為後續：

- `T039`
- `T040`
- `T041`
- `T042`
- `T043`

的直接實作依據。

## 3. 範圍

本票只做文件層面的最小定義，範圍如下：

- 定義 actor-aware mutation matrix
- 定義 actor role 檢查 baseline
- 定義 ownership 檢查 baseline
- 定義錯誤代碼與 message baseline
- 列出哪些 routes 先納入 guardrails，哪些延後

## 4. 資料模型建議

本票不新增新 domain，但需在文件中明確定義以下概念：

- `current_actor_id`
- `current_actor_role`
- `owner_account_id`
- derived ownership

### 4.1 Actor Role Baseline

MVP 仍只允許：

- `developer`
- `tester`

### 4.2 Ownership Baseline

直接 ownership：

- `Project.owner_account_id`
- `DeviceProfile.owner_account_id`

推導 ownership：

- `Campaign` 由 `Project.owner_account_id` 推導
- `Safety` 由 `Campaign -> Project.owner_account_id` 推導
- `EligibilityRule` 由 `Campaign -> Project.owner_account_id` 推導
- `Task` 由 `Campaign -> Project.owner_account_id` 推導 developer side，並由 `device_profile_id -> owner_account_id` 推導 tester side
- `Feedback` 由 `Task` 推導 developer side 與 tester side ownership anchor

## 5. API 路徑建議

本票不新增 runtime API，但文件中必須明確標示以下 route 的 guardrails 覆蓋範圍：

- `POST /api/v1/campaigns`
- `PATCH /api/v1/campaigns/{campaign_id}`
- `POST /api/v1/campaigns/{campaign_id}/safety`
- `PATCH /api/v1/campaigns/{campaign_id}/safety`
- `POST /api/v1/campaigns/{campaign_id}/eligibility-rules`
- `PATCH /api/v1/eligibility-rules/{eligibility_rule_id}`
- `POST /api/v1/campaigns/{campaign_id}/tasks`
- `PATCH /api/v1/tasks/{task_id}`
- `POST /api/v1/tasks/{task_id}/feedback`
- `PATCH /api/v1/feedback/{feedback_id}`

### 5.1 錯誤代碼建議

文件中至少要定義：

- `missing_actor_context`
- `forbidden_actor_role`
- `ownership_mismatch`

並維持既有錯誤結構：

- `code`
- `message`
- `details`

## 6. 前端頁面 / 路由建議

本票不新增頁面，但需在文件中標明：

- 哪些 create / edit 頁面必須帶 current actor header
- 哪些頁面需要顯示 role mismatch / ownership mismatch
- 哪些頁面只做 read-only，不必強制 actor

## 7. Acceptance Criteria

- `DATA_MODEL_DRAFT.md` 或等價文件已明確寫出 actor-aware workflow guardrails baseline
- 已列出優先納入 guardrails 的 routes
- 已明確寫出 role / ownership 的檢查原則
- 已明確寫出錯誤代碼 baseline
- 後續 `T039` 與 `T040` 可直接引用，不需重定義

## 8. Out of Scope

- 不做正式 auth
- 不做 session / token
- 不做 OAuth
- 不做 RBAC framework
- 不做 organization / team model

## 9. Backend Work Items

- 無 runtime code
- 補強文件中的 actor-aware mutation matrix

## 10. Frontend Work Items

- 無 runtime code
- 視需要補充 current actor header baseline 的文件說明

## 11. Test Items

- 無 runtime tests
- 文件需與既有 `T030`、`T032` 的 ownership / actor baseline 一致
- 文件術語需與 `README.md`、`DATA_MODEL_DRAFT.md` 一致

## 12. Risk / Notes

- 這張票最重要的是「不要把權限設計做成正式 auth」
- 只需要為 MVP 定義最小但一致的 actor / role / ownership guardrails

## 13. 依賴關係（Dependencies）

主要依賴：

- `T030-account-and-ownership-mvp-schema-draft`
- `T032-current-actor-context-and-ownership-baseline`

後續支撐：

- `T039-actor-aware-campaign-safety-and-eligibility-mutation-guards`
- `T040-actor-aware-task-and-feedback-action-guards`
