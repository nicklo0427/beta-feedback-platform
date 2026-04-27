# T071 - Global Actor-Aware Read Visibility Hardening

## 1. 背景

`T064` 與 `T062` 已經補了一部分 read guard，但目前仍不是完整的 read visibility policy。若 beta 後繼續擴功能，越晚收斂讀取邊界，修補成本越高。

## 2. 目標

建立較完整的 actor-aware read visibility baseline，明確定義 public read、related-actor read、owner-only read。

## 3. 範圍

- account summary / detail
- campaign summary / related views
- task / feedback / participation read
- reputation summary read visibility
- frontend error state / empty state 一致性

## 4. 資料模型建議

本票不新增產品資料模型。

重點是 read policy matrix，而不是新增新的 owner 關聯。

## 5. API 路徑建議

沿用既有 read routes，逐步補 guard：

- `GET /api/v1/accounts/...`
- `GET /api/v1/campaigns/...`
- `GET /api/v1/tasks/...`
- `GET /api/v1/feedback/...`
- `GET /api/v1/participation-requests/...`
- `GET /api/v1/reputation/...`

## 6. 前端頁面 / 路由建議

沿用既有頁面，主要補：

- detail error state
- role mismatch state
- ownership mismatch state
- unauthenticated state

## 7. Acceptance Criteria

- 敏感 detail / summary 不再匿名可讀
- owner-only / related-actor-only routes 有一致的後端錯誤碼
- frontend 會顯示清楚、可理解的讀取限制提示
- 公開 campaign discovery 不被誤鎖

## 8. Out of Scope

- 不做 database row-level security
- 不做 organization/team RBAC
- 不做 share-link / invite token

## 9. Backend Work Items

- 定義 read visibility matrix
- 逐 route 收斂 read guard
- 補 service / API tests

## 10. Frontend Work Items

- 統一 read-side error handling
- 收斂 detail / queue 的 actor-aware read state

## 11. Test Items

- backend targeted read guard tests
- frontend detail / queue read regression
- Playwright actor-mismatch / unauthenticated regression

## 12. Risk / Notes

- 這張票很容易把公開 discovery 一起鎖死，必須明確保留 public routes
- 需要避免 read guard 與 session-only 政策互相打架

## 13. 依賴關係（Dependencies）

主要依賴：

- `T064`
- `T070`

