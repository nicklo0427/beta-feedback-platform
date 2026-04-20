# T094 - In-Product Terminology Simplification and Helper Copy

## 1. 背景

即使 `T093` 把 public 面改成更容易理解的語言，如果登入後的 app 內頁仍然大量使用工程、QA、資料模型導向的詞，使用者仍會在進入產品後立刻失速。

目前 app 內常見的高門檻用語包含：

- qualification
- participation request
- assignment status
- resolution outcome
- review queue
- structured feedback

這些詞對熟悉流程的人沒有問題，但對沒有開發背景、主要靠使用情境理解產品的人，仍然太抽象。

## 2. 目標

把登入後主流程頁的可見文案收斂成：

- 主標題更口語
- 狀態與 CTA 更好懂
- 必要時用 helper copy 補充系統概念

重點不是降低專業度，而是降低理解門檻。

## 3. 範圍

- `/dashboard`
- `/my/*`
- `/review/*`
- 高頻主流程 detail 頁
  - campaign detail
  - task detail
  - feedback detail
  - participation request detail
- 主要高頻 form 的欄位說明與 helper text
- 相關 i18n key

## 4. 文案策略建議

原則：

- 主標題用人話
- 次要說明才補系統詞
- CTA 用「要做的事」命名，不用資料模型命名

建議方向：

- `Participation requests` -> `參與申請`
- `Qualification result` -> `是否符合這次測試條件`
- `Assignment status` -> `目前任務安排`
- `Resolution outcome` -> `這次任務的結果`
- `Review queue` -> `待你處理的回饋 / 申請`

helper copy 應補：

- 這個區塊在做什麼
- 這個狀態代表什麼
- 你下一步可以做什麼

## 5. API / Route 建議

本票不新增 API。

route contract 維持不變。

## 6. 前端頁面 / 路由建議

優先修改：

- `frontend/pages/dashboard.vue`
- `frontend/pages/my/tasks.vue`
- `frontend/pages/my/eligible-campaigns.vue`
- `frontend/pages/my/participation-requests.vue`
- `frontend/pages/review/feedback.vue`
- `frontend/pages/review/participation-requests.vue`
- `frontend/pages/campaigns/[campaignId].vue`
- `frontend/pages/tasks/[taskId].vue`
- `frontend/pages/tasks/[taskId]/feedback/[feedbackId].vue`
- `frontend/pages/review/review-participation-request-[requestId].vue`
- 相關 form component 與 i18n keys

## 7. Acceptance Criteria

- dashboard 與主流程頁的主要標題、按鈕、狀態文案更口語
- 高頻頁面不再大量出現陌生英文術語
- 常見狀態有 helper copy，不需要靠背景知識猜意思
- `zh-TW / en` 同步更新
- 不改 backend API、不改 route contract

## 8. Out of Scope

- 不改資料模型名稱
- 不做全站 i18n 完成票
- 不重做 dashboard / shell / page template 結構
- 不改 backend response shape

## 9. Backend Work Items

- 無新的 runtime 工作

## 10. Frontend Work Items

- 收斂 dashboard 與主流程頁主標題
- 重寫 queue、detail、context panel 的 helper copy
- 調整 CTA label 與狀態文案
- 對齊主要 form 的 helper text 與 validation 說明
- 更新對應的 i18n keys

## 11. Test Items

- frontend `typecheck`
- frontend `build`
- `dashboard-shell.spec.ts`
- `my-tasks.spec.ts`
- `eligible-campaigns.spec.ts`
- `review-feedback.spec.ts`
- `review-participation-requests.spec.ts`
- `tasks-shell.spec.ts`
- 驗證高頻主流程頁在 `zh-TW / en` 下都能以更口語的方式成立

## 12. Risk / Notes

- 如果改得太口語，可能會失去流程精準度，所以要保留必要的 helper copy
- 目標不是把專業感拿掉，而是讓不懂開發流程的人也能順著 UI 前進
- 這張票適合在 `T093` 後做，避免 public 面與 app 內頁語氣不一致

## 13. 依賴關係（Dependencies）

- `T093`
