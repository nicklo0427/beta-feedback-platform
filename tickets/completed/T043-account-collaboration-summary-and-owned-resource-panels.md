# T043 - Account Collaboration Summary and Owned Resource Panels

## 1. 背景

目前 `Account` 已有：

- list / detail / create / edit
- current actor selector 基線

但 account detail 目前仍偏靜態，尚未真正反映：

- developer 擁有哪些 projects / campaigns
- tester 擁有哪些 device profiles
- 這個帳號目前在系統中的 collaboration footprint

## 2. 目標

讓 account detail 從單純的 profile shell，提升為可以理解該帳號在系統中的 owned resources 與 collaboration summary 的入口。

## 3. 範圍

本票只做 MVP 最小集合：

- developer account detail 顯示 owned projects / campaigns summary
- tester account detail 顯示 owned device profiles / assigned tasks / submitted feedback summary
- 視需要補最小 recent resource panel
- loading / empty / error / happy path 補齊

## 4. 資料模型建議

本票不新增複雜新 domain。

優先以 derived summary 為主，重用既有：

- `Project.owner_account_id`
- `DeviceProfile.owner_account_id`
- `Task.device_profile_id`
- `Feedback`

## 5. API 路徑建議

可選方案：

- 新增最小 account collaboration summary API
- 或以既有 `mine=true` / ownership query 組裝

若新增 API，建議收斂在：

- `GET /api/v1/accounts/{account_id}/summary`

若不新增 API，也需明確定義 frontend 組裝方式。

## 6. 前端頁面 / 路由建議

涉及頁面：

- `frontend/pages/accounts/[accountId].vue`

可補區塊：

- owned resources panel
- collaboration summary panel
- recent activity baseline

## 7. Acceptance Criteria

- developer account detail 可看到 owned projects / campaigns summary
- tester account detail 可看到 owned device profiles / assigned tasks / feedback summary
- summary 不需要 charts，但需可讀、可驗收
- 與既有 account detail flow 相容

## 8. Out of Scope

- 不做 public profile
- 不做 followers / social graph
- 不做 badges
- 不做 global leaderboard
- 不做 full activity timeline

## 9. Backend Work Items

- 視選擇補最小 summary API
- 或補 ownership query baseline 所需的最小擴充
- 補 pytest

## 10. Frontend Work Items

- 擴充 account detail 頁
- 補 summary / owned resources panels
- 保持 API 呼叫集中在 feature / service 層

## 11. Test Items

### 11.1 Backend Tests

- summary happy path
- zero-state
- not found

### 11.2 Frontend Tests

- typecheck
- build

### 11.3 E2E Tests

- developer account summary happy path
- tester account summary happy path
- zero-state
- regression：account detail / current actor selector

## 12. Risk / Notes

- 這張票不要擴成公開 profile 系統
- summary 應維持 derived baseline，不要提早做複雜 reputation engine

## 13. 依賴關係（Dependencies）

主要依賴：

- `T041-developer-workspace-mine-views-and-owned-resource-navigation`
- `T042-role-aware-demo-seed-and-owned-fixtures`
