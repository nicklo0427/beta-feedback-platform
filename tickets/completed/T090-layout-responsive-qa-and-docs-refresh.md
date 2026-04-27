# T090 - Layout Responsive, QA, and Docs Refresh

## 1. 背景

當 public layout、auth pages、dashboard 與 app shell 都完成 redesign 後，仍需要最後一張收 responsive、驗收與文件，避免視覺已改完但 QA baseline 與文件仍停留在舊結構。

## 2. 目標

為新的 layout phase 做最後收尾：

- desktop-first responsive pass
- QA / Playwright 更新
- 文件同步

## 3. 範圍

- 驗 public/home/auth/dashboard/app shell 路徑
- 補 desktop / mobile responsive smoke
- 更新 README / MANUAL_QA / 相關驗收說明
- 補 shell / home / auth / dashboard 相關 Playwright

## 4. Responsive 建議

至少驗證：

- desktop 1280px
- mobile 390px

必須可用的路徑：

- `/`
- `/login`
- `/register`
- `/dashboard`
- 一個 app list page
- 一個 app detail page

## 5. API / Route 建議

本票不新增 API。

本票也不新增功能 route。

## 6. 前端頁面 / 路由建議

主要調整：

- responsive breakpoints / shell behavior
- public header / app nav mobile 狀態
- Playwright specs

主要同步文件：

- `README.md`
- `MANUAL_QA.md`
- 視需要補 UI/UX phase 狀態文件

## 7. Acceptance Criteria

- public/home/auth/dashboard/app shell 在桌機與手機都不破版
- shell/home/auth/dashboard 的 Playwright 驗收到位
- README / MANUAL_QA 與新 layout 結構一致
- 新增 `/dashboard` 的驗收路徑已寫進文件

## 8. Out of Scope

- 不做完整 accessibility audit
- 不做 visual diff pipeline 建置
- 不改 backend API

## 9. Backend Work Items

- 無新的 runtime 工作

## 10. Frontend Work Items

- responsive pass
- shell / home / auth / dashboard regression
- 更新 manual QA
- 更新 README 中的 layout / route 說明

## 11. Test Items

- frontend `typecheck`
- frontend `build`
- Playwright：
  - public homepage
  - auth flow
  - dashboard
  - app shell
  - mobile nav
  - one list page
  - one detail page

## 12. Risk / Notes

- 這張票不是再做大設計，而是收尾與對齊
- 如果前面 `T084` 到 `T089` 還在大幅變動，就不應太早做這張票

## 13. 依賴關係（Dependencies）

- `T085`
- `T086`
- `T087`
- `T088`
- `T089`
