# T103 - Launch Blocker Fix Pass

## 背景

`T102` rehearsal 可能暴露 env、session、migration、runtime 或 UX blocker。這張票負責把 rehearsal 發現的問題集中修掉，避免 blocker 分散在臨時筆記或未追蹤 TODO。

## 目標

建立一輪 launch blocker fix pass，讓 public beta rehearsal 從「可以跑」推進到「可以放心開放小範圍試用」。

## 範圍

- 修復 `T102` rehearsal 標記為 blocker 的問題
- 更新必要 tests / docs / runbook
- 重跑 smoke 與 regression 確認 blocker 已消除

## API / Route / Data 建議

- 預設不改 API / route / schema。
- 若 blocker 必須改 schema，需新增 Alembic migration 並更新 launch checklist。
- 若 blocker 必須改 route 行為，需保留既有 URL contract 或明確記錄 breaking risk。

## Backend Work Items

- 修復 session-only、cookie、migration、database persistence 或 actor-aware guard 相關 blocker。
- 補對應 backend tests。
- 若影響 rollout scripts，更新 `public_beta_smoke.py` 或 `beta_rollout_verification.py`。

## Frontend Work Items

- 修復 public shell、auth handoff、dashboard、workspace role switch 或 error state blocker。
- 補對應 Playwright coverage。
- 確認 launch blocker 不會回退 local QA mode 行為。

## Acceptance Criteria

- `T102` 標記的 blocker 全部關閉或降級為已知限制。
- backend full tests 通過。
- frontend typecheck / build 通過。
- targeted Playwright 與 full Playwright 通過。
- `public_beta_smoke.py` 與 `beta_rollout_verification.py` 重新通過。

## Out of Scope

- 不做非 blocker 的產品 polish。
- 不新增 notification、auto matching、team/org model。
- 不移除 legacy `role`。

## Test Items

- backend full pytest
- frontend typecheck / build
- targeted Playwright for changed areas
- full Playwright
- public beta smoke
- rollout verification

## Risk / Notes

- 這張票的 scope 取決於 `T102` 結果，實作前應先列出 blocker 清單。
- 若 blocker 太大，應拆子票，不要把所有 hardening 塞進單一巨大 patch。

## Dependencies

- `T102`
