# T044 - Qualification and Assignment Semantics Draft

## 1. 背景

目前 repo 已有：

- `Campaign Eligibility Rules`
- `Task Assignment`
- `Tester Device Profile`
- `Actor-Aware Task / Feedback Guards`

但系統還沒有一份正式文件明確定義：

- 多條 eligibility rules 應如何組合
- 沒有 active rules 時是否視為符合
- qualification result 應長什麼樣子
- assignment 不符合資格時應回什麼錯誤

這會讓後續如果直接做 qualification API 或 assignment guard，很容易出現 backend 與 frontend 各自長出不同語意。

## 2. 目標

建立 `Qualification and Assignment Semantics` 的文件基線，作為後續：

- `T045`
- `T046`
- `T047`
- `T048`

的直接實作依據。

## 3. 範圍

本票只做文件層面的最小定義，範圍如下：

- 定義 qualification result 的最小 shape
- 定義 eligibility rules 的組合語意
- 定義 assignment readiness baseline
- 定義 `assignment_not_eligible` error baseline
- 定義最小 reason codes / reason summary baseline

## 4. 資料模型建議

本票不新增新 domain，但需在文件中明確定義以下概念：

- `qualification_status`
- `matched_rule_id`
- `reason_codes`
- `reason_summary`
- `assignment_readiness`

### 4.1 Qualification Result Baseline

建議最小欄位：

- `device_profile_id`
- `qualification_status`
- `matched_rule_id`
- `reason_codes`
- `reason_summary`

### 4.2 Rule Combination Baseline

建議明確定義：

- 單一 rule 內各欄位為 `AND`
- 同一 campaign 的多條 active rules 為 `OR`
- inactive rules 應忽略
- 若沒有 active rules，視為 `qualified`

### 4.3 Failure Reasons Baseline

reason codes 不需要做成完整規則引擎，但至少應支持：

- `platform_mismatch`
- `os_name_mismatch`
- `os_version_below_min`
- `os_version_above_max`
- `install_channel_mismatch`
- `rule_inactive`

### 4.4 Assignment Guard Baseline

文件需明確定義：

- task assignment 使用 campaign qualification semantics
- 若 device profile 不符合資格，task create / edit assignment 應拒絕
- 錯誤代碼建議為：
  - `assignment_not_eligible`

## 5. API 路徑建議

本票不新增 runtime API，但文件中應為後續票明確標示可依附的路徑：

- `GET /api/v1/campaigns/{campaign_id}/qualification-results?mine=true`
- `GET /api/v1/campaigns/{campaign_id}/qualification-check?device_profile_id=...`
- `POST /api/v1/campaigns/{campaign_id}/tasks`
- `PATCH /api/v1/tasks/{task_id}`

## 6. 前端頁面 / 路由建議

本票不新增頁面，但需在文件中標明後續會涉及：

- `frontend/pages/campaigns/[campaignId].vue`
- `frontend/pages/campaigns/task-new-[campaignId].vue`
- `frontend/pages/tasks/edit-[taskId].vue`
- `frontend/pages/my/eligible-campaigns.vue`
- `frontend/pages/my/tasks.vue`

## 7. Acceptance Criteria

- `DATA_MODEL_DRAFT.md` 或等價文件已明確寫出 qualification semantics baseline
- 已明確寫出 rule combination 規則
- 已明確寫出 qualification result 的最小欄位
- 已明確寫出 assignment guard baseline 與錯誤代碼
- 後續 `T045` 到 `T048` 可直接引用，不需重定義

## 8. Out of Scope

- 不做 runtime evaluator
- 不做 matching engine
- 不做 recommendation ranking
- 不做申請制 workflow
- 不做複雜 rule DSL

## 9. Backend Work Items

- 無 runtime code
- 補強文件中的 qualification semantics 定義

## 10. Frontend Work Items

- 無 runtime code
- 視需要補充 current actor 與 qualification panel 的文件說明

## 11. Test Items

- 無 runtime tests
- 文件術語需與 `PRD.md`、`ARCHITECTURE.md`、`DATA_MODEL_DRAFT.md` 一致
- 文件中需明確與既有 `eligibility`、`task assignment`、`current actor` baseline 對齊

## 12. Risk / Notes

- 這張票最重要的是「不要把 qualification semantics 做成規則引擎設計」
- 只需要為 MVP 定義最小但一致的 evaluator 與 assignment baseline

## 13. 依賴關係（Dependencies）

主要依賴：

- `T013-campaign-eligibility-filter-rules`
- `T014-task-assignment-and-task-status-flow`

後續支撐：

- `T045-campaign-qualification-check-api-and-current-tester-shell`
- `T046-task-assignment-eligibility-preview-and-guardrails`
- `T047-tester-eligible-campaigns-workspace`
- `T048-qualification-context-panels-for-task-detail-and-inbox`
