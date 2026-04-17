# T082 - Homepage Intro and Auth Entry Separation

## 1. 背景

目前首頁已具備 role-aware dashboard baseline，但登入前與登入後的資訊節奏仍有點混在一起。對第一次進站的使用者來說，首頁應先像產品 landing page，而不是先看到偏 workspace / internal panel 感的資訊堆疊。

另外，`登入 / 註冊` CTA 目前仍偏向被包在 panel / dashboard 節奏內。這讓登入前的使用者不容易一眼理解：

- 這個產品是做什麼的
- 我現在該先註冊還是先登入
- 登入之後會進入什麼樣的工作區

## 2. 目標

把首頁收斂成兩種明確狀態：

- 未登入：
  - 以產品介紹與角色價值為主
  - `登入 / 註冊` CTA 清楚可見，並從 panel 感抽離
- 已登入：
  - 才進入目前的 role-aware workspace / dashboard panel

## 3. 範圍

- 重做 `/` 的登入前資訊架構
- 重排登入前首頁的 hero / intro / CTA 區塊
- 調整 `login / register` 與首頁的進場節奏與導覽邏輯
- 保留既有 route：
  - `/`
  - `/login`
  - `/register`
- 保留既有 session/auth API 與 route contract

## 4. 資訊架構建議

首頁至少拆成：

- Hero：
  - 產品定位
  - 角色摘要
  - `登入`
  - `建立帳號`
- Product value section：
  - 給開發者的價值
  - 給測試者的價值
- Workflow preview：
  - `Project -> Campaign -> Participation -> Task -> Feedback`
- Logged-in workspace handoff：
  - 僅在已登入時顯示目前 dashboard / panel

## 5. API 路徑建議

本票不新增 API。

## 6. 前端頁面 / 路由建議

- 主要修改：
  - `frontend/pages/index.vue`
  - `frontend/pages/login.vue`
  - `frontend/pages/register.vue`
- 視需要調整：
  - `frontend/layouts/default.vue`
  - 共享 shell / CTA 元件

## 7. Acceptance Criteria

- 未登入時的首頁，第一屏以產品介紹與登入/註冊 CTA 為主
- `登入 / 註冊` CTA 不再被包在 dashboard / panel 主視覺裡
- 已登入時首頁仍可進入 role-aware workspace / dashboard
- 不改 backend API
- 不改既有 URL
- `zh-TW / en` 文案都同步成立

## 8. Out of Scope

- 不改 auth backend
- 不改 session model
- 不做多步 onboarding flow
- 不做 marketing site 多頁 routing

## 9. Backend Work Items

- 無新的 runtime 工作

## 10. Frontend Work Items

- 重排首頁未登入狀態的版面
- 收斂 CTA hierarchy
- 已登入 / 未登入首頁切換節奏
- login / register 與首頁之間的 copy / CTA 一致化
- 補齊 i18n keys 與 Playwright 驗收

## 11. Test Items

- frontend `typecheck`
- frontend `build`
- homepage unauthenticated shell regression
- homepage authenticated shell regression
- login / register navigation flow
- `zh-TW / en` i18n regression

## 12. Risk / Notes

- 這張票要避免把首頁做成完全獨立站點，否則會和現有 app shell 斷裂
- 關鍵是「登入前 landing 感」與「登入後 workspace handoff」要清楚，不是大幅擴張 marketing 頁面系統

## 13. 依賴關係（Dependencies）

主要依賴：

- `T075` 到 `T081`
- `T065`

