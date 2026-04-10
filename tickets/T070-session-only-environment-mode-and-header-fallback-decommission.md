# T070 - Session-Only Environment Mode and Header Fallback Decommission

## 1. 背景

`T065` 已提供 session/auth baseline，但 `X-Actor-Id` fallback 仍存在，主要是為了 local QA 與 seed workflow。這在 beta 後會變成環境行為不一致的風險。

## 2. 目標

把 session-only 環境模式正式定義清楚，並把 header fallback 限縮到 local QA / seed，不再讓 beta / staging / production 依賴它。

## 3. 範圍

- environment mode 收斂
- fallback 行為與文件收斂
- seed / QA / ops 文件同步
- frontend 對未登入與 session 過期狀態提示收斂

## 4. 資料模型建議

本票不新增產品資料模型。

## 5. API 路徑建議

沿用既有 auth API：

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

## 6. 前端頁面 / 路由建議

沿用既有：

- `/login`
- `/register`
- session-required routes

## 7. Acceptance Criteria

- beta / staging / production 預設為 session-only
- local QA / seed 可明確地在受控模式下使用 header fallback
- 文件已寫清楚兩種模式的差異
- frontend 對 unauthenticated / session_expired 狀態有一致提示

## 8. Out of Scope

- 不做完整 OAuth
- 不做 email verification
- 不做 password reset

## 9. Backend Work Items

- 收斂 fallback env gating
- 收斂錯誤碼與 auth mode 文件
- 更新 health / ops / seed 說明

## 10. Frontend Work Items

- 收斂 session-only UI 提示
- 確認 session 過期 / 未登入時的 redirect 或 error state 一致

## 11. Test Items

- session-only smoke
- local QA fallback smoke
- frontend auth-related E2E regression

## 12. Risk / Notes

- seed workflow 仍需要某種 fixture-friendly 模式，不能直接粗暴刪掉 fallback
- 這張票的目標是「明確隔離」，不是完全移除所有 QA 便利工具

## 13. 依賴關係（Dependencies）

主要依賴：

- `T065`
- `T067`
- `T068`

