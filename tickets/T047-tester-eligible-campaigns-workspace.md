# T047 - Tester Eligible Campaigns Workspace

## 1. 背景

目前 tester 已有：

- owned `Device Profiles`
- `/my/tasks` inbox

但還沒有一個 role-aware 入口可以看到：

- 自己目前符合哪些 campaigns
- 是被哪個 device profile 命中

這與 PRD 中「Tester 查看符合條件的 Campaign 或 Task」仍有落差。

## 2. 目標

建立 tester 的最小 eligible campaigns workspace，讓 tester 可以在一個頁面看到：

- 目前符合的 campaigns
- 命中的 device profile
- 進入 campaign detail 的入口

## 3. 範圍

本票只做 MVP 最小集合：

- backend 提供 current tester eligible campaigns list
- frontend 新增 tester workspace 頁面
- 顯示 qualifying device profile baseline
- loading / empty / error / role mismatch / happy path 補齊

## 4. 資料模型建議

本票優先重用：

- `Campaign`
- `EligibilityRule`
- `DeviceProfile.owner_account_id`
- qualification evaluator baseline

list item 除既有 campaign 欄位外，建議補：

- `qualifying_device_profile_ids`
- `qualification_summary`

## 5. API 路徑建議

建議新增：

- `GET /api/v1/campaigns?qualified_for_me=true`

行為建議：

- 使用 `X-Actor-Id`
- 只允許 `tester`
- 根據 owned device profiles 與 active eligibility rules 回傳結果

## 6. 前端頁面 / 路由建議

建議新增：

- `frontend/pages/my/eligible-campaigns.vue`

頁面至少包含：

- current actor selector
- tester role guard
- campaign cards
- qualifying device profile chips

首頁 tester 區塊可補：

- `Open eligible campaigns`

## 7. Acceptance Criteria

- tester 可在一個 role-aware 頁面看到目前符合的 campaigns
- 每個 campaign 至少顯示一個命中的 device profile
- 未選 actor、developer actor、無 owned device profiles 都有正確狀態
- backend / frontend / E2E 測試補齊

## 8. Out of Scope

- 不做申請任務
- 不做 campaign subscription
- 不做 recommendation ranking
- 不做 sorting engine

## 9. Backend Work Items

- 新增 qualified_for_me query baseline
- 驗證 current actor 與 owned device profiles 的推導邏輯
- 補 pytest

## 10. Frontend Work Items

- 新增 tester eligible campaigns workspace
- 首頁 tester 區塊補入口
- 保持 API 呼叫集中在 `features/campaigns/` 或相鄰 feature 層

## 11. Test Items

### 11.1 Backend Tests

- qualified campaigns happy path
- no owned device profiles
- missing actor
- role mismatch

### 11.2 Frontend Tests

- typecheck
- build

### 11.3 E2E Tests

- tester eligible campaigns happy path
- no owned device profiles state
- role mismatch state
- regression：homepage tester navigation / campaign detail

## 12. Risk / Notes

- 這張票不要擴成 marketplace 或 application flow
- 只需要提供 current tester 的最小 qualified campaigns view

## 13. 依賴關係（Dependencies）

主要依賴：

- `T044-qualification-and-assignment-semantics-draft`
- `T045-campaign-qualification-check-api-and-current-tester-shell`

後續支撐：

- `T049-qualification-aware-demo-seed-and-manual-qa-refresh`
