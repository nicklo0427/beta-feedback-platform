# T028 - Local Demo Data Seeding Workflow

## 1. 背景

目前 backend 仍採 in-memory repository，process restart 後資料會消失。

這個策略在 MVP 階段很合理，但也帶來一個明顯問題：每次手動驗收、錄影 demo 或跨頁面驗證時，都得從零建立資料，成本高且容易因資料不足而中斷測試流程。

在 `T024` 到 `T027` 補齊 form 後，系統雖然會更可操作，但手動建立完整圖譜仍然很花時間。因此需要一條可重複執行、對齊現有 API contract 的本地 seed workflow。

## 2. 目標

提供可重複執行的本地 demo data 建立流程，讓開發者 / QA 能快速生成一組：

- `Project`
- `Campaign`
- `Safety`
- `Device Profile`
- `Task`
- `Feedback`

測試資料。

本票完成後，應具備以下結果：

- 一個命令可建立 demo graph
- seed 結果可直接拿來做手動驗收
- seed 輸出可列出建立後的 IDs / URLs

## 3. 範圍

本票只做本地 demo data workflow，範圍如下：

- 建立本地 seed script 或命令流程
- 透過既有 HTTP API 建資料
- 補一份 seed 使用說明
- 補最小 smoke verification

本票不應直接碰 repository internals，也不應引入 dev-only product endpoint。

## 4. 資料模型建議

本票不新增新資料模型。

### 4.1 Seed Data Requirements

seed data 至少應覆蓋：

- 1 筆 project
- 1 筆 campaign
- 1 筆 campaign safety
- 1 筆 device profile
- 1 筆 task
- 1 筆 feedback

### 4.2 Data Shape Rules

- 所有 seed payload 必須對齊現有 API contract
- 顯示文案使用 `Mobile Web`
- internal / API values 仍使用既有 enum values，例如 `h5`

## 5. API 路徑建議

本票只調用既有 API，例如：

- `POST /api/v1/projects`
- `POST /api/v1/campaigns`
- `POST /api/v1/campaigns/{campaign_id}/safety`
- `POST /api/v1/device-profiles`
- `POST /api/v1/campaigns/{campaign_id}/tasks`
- `POST /api/v1/tasks/{task_id}/feedback`

本票不新增任何 dev-only backend endpoint。

## 6. 前端頁面 / 路由建議

本票不新增頁面。

但 seed workflow 的輸出應方便對照現有 route，例如：

- `/projects/{project_id}`
- `/campaigns/{campaign_id}`
- `/device-profiles/{device_profile_id}`
- `/tasks/{task_id}`
- `/tasks/{task_id}/feedback/{feedback_id}`

## 7. Acceptance Criteria

- 一個命令可建立 demo graph
- seed 結果至少包含 1 project、1 campaign、1 safety、1 device profile、1 task、1 feedback
- seed script 可重複執行
- script 輸出至少包含建立後的 IDs 與可打開的 route / URL
- 不需要 reset endpoint；重啟 backend 即可清空 in-memory 狀態
- 文件已清楚標示 restart 後資料會消失

## 8. Out of Scope

- 不做正式 fixtures system
- 不做資料庫 migration
- 不做 admin seed panel
- 不做 multi-tenant demo packs
- 不做 production seeding strategy

## 9. Backend Work Items

本票原則上不新增 product endpoint。

若需要最小 backend 配合：

- 只允許 script 調用現有 API 的必要順序調整或錯誤處理穩定化
- 不得為 seed 專門新增 reset / seed endpoint

## 10. Frontend Work Items

本票無直接 runtime UI 變更。

若需要補文件：

- 可在 script 輸出中直接列出建好的前端 detail URLs

## 11. Test Items

### 11.1 Script / Workflow Tests

- seed command smoke test
- 確認所有 HTTP request 都使用現有 API
- 確認 seed 後主要 detail routes 可打開

### 11.2 Manual Verification Notes

- backend restart 後重新執行 seed
- 使用 script 輸出的 URLs 手動驗收主要頁面

## 12. Risk / Notes

- 因為是 in-memory，seed workflow 必須清楚寫出「backend restart 後資料會消失」
- script 輸出應偏向人類可讀，不要只輸出原始 JSON
- 若 script 要放 repo 中，應優先選擇簡單、可直接跑的形式，不要引入過度複雜的 CLI 框架

## 13. 依賴關係（Dependencies）

建議依賴：

- `T024-project-create-and-edit-forms`
- `T025-campaign-create-and-edit-forms`
- `T026-campaign-safety-create-and-edit-forms`
- `T027-feedback-review-status-and-supplement-request`

但本票也可獨立提前做，只是覆蓋面會較小。
