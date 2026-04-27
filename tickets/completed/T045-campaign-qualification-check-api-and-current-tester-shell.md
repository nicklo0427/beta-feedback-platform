# T045 - Campaign Qualification Check API and Current Tester Shell

## 1. 背景

目前 tester 雖然可以看到 `Campaign` 與自己的 `Device Profile`，但系統還不能清楚表示：

- 自己是否符合某個 campaign 的資格
- 是哪一個 device profile 符合
- 若不符合，主要原因是什麼

這代表 `FR-011` 與 `FR-012` 還沒有真正落地。

## 2. 目標

建立 campaign qualification 的最小 read-only evaluator 與 current tester shell，讓 tester 能在 campaign detail 清楚看到：

- 自己有哪些 owned device profiles
- 哪些符合資格
- 哪些不符合
- 最小原因摘要

## 3. 範圍

本票只做 MVP 最小集合：

- backend 新增 campaign qualification read-only evaluation
- 只支援 current actor 的 owned device profiles
- frontend 在 campaign detail 加入 qualification section
- loading / empty / error / role mismatch / happy path 補齊

## 4. 資料模型建議

本票優先重用既有：

- `EligibilityRule`
- `DeviceProfile.owner_account_id`
- current actor baseline

qualification result 建議最小欄位：

- `device_profile_id`
- `qualification_status`
- `matched_rule_id`
- `reason_codes`
- `reason_summary`

## 5. API 路徑建議

建議新增：

- `GET /api/v1/campaigns/{campaign_id}/qualification-results?mine=true`

行為建議：

- `mine=true` 時用 `X-Actor-Id` 找出 current tester 的 owned device profiles
- 若 actor 缺失，回 `400 missing_actor_context`
- 若 actor 不是 `tester`，回 `409 forbidden_actor_role`

## 6. 前端頁面 / 路由建議

涉及頁面：

- `frontend/pages/campaigns/[campaignId].vue`

可補區塊：

- current tester qualification section
- qualification result list
- zero-state / no owned device profiles state

## 7. Acceptance Criteria

- tester 在 campaign detail 可看到 owned device profiles 的 qualification results
- qualification pass / fail 與原因摘要可見
- 沒有 active rules 時，qualification 可正確顯示為符合
- missing actor / role mismatch / no owned device profiles 都有清楚狀態
- backend / frontend / E2E 測試補齊

## 8. Out of Scope

- 不做 campaign application flow
- 不做 tester recommendation
- 不做 developer candidate search
- 不做批次 export

## 9. Backend Work Items

- 新增 campaign qualification read-only evaluator
- 以 current actor 的 owned device profiles 做 `mine=true` 查詢
- 補 pytest

## 10. Frontend Work Items

- campaign detail 補 qualification section
- 顯示 qualification result list 與原因摘要
- 保持 API 呼叫集中在 `features/eligibility/` 或相鄰 feature 層

## 11. Test Items

### 11.1 Backend Tests

- no rules happy path
- active rule match happy path
- fail reasons
- missing actor
- role mismatch
- no owned device profiles

### 11.2 Frontend Tests

- typecheck
- build

### 11.3 E2E Tests

- tester campaign qualification happy path
- no owned device profiles
- role mismatch
- regression：campaign detail 既有 safety / eligibility / tasks / reputation 區塊

## 12. Risk / Notes

- 這張票不要擴成 global candidate view
- 只做 current tester 的 qualification visibility

## 13. 依賴關係（Dependencies）

主要依賴：

- `T044-qualification-and-assignment-semantics-draft`

後續支撐：

- `T046-task-assignment-eligibility-preview-and-guardrails`
- `T047-tester-eligible-campaigns-workspace`
- `T048-qualification-context-panels-for-task-detail-and-inbox`
