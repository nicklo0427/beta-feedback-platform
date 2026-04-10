# T060 - Developer Candidate Overview and Participation Funnel Panels

## 1. 背景

目前 developer 可以 review 單筆 request，也可以看單筆 candidate snapshot，但還缺少跨 campaign / 跨 request 的 overview。

## 2. 目標

建立 developer 端最小 candidate / participation funnel overview，讓 review 決策不只靠單筆 detail。

## 3. 範圍

- 在 developer workspace 或 campaign detail 顯示 participation funnel summary
- 顯示：
  - pending requests count
  - accepted requests count
  - linked tasks count
- 提供最小 candidate overview panel

## 4. 資料模型建議

優先使用 derived summary，不新增新 persistence。

建議 summary 至少包含：

- `pending_requests_count`
- `accepted_requests_count`
- `linked_tasks_count`
- `recent_participation_requests`

## 5. API 路徑建議

可考慮新增 read-only summary API：

- `GET /api/v1/campaigns/{campaign_id}/participation-summary`

或在既有 campaign detail / request queue response 內補 derived summary。

## 6. 前端頁面 / 路由建議

優先使用既有頁面：

- `frontend/pages/my/campaigns.vue`
- `frontend/pages/campaigns/[campaignId].vue`
- `frontend/pages/review/participation-requests.vue`

## 7. Acceptance Criteria

- developer 可在至少一個 workspace / detail 頁看到 participation funnel summary
- summary 能反映 pending / accepted / linked task 三段狀態
- 既有 request detail 仍可進一步 drill down

## 8. Out of Scope

- 不做 ranking
- 不做 search
- 不做 recommendation engine
- 不做 BI dashboard

## 9. Backend Work Items

- derived summary service / API
- 依 developer owned campaign 過濾資料

## 10. Frontend Work Items

- summary panels
- owned campaign participation overview

## 11. Test Items

- summary correctness
- empty state / zero state
- regression：campaign detail / my campaigns / review queue

## 12. Risk / Notes

- 這張票應維持 summary level，不要變成 candidate management system

## 13. 依賴關係（Dependencies）

主要依賴：

- `T058`
- `T059`

