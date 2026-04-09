# T057 - Participation-Aware Demo Seed and Docs Refresh

## 1. 背景

當 `T051` 到 `T056` 完成後，seed / README / manual QA / roadmap 都需要更新，否則：

- qualification fidelity 相關驗收資料不足
- participation request flow 難以手測
- repo 文件會再次落後實際能力

## 2. 目標

更新本地 demo seed 與文件，讓 participation phase 能被快速驗收與理解。

## 3. 範圍

本票只做收斂工作：

- 更新 seed script
- 更新 `LOCAL_DEMO_SEED.md`
- 更新 `MANUAL_QA.md`
- 更新 `README.md`
- 更新 `NEXT_PHASE_PLAN.md`

## 4. 資料模型建議

本票不新增新資料模型。

seed 需對齊既有：

- accounts
- projects
- campaigns
- eligibility
- device_profiles
- tasks
- qualification baseline
- participation requests

## 5. API 路徑建議

seed 仍應只調用既有 product API，不新增 dev-only endpoint。

需覆蓋的重點 API：

- participation request create / review / detail
- qualification routes
- assignment preview routes

## 6. 前端頁面 / 路由建議

本票不新增新頁面，但文件應涵蓋：

- `/my/eligible-campaigns`
- `/my/participation-requests`
- `/review/participation-requests`
- `/review/participation-requests/:requestId`
- qualification / assignment 相關既有頁面

## 7. Acceptance Criteria

- 一個 seed command 可建立 qualification fidelity 與 participation flow 驗收資料
- `MANUAL_QA.md` 可直接對應 `T051` 到 `T056`
- `README.md` 與 `NEXT_PHASE_PLAN.md` 可反映 participation phase 的真實進度

## 8. Out of Scope

- 不做多租戶 seed pack
- 不做 DB fixtures framework
- 不做 marketing 文案重寫

## 9. Backend Work Items

- 原則上不新增 product endpoint
- 視需要補 seed 所需的最小 HTTP sequence 調整

## 10. Frontend Work Items

- 無直接 runtime UI 變更
- 視需要更新手動 QA 路徑與說明

## 11. Test Items

### 11.1 Seed / Script Tests

- seed smoke test
- participation-aware fixtures 可成功建立

### 11.2 Docs Checks

- `MANUAL_QA.md` 驗收步驟可對應現有 routes
- `README.md`、`NEXT_PHASE_PLAN.md`、`LOCAL_DEMO_SEED.md` 內容一致

## 12. Risk / Notes

- backend 仍是 in-memory，文件中必須清楚標示 restart 後資料會消失
- fixtures 只需要覆蓋 participation phase，不要膨脹成完整 demo generator

## 13. 依賴關係（Dependencies）

主要依賴：

- `T051-device-profile-install-channel-baseline-and-form-support`
- `T052-qualification-evaluator-install-channel-fidelity`
- `T053-participation-intent-semantics-draft`
- `T054-tester-campaign-participation-request-flow`
- `T055-developer-participation-review-queue-and-decision-actions`
- `T056-participation-request-detail-and-candidate-snapshot-panels`
