# T065 - Session/Auth Baseline

## 1. 背景

目前系統仍依賴 `X-Actor-Id` 與 localStorage current actor selector。這適合內部驗收，但不適合 public beta。若不先補最小 session/auth，對外使用者無法以正常方式登入，也無法安全地識別目前 actor。

## 2. 目標

建立 public beta 可用的最小登入 / session baseline，讓主要 workflow 不再依賴手動 header 模擬身份。

## 3. 範圍

- 新增最小 auth model
- 新增 register / login / logout / current-session API
- frontend 新增登入流程與 session state
- 既有 current actor 讀取改由 session 提供

## 4. 資料模型建議

本票建議在 `Account` 增加最小 auth 欄位：

- `email`
- `password_hash`
- `is_active`

另新增最小 session 概念：

- `actor_session`
  - `id`
  - `account_id`
  - `created_at`
  - `expires_at`

## 5. API 路徑建議

新增：

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

行為建議：

- 使用 HttpOnly session cookie
- current actor 由 session 推導，而不是由 header 任意指定
- `X-Actor-Id` 僅保留給 local seed / dev workflow，並透過明確 dev flag 控制

## 6. 前端頁面 / 路由建議

新增：

- `/login`
- `/register`

調整：

- homepage
- 所有目前依賴 `Current Actor Selector` 的頁面
- 全域 session state / current account 顯示

## 7. Acceptance Criteria

- 使用者可註冊、登入、登出
- 已登入使用者可透過 session 進入原本的主要 workflow
- 既有 role-aware 頁面不再依賴手動 actor selector 才能使用
- 未登入時，受保護頁面會導向 login 或顯示明確提示
- local seed / dev workflow 仍有最小可操作 fallback

## 8. Out of Scope

- 不做 OAuth
- 不做 social login
- 不做 password reset
- 不做 multi-factor auth
- 不做 organization/team membership

## 9. Backend Work Items

- auth schema / service / router
- session cookie issuing / revocation
- current actor dependency 改吃 session
- dev-only actor header fallback 機制

## 10. Frontend Work Items

- login / register form
- session bootstrap
- logout action
- 用 session 取代目前主要 current actor 使用方式

## 11. Test Items

- register / login / logout API tests
- session expiry / unauthenticated tests
- frontend auth happy path
- protected-route redirect / error state
- regression：existing role-aware pages still work after login

## 12. Risk / Notes

- 這張票要控制 scope，只做 public beta 最小可用 session/auth
- 不要順手擴成完整 auth platform
- 若 dev-only `X-Actor-Id` fallback 保留，必須明確隔離並文件化

## 13. 依賴關係（Dependencies）

主要依賴：

- `T061`
- 建議在 `T064` 後做

