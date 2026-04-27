# T032 - Current Actor Context and Ownership Baseline

## 1. 背景

即使 `Account` CRUD 建好了，若系統仍沒有 current actor 與 ownership baseline，後續的：

- 我的 project
- 我的 device profiles
- tester inbox
- developer review queue

都仍無法成立。

因此這張票要補的是：

- current actor context
- ownership baseline

而不是完整 auth。

## 2. 目標

建立 MVP 階段最小的 current actor / ownership flow，讓系統能知道：

- 現在是誰在操作
- 新建的 root resource 應屬於誰
- 哪些 list 應可支援「只看我的資料」

## 3. 範圍

本票只做最小集合：

- frontend current actor selector
- backend 讀取 current actor baseline
- `Project.owner_account_id`
- `DeviceProfile.owner_account_id`
- create flow 自動帶 owner
- list / detail 最小 ownership 顯示或過濾

## 4. 資料模型建議

建議直接持有 owner 的資源：

- `Project.owner_account_id`
- `DeviceProfile.owner_account_id`

衍生規則：

- `Campaign` 的 developer owner 由 `Project` 推導
- `Task` 的 developer owner 由 `Campaign` 推導
- `Task` 的 tester side anchor 由 `device_profile_id` 推導
- `Feedback` 的 tester side anchor 由 `device_profile_id` 推導

## 5. API 路徑建議

本票不要求大量新增 endpoint，但建議補：

- list query 例如 `mine=true` 的 baseline
- 或 request header baseline，例如 `X-Actor-Id`

實作上可接受：

- `GET /api/v1/projects?mine=true`
- `GET /api/v1/device-profiles?mine=true`

但應保持 MVP 最小集合。

## 6. 前端頁面 / 路由建議

至少需要：

- current actor selector
- ownership-aware projects list
- ownership-aware device profiles list

selector placement 建議：

- homepage
- global layout/header

## 7. Acceptance Criteria

- frontend 可切換 current actor
- 建立 `Project` 時會自動帶入 owner
- 建立 `DeviceProfile` 時會自動帶入 owner
- 可顯示 root resource 的 owner baseline
- 至少一個 list 支援「只看我的資料」
- backend / frontend tests 補齊

## 8. Out of Scope

- 不做正式 session
- 不做 token
- 不做 RBAC
- 不做 multi-account switching history
- 不做 organization ownership

## 9. Backend Work Items

- 擴充 `projects`、`device_profiles` schema / service / API
- 建立最小 actor resolution baseline
- 補 ownership 相關 pytest

## 10. Frontend Work Items

- 建立 current actor selector
- create form 串 current actor
- list / detail 顯示 owner baseline
- 視需要建立最小 actor composable / store

## 11. Test Items

### 11.1 Backend Tests

- create with actor happy path
- missing actor / invalid actor
- `mine=true` baseline

### 11.2 Frontend Tests

- actor selector persistence
- create flow 帶入 owner

### 11.3 E2E Tests

- 切換 actor 後建立 project
- 切換 actor 後建立 device profile
- mine filter / owner display

## 12. Risk / Notes

- 這張票不應變成 auth 架構重做
- owner baseline 先只落在 root resource，避免一次擴太大

## 13. 依賴關係（Dependencies）

主要依賴：

- `T031-account-crud-and-role-shell`

後續支撐：

- `T033-tester-task-inbox-and-assigned-task-actions`
- `T034-developer-feedback-review-queue-and-filters`
- `T035-feedback-supplement-response-and-resubmission`
