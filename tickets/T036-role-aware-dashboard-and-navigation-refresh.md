# T036 - Role-Aware Dashboard and Navigation Refresh

## 1. 背景

`T023` 已整理首頁 IA，但當時系統還沒有：

- account
- current actor
- role-aware inbox / queue

一旦 `T031` 到 `T035` 完成，首頁與導航就需要從「通用產品入口」進一步提升成「依角色導向的入口」。

## 2. 目標

建立最小的 role-aware dashboard / navigation baseline，讓：

- developer 看得到自己的工作入口
- tester 看得到自己的工作入口
- current actor 切換後，入口與摘要會跟著改變

## 3. 範圍

本票只做 MVP 最小集合：

- role-aware homepage / overview refresh
- current actor 狀態顯示
- developer / tester 入口整理
- 最小 summary cards

## 4. 資料模型建議

本票以既有資料推導為主，不新增新 domain。

首頁 summary 可先依據既有資料與 queue / inbox API 取回，例如：

- developer：
  - my projects
  - active campaigns
  - submitted feedback to review
- tester：
  - my device profiles
  - assigned tasks
  - needs_more_info feedback count

## 5. API 路徑建議

優先重用既有 list APIs 與 queue APIs。

若需要最小 summary endpoint，應保持務實，例如：

- `GET /api/v1/me/overview`

但若現有 queries 足夠，可先不新增 endpoint。

## 6. 前端頁面 / 路由建議

優先更新：

- `frontend/pages/index.vue`

並整理主要入口，例如：

- `/projects`
- `/campaigns`
- `/device-profiles`
- `/my/tasks`
- `/review/feedback`
- `/accounts`

## 7. Acceptance Criteria

- current actor 可在首頁明顯辨識
- 首頁入口會依 role 顯示重點入口
- 至少有最小 summary cards
- 導航層級比目前更清楚反映 developer / tester 差異
- frontend typecheck / build / Playwright 通過

## 8. Out of Scope

- 不做 marketing site 重設計
- 不做完整 auth dashboard
- 不做 analytics system
- 不做 charts / BI

## 9. Backend Work Items

- 若必要，補最小 summary query
- 否則以既有 API 為主

## 10. Frontend Work Items

- 更新首頁 IA / dashboard shell
- 顯示 current actor 與 role
- 整理主要導航入口
- 樣式變更前需先判斷：
  - 共用樣式放 `assets/scss`
  - 單頁專屬放 `.vue scoped style`

## 11. Test Items

### 11.1 Frontend Tests

- typecheck
- build

### 11.2 E2E Tests

- role-aware homepage
- actor switch 導致入口改變
- developer / tester 主要入口可達

## 12. Risk / Notes

- 這張票的目標是入口整理，不是視覺翻新
- 不要順手擴成大規模 layout 重構

## 13. 依賴關係（Dependencies）

主要依賴：

- `T033-tester-task-inbox-and-assigned-task-actions`
- `T034-developer-feedback-review-queue-and-filters`
- `T035-feedback-supplement-response-and-resubmission`

後續支撐：

- `T037-role-aware-docs-and-manual-qa-refresh`
