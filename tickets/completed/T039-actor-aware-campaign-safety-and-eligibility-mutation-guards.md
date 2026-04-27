# T039 - Actor-Aware Campaign, Safety, and Eligibility Mutation Guards

## 1. 背景

目前 `Campaign / Safety / Eligibility Rule` 已有：

- backend CRUD
- frontend shell
- create / edit forms

但這些 mutation 目前還沒有完整驗證：

- current actor 是否存在
- current actor 是否是 developer
- current actor 是否擁有對應 project / campaign

這會讓 role-aware collaboration 的 baseline 還不夠可靠。

## 2. 目標

把 campaign、campaign safety、eligibility rule 的 mutation 全部補上 actor-aware guardrails，讓 developer side 的核心配置流程有一致的權限邊界。

## 3. 範圍

本票只做 MVP 最小集合：

- campaign create / edit 的 actor role 與 ownership 驗證
- safety create / edit 的 actor role 與 ownership 驗證
- eligibility rule create / edit 的 actor role 與 ownership 驗證
- frontend create / edit flow 一律帶 current actor header
- frontend 顯示最小 role mismatch / ownership mismatch 錯誤

## 4. 資料模型建議

本票不新增新資料模型。

需要重用：

- `Account.role`
- `Project.owner_account_id`
- current actor header baseline

## 5. API 路徑建議

需納入 guardrails 的 routes：

- `POST /api/v1/campaigns`
- `PATCH /api/v1/campaigns/{campaign_id}`
- `POST /api/v1/campaigns/{campaign_id}/safety`
- `PATCH /api/v1/campaigns/{campaign_id}/safety`
- `POST /api/v1/campaigns/{campaign_id}/eligibility-rules`
- `PATCH /api/v1/eligibility-rules/{eligibility_rule_id}`

錯誤 baseline 應維持：

- `missing_actor_context`
- `forbidden_actor_role`
- `ownership_mismatch`

## 6. 前端頁面 / 路由建議

涉及頁面：

- `frontend/pages/projects/campaign-new-[projectId].vue`
- `frontend/pages/campaigns/edit-[campaignId].vue`
- `frontend/pages/campaigns/safety-new-[campaignId].vue`
- `frontend/pages/campaigns/safety-edit-[campaignId].vue`
- `frontend/pages/campaigns/eligibility-rule-new-[campaignId].vue`
- `frontend/pages/campaigns/eligibility-rule-edit-[campaignId]-[eligibilityRuleId].vue`

## 7. Acceptance Criteria

- developer actor 才能建立 / 編輯 campaign
- developer actor 只能操作自己擁有 project / campaign 衍生出的 campaign / safety / eligibility
- 未帶 actor 時，frontend 會顯示明確錯誤
- role mismatch 與 ownership mismatch 會顯示明確錯誤
- 現有 campaign detail shell、safety shell、eligibility shell 不被破壞

## 8. Out of Scope

- 不做正式 auth
- 不做 organization / team collaboration
- 不做 reviewer role
- 不做 bulk actions

## 9. Backend Work Items

- 補 campaign create / update 的 actor-aware guard
- 補 safety create / update 的 actor-aware guard
- 補 eligibility create / update 的 actor-aware guard
- 補 pytest

## 10. Frontend Work Items

- 讓相關 form flow 一律帶 current actor header
- 顯示 actor-aware backend error
- 保持 API 呼叫集中在 feature / service 層

## 11. Test Items

### 11.1 Backend Tests

- missing actor
- actor role mismatch
- ownership mismatch
- happy path

### 11.2 Frontend Tests

- typecheck
- build

### 11.3 E2E Tests

- developer happy path
- tester 嘗試操作 developer-only mutation
- missing actor path
- regression：campaign shell / safety form / eligibility form

## 12. Risk / Notes

- 不要把這張票擴成完整 access control system
- 只補目前已存在流程的最小 guardrails

## 13. 依賴關係（Dependencies）

主要依賴：

- `T038-actor-aware-workflow-guardrails-draft`

後續支撐：

- `T041-developer-workspace-mine-views-and-owned-resource-navigation`
