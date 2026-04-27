# T102 - Target Beta Environment Rehearsal

## 背景

`T095-T101` 已完成 dual-role account baseline 與本地回歸文件。下一步需要用接近 public beta 的設定跑一次 target environment rehearsal，確認 session-only auth、database persistence、migration、frontend shell 與 smoke scripts 在實際 beta 設定下穩定。

## 目標

建立一份可重複執行的 beta rehearsal 流程，回答：

- 目標環境是否能正確啟動 backend / frontend
- database 與 Alembic migration 是否可用
- session-only auth 是否可用
- public beta smoke 與 rollout evidence 是否能產出可信結果

## 範圍

- 目標 beta env vars 檢查
- backend migration rehearsal
- backend health / auth / persistence smoke
- frontend public shell / auth / dashboard smoke
- `public_beta_smoke.py` 與 `beta_rollout_verification.py` evidence output
- rehearsal 結果文件化

## API / Route / Data 建議

- 不新增 backend API
- 不改 route contract
- rehearsal 應覆蓋：
  - `/api/v1/health`
  - `/`
  - `/login`
  - `/register`
  - `/dashboard`

## Backend Work Items

- 確認 `BFP_DATABASE_URL`、`BFP_AUTH_MODE=session_only`、session cookie 設定在 target env 可用。
- 執行 `alembic upgrade head` 並確認 `accounts.roles` migration 已套用。
- 跑 `scripts/public_beta_smoke.py --require-database-configured --require-session-only`。
- 跑 `scripts/beta_rollout_verification.py --require-database-configured --require-session-only` 並保存 evidence pack。

## Frontend Work Items

- 確認 `NUXT_PUBLIC_API_BASE_URL` 指向 target backend。
- 確認 `NUXT_PUBLIC_AUTH_MODE=session_only` 下不顯示 local QA actor selector。
- 手動檢查 public home、login、register、dashboard shell。

## Acceptance Criteria

- backend health 回傳 `status=ok`、`database_configured=true`、`persistence_mode=database`、`auth_mode=session_only`。
- migration 可從乾淨資料庫套到 head。
- public beta smoke 通過。
- rollout evidence pack 可讀且包含 go / no-go 結論。
- 若 rehearsal 發現 blocker，需整理成 `T103` input。

## Out of Scope

- 不修 launch blocker；本票只負責 rehearsal 與記錄。
- 不新增產品功能。
- 不做正式 production observability。

## Test Items

- backend full pytest
- frontend typecheck / build
- public beta smoke
- rollout verification
- manual smoke for `/`、`/login`、`/register`、`/dashboard`

## Risk / Notes

- target env 的 cookie secure / domain / CORS 設定最容易和 local 不同。
- seed fixture 不應直接跑在 public beta target env，除非使用隔離 QA database。

## Dependencies

- `T101`
