# T042 - Role-Aware Demo Seed and Owned Fixtures

## 1. 背景

目前 repo 已有：

- `scripts/seed_demo_data.py`
- `LOCAL_DEMO_SEED.md`

但這份 seed 目前只建立主流程資料，還不能完整支撐 role-aware 驗收，因為它不會自動建立：

- accounts
- owned projects
- owned device profiles
- 具備 developer / tester actor context 的整組資料

## 2. 目標

建立一份可重複執行的 role-aware demo seed workflow，讓開發者與 QA 可以快速得到一組可驗收：

- current actor
- ownership
- tester inbox
- developer review queue

的本地 fixture graph。

## 3. 範圍

本票只做 MVP 最小集合：

- seed 一組 developer account
- seed 一組 tester account
- seed 一組 owned project / campaign / safety / eligibility / task / feedback
- seed 一組 owned device profile
- 在輸出中明確列出：
  - actor ids
  - owned resource ids
  - 前端可直接打開的 URLs

## 4. 資料模型建議

本票不新增新資料模型。

所有 seed payload 必須對齊現有 API contract 與 current actor baseline。

## 5. API 路徑建議

seed 應只調用現有 API，例如：

- `/api/v1/accounts`
- `/api/v1/projects`
- `/api/v1/campaigns`
- `/api/v1/campaigns/{campaign_id}/safety`
- `/api/v1/campaigns/{campaign_id}/eligibility-rules`
- `/api/v1/device-profiles`
- `/api/v1/campaigns/{campaign_id}/tasks`
- `/api/v1/tasks/{task_id}/feedback`

不新增 dev-only endpoint。

## 6. 前端頁面 / 路由建議

本票不新增 runtime UI，但 seed 輸出至少要能直接對應：

- `/accounts/:accountId`
- `/projects/:projectId`
- `/campaigns/:campaignId`
- `/device-profiles/:deviceProfileId`
- `/tasks/:taskId`
- `/tasks/:taskId/feedback/:feedbackId`
- `/my/tasks`
- `/review/feedback`

## 7. Acceptance Criteria

- 一個命令可建立 role-aware fixture graph
- 結果至少包含：
  - 1 developer
  - 1 tester
  - 1 owned project
  - 1 owned campaign
  - 1 owned device profile
  - 1 task
  - 1 feedback
- script 輸出 actor ids 與 URLs
- 文件可直接指引手動 QA

## 8. Out of Scope

- 不做正式 fixture framework
- 不做 reset endpoint
- 不做 multi-pack demo generator
- 不做 admin seed UI

## 9. Backend Work Items

- 不新增 product endpoint
- 如有必要，只允許最小 contract 配合

## 10. Frontend Work Items

- 無直接 runtime UI 變更
- 視需要更新文件中的 URL 驗收順序

## 11. Test Items

### 11.1 Script / Smoke Tests

- seed command happy path
- health check
- seeded routes 可打開

### 11.2 文件驗證

- seed 文件與 `MANUAL_QA.md` 一致

## 12. Risk / Notes

- backend 仍是 in-memory，重啟後資料會消失
- script 必須明確寫出這項限制
- 不要讓 seed script 直接碰 repository internals

## 13. 依賴關係（Dependencies）

主要依賴：

- `T039-actor-aware-campaign-safety-and-eligibility-mutation-guards`
- `T040-actor-aware-task-and-feedback-action-guards`

後續支撐：

- `T043-account-collaboration-summary-and-owned-resource-panels`
