# T041 - Developer Workspace Mine Views and Owned Resource Navigation

## 1. 背景

目前系統已經有：

- `/my/tasks` tester inbox
- `/review/feedback` developer review queue
- `projects?mine=true`

但 developer side 還缺少明確的 owned workspace 入口，無法在 UI 中快速集中看到：

- 自己的 projects
- 自己的 campaigns
- 自己擁有的主流程入口

## 2. 目標

補 developer 的最小 workspace views 與 owned resource navigation，讓 developer 能以 `mine` 為主線操作已擁有的資源。

## 3. 範圍

本票只做 MVP 最小集合：

- campaign list 補 `mine=true`
- 新增 developer workspace 頁面
- 至少提供：
  - `/my/projects`
  - `/my/campaigns`
- 與既有 current actor selector / ownership baseline 串接

## 4. 資料模型建議

本票不新增新資料模型。

核心依賴：

- `Project.owner_account_id`
- `Campaign` 由 `Project` 推導的 developer ownership
- current actor

## 5. API 路徑建議

建議補：

- `GET /api/v1/campaigns?mine=true`

並重用：

- `GET /api/v1/projects?mine=true`

若已有 `status` filter，應可與 `mine=true` 併用。

## 6. 前端頁面 / 路由建議

建議新增：

- `frontend/pages/my/projects.vue`
- `frontend/pages/my/campaigns.vue`

首頁 developer 區塊與 review queue 頁可補連結：

- `Open my projects`
- `Open my campaigns`

## 7. Acceptance Criteria

- developer 可集中看到自己的 projects
- developer 可集中看到自己的 campaigns
- mine views 只顯示屬於 current developer 的資源
- tester actor 進入 developer workspace 時會得到明確 role mismatch 提示
- loading / empty / error / happy path 補齊

## 8. Out of Scope

- 不做 global search
- 不做 saved views
- 不做 project / campaign analytics dashboard
- 不做 team workspace

## 9. Backend Work Items

- 補 `campaigns?mine=true`
- 確保 `projects?mine=true` 與 current actor baseline 一致
- 補 pytest

## 10. Frontend Work Items

- 新增 developer workspace pages
- 補首頁 / 導航入口
- 重用既有 list / card / state pattern

## 11. Test Items

### 11.1 Backend Tests

- `campaigns?mine=true` happy path
- no actor
- tester actor mismatch

### 11.2 Frontend Tests

- typecheck
- build

### 11.3 E2E Tests

- developer workspace happy path
- empty state
- role mismatch
- regression：homepage developer actions

## 12. Risk / Notes

- 這張票不要做成完整 dashboard
- 先把 mine views 與 owned navigation 補齊即可

## 13. 依賴關係（Dependencies）

主要依賴：

- `T039-actor-aware-campaign-safety-and-eligibility-mutation-guards`

後續支撐：

- `T043-account-collaboration-summary-and-owned-resource-panels`
