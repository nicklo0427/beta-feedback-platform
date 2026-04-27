# T086 - Auth Page and Entry Flow Alignment

## 1. 背景

當 public homepage 與 app shell 開始分層後，`/login` 與 `/register` 也需要明確對齊 public brand language，並把登入成功後的 handoff 固定化。否則首頁像 public product，但 auth 完成後的進場節奏仍會顯得斷裂。

## 2. 目標

讓：

- `/login`
- `/register`

都成為 public auth pages，並把 auth success redirect 統一導向 `/dashboard`。

## 3. 範圍

- auth pages 掛到 public layout
- auth copy / CTA / back-home language 對齊 public homepage
- login / register success redirect 統一進 `/dashboard`
- 已登入時進 auth 頁，自動導回 `/dashboard`

## 4. Entry Flow 建議

- 未登入使用者：
  - 從 `/` 點進 `/login` 或 `/register`
- 登入 / 註冊成功：
  - 統一導到 `/dashboard`
- 已登入使用者：
  - 再訪 `/login` 或 `/register` 時，不應停留在 auth form

## 5. API / Route 建議

不新增 API。

route 維持：

- `/login`
- `/register`

但成功導向的預設目標應改為：

- `/dashboard`

## 6. 前端頁面 / 路由建議

主要修改：

- `frontend/pages/login.vue`
- `frontend/pages/register.vue`
- auth session guard / redirect logic

視需要調整：

- public layout header CTA
- shared auth copy helpers

## 7. Acceptance Criteria

- `/login`、`/register` 與 public homepage 的品牌語言一致
- login success -> `/dashboard`
- register success -> `/dashboard`
- 已登入進 auth 頁會被導回 `/dashboard`
- 不改 backend auth API

## 8. Out of Scope

- 不改 auth backend schema
- 不做 multi-step onboarding
- 不做 forgot password / email verification

## 9. Backend Work Items

- 無新的 runtime 工作

## 10. Frontend Work Items

- auth page brand language alignment
- auth success redirect 統一
- auth guard / already-signed-in redirect
- 補 entry flow regression 測試

## 11. Test Items

- frontend `typecheck`
- frontend `build`
- login success redirect regression
- register success redirect regression
- already-signed-in auth route redirect regression
- public auth page shell regression

## 12. Risk / Notes

- 這張票不該把 auth flow 擴張成 onboarding system
- 目標是讓登入前產品體驗與登入後 dashboard handoff 變清楚

## 13. 依賴關係（Dependencies）

- `T084`
- 建議在 `T085` 後做
