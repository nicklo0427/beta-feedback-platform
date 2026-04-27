# T063 - Participation Assignment Seed and Docs Refresh

## 1. 背景

當 `T058` 到 `T062` 完成後，seed / README / manual QA / roadmap 需要再次更新，否則：

- accepted request -> task assignment 驗收資料不足
- request-to-task traceability 難以手測
- 文件會再次落後實際能力

## 2. 目標

更新本地 demo seed 與文件，讓 participation-to-assignment phase 能被快速驗收與理解。

## 3. 範圍

- 更新 seed script
- 更新 `LOCAL_DEMO_SEED.md`
- 更新 `MANUAL_QA.md`
- 更新 `README.md`
- 更新 `NEXT_PHASE_PLAN.md`

## 4. 資料模型建議

本票不新增新資料模型。

## 5. API 路徑建議

seed 仍應只調用既有 product API，不新增 dev-only endpoint。

需覆蓋的重點：

- participation accepted -> task bridge
- request / task traceability
- candidate overview summary

## 6. 前端頁面 / 路由建議

文件應涵蓋：

- `/my/participation-requests`
- `/review/participation-requests`
- `/review/participation-requests/:requestId`
- 與 request bridge 後對應的 task detail / workspace

## 7. Acceptance Criteria

- 一個 seed command 可建立 participation-to-assignment 驗收資料
- `MANUAL_QA.md` 可直接對應 `T058` 到 `T062`
- `README.md` 與 `NEXT_PHASE_PLAN.md` 可反映下一個 phase 的真實進度

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

- seed smoke test
- 文件一致性檢查

## 12. Risk / Notes

- backend 仍是 in-memory，文件中必須清楚標示 restart 後資料會消失

## 13. 依賴關係（Dependencies）

主要依賴：

- `T058`
- `T059`
- `T060`
- `T061`
- `T062`
