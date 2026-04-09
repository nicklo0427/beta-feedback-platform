# T049 - Qualification-Aware Demo Seed and Manual QA Refresh

## 1. 背景

`T042` 已讓本地 seed workflow 能建立 role-aware fixtures，但 qualification phase 完成後，手動驗收還需要更精準的資料：

- qualification pass 的 device profile
- qualification fail 的 device profile
- 可成功 assignment 的案例
- 會被 assignment guard 擋下的案例

如果沒有這些 fixtures，後續手動 QA 會變得很難重現。

## 2. 目標

更新本地 demo seed 與手動 QA 文件，讓 qualification / assignment phase 能被快速驗收。

## 3. 範圍

本票只做 MVP 最小集合：

- 更新 seed script
- 補 qualification pass / fail fixtures
- 補可展示 ineligible assignment fail 的 fixture
- 更新 `MANUAL_QA.md`
- 視需要補 `LOCAL_DEMO_SEED.md`

## 4. 資料模型建議

本票不新增新資料模型。

seed 需對齊既有：

- `accounts`
- `projects`
- `campaigns`
- `eligibility`
- `device_profiles`
- `tasks`
- qualification semantics baseline

## 5. API 路徑建議

seed 仍應只調用既有 product API，不新增 dev-only endpoint。

需覆蓋的重點 API：

- campaign qualification read-only routes
- task assignment routes
- tester eligible campaigns routes

## 6. 前端頁面 / 路由建議

本票不新增新頁面，但手動 QA 文件應涵蓋：

- `/campaigns/:campaignId`
- `/campaigns/:campaignId/tasks/new`
- `/my/eligible-campaigns`
- `/my/tasks`
- `/tasks/:taskId`

## 7. Acceptance Criteria

- 一個 seed command 可生成 qualification pass / fail 驗收資料
- 至少有一組 fixture 可展示：
  - campaign qualification pass
  - campaign qualification fail
  - eligible assignment
  - ineligible assignment fail
- `MANUAL_QA.md` 能直接對應 `T045` 到 `T048`

## 8. Out of Scope

- 不做多租戶 seed pack
- 不做 DB fixtures framework
- 不做 admin seed panel

## 9. Backend Work Items

- 原則上不新增 product endpoint
- 視需要補 seed 所需的安全 HTTP sequence 調整

## 10. Frontend Work Items

- 無直接 runtime UI 變更
- 視需要更新手動 QA 路徑與說明

## 11. Test Items

### 11.1 Seed / Script Tests

- seed smoke test
- qualification-aware fixtures 可成功建立

### 11.2 Docs Checks

- `MANUAL_QA.md` 驗收步驟可對應現有 routes
- `LOCAL_DEMO_SEED.md` 與 seed script 行為一致

## 12. Risk / Notes

- 因為 backend 仍是 in-memory，文件中必須明確說明 restart 後資料會消失
- fixtures 只需要覆蓋 qualification / assignment phase，不要膨脹成完整 demo generator

## 13. 依賴關係（Dependencies）

主要依賴：

- `T045-campaign-qualification-check-api-and-current-tester-shell`
- `T046-task-assignment-eligibility-preview-and-guardrails`
- `T047-tester-eligible-campaigns-workspace`
- `T048-qualification-context-panels-for-task-detail-and-inbox`

後續支撐：

- `T050-readme-and-roadmap-refresh-for-qualification-phase`
