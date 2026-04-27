# T104 - Beta Onboarding Polish

## 背景

目前 public home、register、login、dashboard 與 app shell 已完成分層，也已支援 dual-role account。下一步需要讓第一次進來的 vibe coder 與好奇試用者更快知道該怎麼開始，降低註冊後進入 dashboard 的迷路感。

## 目標

優化 public beta onboarding：

- 未登入者知道要註冊或登入
- 註冊後知道自己可以用開發者 / 測試者視角做什麼
- 空狀態與 CTA 能引導下一步
- dual-role 使用者理解工作視角切換不是帳號切換

## 範圍

- register success / dashboard first-run copy
- dashboard empty states
- workspace role switch helper copy
- developer / tester 起步 CTA
- public home 到 auth / dashboard 的 handoff copy

## API / Route / Data 建議

- 不改 backend API
- 不新增 route
- 可使用既有 `/register?role=developer|tester` query behavior
- 可新增 frontend-only helper text / i18n keys

## Backend Work Items

- 預期無 backend work。
- 若 frontend 需要資料判斷 first-run state，優先使用既有 summary endpoints。

## Frontend Work Items

- 調整 dashboard developer / tester empty state copy。
- 在 dual-role switch 附近補簡短說明，避免被理解成切換帳號。
- 確認 public CTA、register role preselect、dashboard onboarding 文案一致。
- 更新 `zh-TW` / `en` i18n。

## Acceptance Criteria

- 新帳號註冊後可清楚看到下一步 CTA。
- developer-only、tester-only、dual-role 三種帳號的 dashboard empty state 都可理解。
- dual-role switch helper copy 說明 active workspace role 只是工作視角。
- 首頁 CTA 到 register / login / dashboard 的文案一致。

## Out of Scope

- 不新增完整 onboarding wizard。
- 不新增 email verification。
- 不新增 notification。
- 不改 public homepage 主要 layout。

## Test Items

- frontend typecheck / build
- Playwright for register query preselect
- Playwright for dashboard empty states
- Playwright for workspace role switch helper visibility
- manual responsive smoke at 390px

## Risk / Notes

- 文案需要維持非技術語氣，避免回到內部工具感。
- 不應把 active workspace role 描述成安全或權限來源。

## Dependencies

- `T101`
- 建議在 `T102` 後做，避免 target env blocker 打斷 polish。
