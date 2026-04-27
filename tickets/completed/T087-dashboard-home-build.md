# T087 - Dashboard Home Build

## 1. 背景

一旦 `/` 固定變成 public landing，就需要一個真正的登入後首頁，承接 auth success redirect 與日常工作流的第一落點。現在的首頁雖然已有 role-aware summary 基線，但它仍與 public/home 心智混在一起。

## 2. 目標

新增 `/dashboard`，成為登入後首頁，並以角色化工作總覽呈現 developer / tester 的主要摘要、queue 與 CTA。

## 3. 範圍

- 新增 `/dashboard`
- 建立 developer / tester 兩種 dashboard 狀態
- 成為 login/register success redirect landing page
- 未登入進 `/dashboard` 時走既有 auth gate

## 4. Dashboard 內容建議

### Developer

- 我的專案
- 我的活動
- participation review queue
- feedback review queue
- 最近待處理 / quick actions

### Tester

- 我的任務
- 符合資格的活動
- 我的 participation requests
- 最近待辦 / quick actions

dashboard 應以：

- summary cards
- queue cards
- next actions

為主，而不是純導航集合或 timeline-first 頁。

## 5. API / Route 建議

新增 route：

- `/dashboard`

不新增 backend API，盡量重用現有 summary / mine / review queue APIs。

## 6. 前端頁面 / 路由建議

主要新增 / 修改：

- `frontend/pages/dashboard.vue`
- auth success redirect
- dashboard 相關 i18n 與 summary shell

## 7. Acceptance Criteria

- `/dashboard` 存在且可作為登入後首頁
- developer / tester 看到不同內容
- login / register 成功後會進 `/dashboard`
- 未登入進 `/dashboard` 時不會看到 dashboard 內容

## 8. Out of Scope

- 不做 timeline-first dashboard
- 不做 analytics / charts
- 不新增 backend dashboard API aggregation layer

## 9. Backend Work Items

- 無新的 runtime 工作

## 10. Frontend Work Items

- 建立 dashboard page
- developer / tester summary modules
- quick action cards
- auth gate / redirect 對齊
- 補 dashboard regression

## 11. Test Items

- frontend `typecheck`
- frontend `build`
- dashboard unauthenticated redirect
- dashboard developer state
- dashboard tester state
- auth success redirect to dashboard

## 12. Risk / Notes

- 這張票要避免把 dashboard 做成巨大的資訊總匯
- 目標是成為登入後首頁，而不是取代所有 workspace 頁

## 13. 依賴關係（Dependencies）

- `T084`
- `T086`
