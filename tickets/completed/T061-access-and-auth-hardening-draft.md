# T061 - Access and Auth Hardening Draft

## 1. 背景

目前系統仍以 `X-Actor-Id` + localStorage current actor 作為 MVP baseline。這足以支撐開發與手測，但若 workflow 繼續往下走，read visibility 與 mutation guard 需要更清楚的長期方向。

## 2. 目標

先用文件定義下一階段的 access / auth hardening 邊界，避免 runtime 票各自發散。

## 3. 範圍

- 更新 `DATA_MODEL_DRAFT.md`
- 定義：
  - current actor baseline 的限制
  - read visibility baseline
  - 最小 auth migration path
  - 哪些 flow 未來必須有正式 session / auth

## 4. 資料模型建議

本票不新增 runtime model。

但應定義未來可能需要的概念：

- `actor_session`
- `identity_provider`
- `access_scope`

## 5. API 路徑建議

本票不新增 runtime API。

文件中應標示：

- 哪些 routes 目前可 anonymous read
- 哪些 routes 未來應收斂成 actor-aware read

## 6. 前端頁面 / 路由建議

本票不新增新頁面。

## 7. Acceptance Criteria

- 文件中已清楚定義 auth hardening 的目標與邊界
- 可直接支撐後續 read guard / auth migration tickets

## 8. Out of Scope

- 不做正式 auth
- 不做 token
- 不做 OAuth
- 不做 RBAC framework

## 9. Backend Work Items

- 無 runtime 變更

## 10. Frontend Work Items

- 無 runtime 變更

## 11. Test Items

- 文件一致性檢查

## 12. Risk / Notes

- 這張票必須刻意避免直接進入正式 auth implementation

## 13. 依賴關係（Dependencies）

主要依賴：

- 無

