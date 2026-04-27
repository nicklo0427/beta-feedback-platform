# T029 - README and Manual QA Docs Refresh

## 1. 背景

現在 repo 已不再是初始化階段，但 `README.md` 仍保留較早期的描述，例如：

- 專案仍處於初始化階段
- 前後端框架尚未建立

這已與目前 repo 狀態不一致。現在專案已具備：

- 完整 MVP 主流程
- 第一輪產品化補強
- 多個 create / edit form
- Playwright 與 pytest 基線

此外，repo 目前也缺少一份與現況對齊的手動 QA 文件，導致新加入開發者或驗收者需要自己摸索測試順序。

## 2. 目標

更新 `README.md` 與手動 QA 文件，讓 repo 對目前 MVP 狀態有正確描述，並降低新加入開發者與驗收者的理解成本。

本票完成後，應具備以下結果：

- README 可正確描述目前已完成能力
- README 的啟動方式與本機驗證流程正確
- 有一份可直接照著跑的手動 QA 文件

## 3. 範圍

本票只做文件同步，範圍如下：

- 更新 `README.md` 的 current state / run instructions / module summary
- 新增手動 QA 文件，例如：
  - `MANUAL_QA.md`
- 文件中納入目前已完成 routes、主要 flow、已知限制
- 文件中明確說明：
  - in-memory 限制
  - `Mobile Web` 用語

## 4. 資料模型建議

本票不新增資料模型。

### 4.1 Documentation Baseline

文件應反映：

- 目前已有的 backend modules
- 目前已有的 frontend routes
- 目前已有的測試基線
- 目前已知技術限制

## 5. API 路徑建議

本票不新增 API。

文件中若需要列出 API，只應列出已存在且可用的路徑，不預寫未實作能力。

## 6. 前端頁面 / 路由建議

本票不新增頁面。

但手動 QA 文件應列出主要驗收頁面與順序，例如：

- `/projects`
- `/campaigns`
- `/device-profiles`
- `/tasks`
- nested detail routes

## 7. Acceptance Criteria

- README 不再描述 repo 為「尚未建立框架」
- README 能反映已完成模組與 run 方式
- README 中的啟動指令與本機現況一致
- 新增一份手動 QA 文件
- 手動 QA 文件可覆蓋從 `Project` 到 `Feedback` 的主要 flow
- 文件中明確標示：
  - backend 仍為 in-memory
  - restart 後資料會消失
  - 第一階段平台文案使用 `Mobile Web`

## 8. Out of Scope

- 不做產品 PR / marketing 文案重寫
- 不做完整 contributor guide
- 不做 CI/CD 教學文件
- 不調整 runtime 功能

## 9. Backend Work Items

本票無 backend runtime 變更。

若文件中提到 backend，內容必須以實際已存在的 module / API 為準。

## 10. Frontend Work Items

本票無 frontend runtime 變更。

若文件需要路由與頁面驗收順序，應以現有 routes 與實際可操作 flow 為準。

## 11. Test Items

### 11.1 Documentation Verification

- README 中列出的啟動指令實際可跑
- README 中列出的主要頁面 / API 與 repo 現況一致
- 手動 QA 文件中的驗收步驟可實際執行

### 11.2 Consistency Focus

- `README.md`
- `MANUAL_QA.md`
- 既有 `PRD.md`
- 既有 `ARCHITECTURE.md`

之間的關鍵描述不能互相衝突。

## 12. Risk / Notes

- 這張票是文件同步，不應順手改產品功能
- 若 `T024`～`T028` 尚未完成，文件應以實際完成狀態為準，不預寫未完成能力
- 手動 QA 文件應聚焦高價值驗收，不要變成過長的逐像素檢查清單

## 13. 依賴關係（Dependencies）

建議依賴：

- `T024-project-create-and-edit-forms`
- `T025-campaign-create-and-edit-forms`
- `T026-campaign-safety-create-and-edit-forms`
- `T027-feedback-review-status-and-supplement-request`
- `T028-local-demo-data-seeding-workflow`

本票建議最後做，因為它需要反映前述票完成後的真實 repo 狀態。
