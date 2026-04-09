# T056 - Participation Request Detail and Candidate Snapshot Panels

## 1. 背景

`T055` 會讓 developer 能 accept / decline requests，但 queue card 本身通常不夠做決策。developer 還需要一個最小 candidate context：

- tester 是誰
- 用哪個 device profile 申請
- qualification 狀態是什麼
- 最近的 collaboration summary 如何

## 2. 目標

建立 participation request detail 與 candidate snapshot panels，讓 developer 在不做 auto matching 的前提下，仍有基本決策上下文。

## 3. 範圍

本票只做 read-only detail context：

- backend request detail enriched response
- frontend request detail 頁
- candidate snapshot panels

## 4. 資料模型建議

不新增新 domain，但 request detail 建議至少帶：

- request baseline fields
- tester account summary snippet
- device profile summary snippet
- qualification snapshot
- campaign summary snippet

## 5. API 路徑建議

- `GET /api/v1/participation-requests/{request_id}`

可視需要重用既有 summary：

- account summary
- qualification context

## 6. 前端頁面 / 路由建議

涉及：

- `frontend/pages/review/participation-requests/[requestId].vue`
- `frontend/pages/review/participation-requests.vue`

## 7. Acceptance Criteria

- developer 可從 review queue 進入 request detail
- detail 頁可看見 tester / device profile / qualification / summary context
- 不新增 ranking，也不做 recommendation
- queue 與 detail 間導覽清楚

## 8. Out of Scope

- 不做 search
- 不做 sorting engine
- 不做 public candidate discovery
- 不做 recommendation score

## 9. Backend Work Items

- enriched request detail response
- ownership guard
- 視需要重用既有 summary service

## 10. Frontend Work Items

- request detail route
- snapshot panels
- queue card to detail navigation

## 11. Test Items

### 11.1 Backend

- request detail happy path
- ownership guard
- enriched response shape

### 11.2 Frontend

- queue -> detail navigation
- detail panels load / error / happy path

## 12. Risk / Notes

- 這張票的目標是「看得懂 candidate」，不是「幫 developer 自動決定 candidate」
- 要避免把 detail 頁膨脹成完整 CRM / ATS 介面

## 13. 依賴關係（Dependencies）

主要依賴：

- `T055-developer-participation-review-queue-and-decision-actions`

後續支撐：

- `T057-participation-aware-demo-seed-and-docs-refresh`

