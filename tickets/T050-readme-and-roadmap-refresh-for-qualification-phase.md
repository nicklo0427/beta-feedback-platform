# T050 - README and Roadmap Refresh for Qualification Phase

## 1. 背景

qualification / assignment phase 完成後，repo 文件需要重新對齊實際狀態，否則：

- `README.md` 會落後真實能力
- `NEXT_PHASE_PLAN.md` 會繼續停在過時判斷
- 手動 QA 與 seed 說明也會出現落差

## 2. 目標

更新 README、roadmap 與相關文件，讓 repo 對 qualification phase 的完成狀態有正確描述。

## 3. 範圍

本票只做文件同步，範圍如下：

- 更新 `README.md`
- 更新 `NEXT_PHASE_PLAN.md` 或改寫成下一份 phase plan
- 補 qualification / assignment 相關 routes 與使用說明
- 對齊手動 QA 與 seed 文件

## 4. 資料模型建議

本票不新增資料模型。

## 5. API 路徑建議

本票不新增 API，但文件應至少涵蓋：

- qualification results routes
- assignment preview routes
- eligible campaigns workspace routes
- qualification context 相關 routes

## 6. 前端頁面 / 路由建議

文件中應明確列出主要驗收頁面，例如：

- `frontend/pages/campaigns/[campaignId].vue`
- `frontend/pages/campaigns/task-new-[campaignId].vue`
- `frontend/pages/my/eligible-campaigns.vue`
- `frontend/pages/my/tasks.vue`
- `frontend/pages/tasks/[taskId].vue`

## 7. Acceptance Criteria

- `README.md` 能反映 `T044` 到 `T049` 的實際完成狀態
- `NEXT_PHASE_PLAN.md` 不再停在過時的 phase 判斷
- qualification / assignment 相關 route、seed、manual QA 說明一致
- 文件中的啟動指令與驗收路徑可實際使用

## 8. Out of Scope

- 不做產品行銷文案重寫
- 不做 CI/CD 文件擴寫
- 不做 contributor guide 大改版

## 9. Backend Work Items

- 無 runtime code
- 視需要補文件中的 API baseline 說明

## 10. Frontend Work Items

- 無 runtime code
- 視需要補頁面路由與手動驗收說明

## 11. Test Items

- 文件指令實際可跑
- README / roadmap / manual QA / seed 文件之間內容一致

## 12. Risk / Notes

- 這張票是文件同步，不應順手改產品功能
- 若 qualification phase 尚未完整完成，文件應以實際狀態為準，不預寫未完成能力

## 13. 依賴關係（Dependencies）

主要依賴：

- `T049-qualification-aware-demo-seed-and-manual-qa-refresh`

建議最後做：

- 作為 qualification phase 的文件收斂票
