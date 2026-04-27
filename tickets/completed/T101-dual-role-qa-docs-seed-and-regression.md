# T101 - Dual-Role QA, Docs, Seed, and Regression

Status: completed.

## 1. 背景

`T095-T100` 會改變 account 模型、auth payload、backend role guards、registration UI、app shell 與 dashboard behavior。這是一個跨層產品模型變更，需要獨立的 QA / docs / seed 收斂票。

## 2. 目標

把 dual-role account phase 收斂到可驗收狀態：

- seed 覆蓋 dual-role / developer-only / tester-only
- docs 和 manual QA 反映新模型
- backend 與 frontend regression 穩定
- public beta checklist 補上 dual-role 行為

## 3. 範圍

- demo seed
- README
- MANUAL_QA
- PUBLIC_BETA_LAUNCH_CHECKLIST
- backend regression tests
- frontend E2E regression
- smoke runbook notes

## 4. API / Route / Data 建議

- 不新增 runtime API
- 文件需明確記錄：
  - `roles` 是權限來源
  - `role` 是 legacy 相容欄位
  - active workspace role 只影響 frontend 視角

## 5. Backend Work Items

- 更新 seed data
- 補 full backend regression 目標清單
- 確認 migration lifecycle 文件

## 6. Frontend Work Items

- 補 dual-role E2E
- 補 shell switch E2E
- 補 register / account form E2E
- 更新 manual QA screenshots / steps if applicable

## 7. Acceptance Criteria

- seed 內至少有一個 dual-role account
- manual QA 可驗 developer-only、tester-only、dual-role 三種帳號
- README 描述 dual-role account 和 workspace role switch
- full backend tests 通過
- frontend typecheck / build 通過
- targeted Playwright 通過

## 8. Out of Scope

- 不新增新產品功能
- 不新增 notification / search / matching
- 不移除 legacy `role`
- 不做 organization/team model

## 9. Test Items

- backend full tests
- frontend typecheck
- frontend build
- auth shell E2E
- dashboard shell E2E
- my tasks / eligible campaigns E2E
- review feedback / review participation E2E
- smoke for public home -> register -> dashboard

## 10. Risk / Notes

- 這張票應在 `T095-T100` 都完成後做
- 文件要避免把 active workspace role 描述成 backend permission
- 若 full E2E 太慢，至少保留一組 targeted regression 和 manual QA checklist

## 11. Dependencies

- `T095`
- `T096`
- `T097`
- `T098`
- `T099`
- `T100`
