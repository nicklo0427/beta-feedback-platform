# T037 - Role-Aware Docs and Manual QA Refresh

## 1. 背景

一旦 `T030` 到 `T036` 完成，repo 的重心會從：

- 單純的資料流程與 form

進一步走到：

- account
- ownership
- role-aware collaboration

這時 README、manual QA、demo seed 文案都需要同步，否則文件會再次落後於 runtime 現況。

## 2. 目標

更新 repo 文件，使其正確反映：

- account / role baseline
- current actor 使用方式
- developer / tester 的主要工作入口
- role-aware manual QA 流程

## 3. 範圍

本票只做文件同步：

- 更新 `README.md`
- 更新 `MANUAL_QA.md`
- 視需要更新 `LOCAL_DEMO_SEED.md`
- 視需要更新 `NEXT_PHASE_PLAN.md`

## 4. 資料模型建議

無新增資料模型。

但文件需能正確描述：

- `Account`
- `owner_account_id`
- current actor
- role-aware queue / inbox

## 5. API 路徑建議

無新增 API。

但文件需列出目前最主要的 role-aware routes 與操作順序。

## 6. 前端頁面 / 路由建議

文件中應至少涵蓋：

- `/accounts`
- `/projects`
- `/campaigns`
- `/device-profiles`
- `/my/tasks`
- `/review/feedback`

以及 detail / form 相關路由。

## 7. Acceptance Criteria

- README 已反映 role-aware phase 的真實狀態
- MANUAL_QA 已能覆蓋 developer / tester 兩條主要驗收路徑
- seed 文件若受影響，也已同步
- 文件中不預寫未完成功能

## 8. Out of Scope

- 不做產品官網文案改寫
- 不做 contributor guide 大重寫
- 不做 CI/CD 文件重整

## 9. Backend Work Items

- 無 runtime code

## 10. Frontend Work Items

- 無 runtime code
- 只更新文件對 routes / flows 的描述

## 11. Test Items

- README 中的本機啟動指令可實際執行
- 文件中的主要路由與 flow 與 repo 實際狀態一致
- MANUAL_QA 可直接作為瀏覽器驗收 checklist

## 12. Risk / Notes

- 這張票是文件票，不應順手改產品功能
- 文件應以實際完成狀態為準，不提前描述下一張票

## 13. 依賴關係（Dependencies）

主要依賴：

- `T036-role-aware-dashboard-and-navigation-refresh`

後續支撐：

- 後續 onboarding 與 QA 溝通
