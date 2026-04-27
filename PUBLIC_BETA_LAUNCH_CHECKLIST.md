# Public Beta Launch Checklist

## 1. 目的

這份文件提供 public beta 上線前最後一輪的逐項確認清單。

它不是功能規格，也不是 marketing checklist。它只負責回答一件事：

- 這個 repo 目前是否已準備好進入 public beta 試用

## 2. 使用方式

建議分成兩段執行：

1. `session-only beta smoke`
   - 驗證目標 beta 環境的 auth / persistence / health / shell
2. `full fixture regression`
   - 在本地 QA 環境使用 seed fixture 跑完整功能回歸

補充：

- 第一段偏「環境 readiness」
- 第二段偏「產品流程回歸」

## 3. Release Gates

以下項目全部滿足，才建議進入 public beta：

- [ ] backend health 為 `status = ok`
- [ ] `database_configured = true`
- [ ] `persistence_mode = database`
- [ ] `auth_mode = session_only`
- [ ] `scripts/public_beta_smoke.py` 成功
- [ ] `scripts/beta_rollout_verification.py` 已產出一份 evidence pack
- [ ] backend 全量 pytest 成功
- [ ] frontend `npm run typecheck` 成功
- [ ] frontend `npm run build` 成功
- [ ] frontend Playwright 全量成功
- [ ] [DUAL_ROLE_TEST_PLAN.md](/Users/lowhaijer/projects/beta-feedback-platform/DUAL_ROLE_TEST_PLAN.md) 的 T095-T101 測試矩陣已完成
- [ ] [MANUAL_QA.md](/Users/lowhaijer/projects/beta-feedback-platform/MANUAL_QA.md) 的 public beta 必驗案例完成
- [ ] 已知限制已整理並可對外說明
- [ ] [OPS_RUNBOOK.md](/Users/lowhaijer/projects/beta-feedback-platform/OPS_RUNBOOK.md) 中的啟動與排查步驟可直接使用

## 4. Session-Only Beta Smoke

### 4.1 環境設定

- [ ] `.env.local` 已從 [/.env.example](/Users/lowhaijer/projects/beta-feedback-platform/.env.example) 建立
- [ ] `BFP_DATABASE_URL` 已設定
- [ ] `BFP_AUTH_MODE=session_only`
- [ ] `NUXT_PUBLIC_API_BASE_URL` 指向正確 backend
- [ ] `NUXT_PUBLIC_AUTH_MODE=session_only`
- [ ] 若 beta 為 HTTPS，`BFP_AUTH_SESSION_COOKIE_SECURE=true`
- [ ] deploy 前已執行 `./backend/.venv/bin/alembic -c backend/alembic.ini upgrade head`

### 4.2 啟動檢查

- [ ] backend 已可啟動
- [ ] frontend 已可啟動
- [ ] [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health) 或對應 beta health URL 可正常回 `200`
- [ ] [http://127.0.0.1:3000/](http://127.0.0.1:3000/) 或對應 beta frontend URL 可正常回首頁 shell

### 4.3 Smoke Script

建議指令：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/public_beta_smoke.py --require-database-configured --require-session-only
```

確認項目：

- [ ] backend health 成功
- [ ] frontend shell 成功
- [ ] register 成功
- [ ] register / auth `me` 會回傳 `roles`，且 dual-role payload 可保留 `developer / tester`
- [ ] auth `me` 成功
- [ ] logout 後 `me` 回 `401`
- [ ] session cookie 可直接建立 project

### 4.4 Rollout Evidence Pack

建議指令：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/beta_rollout_verification.py --environment-label beta-rollout --require-database-configured --require-session-only --manual-qa-status pending
```

確認項目：

- [ ] evidence pack 成功輸出
- [ ] `summary.json` 與 `health.json` 可讀
- [ ] `evidence_pack.md` 已包含：
  - health 結果
  - smoke 結果
  - 關鍵頁面檢查
  - manual QA 狀態
  - 已知限制
  - go / no-go 結論
- [ ] 若 launch 當天 manual QA 已完成，已用最終狀態重跑或補齊 go / no-go 結論

## 5. Full Fixture Regression

這一段建議在本地 QA 環境執行，而不是直接在對外 beta 環境執行。

原因：

- seed fixture 仍使用 current actor / `X-Actor-Id` baseline 建立 ownership fixture
- 它適合功能回歸，不適合當成 public beta 真實登入流程

### 5.1 QA 環境設定

- [ ] QA backend 可啟動
- [ ] 若要跑完整 fixture regression，`BFP_AUTH_MODE=session_with_header_fallback`
- [ ] 若 frontend 要顯示 fallback actor selector，`NUXT_PUBLIC_AUTH_MODE=session_with_header_fallback`
- [ ] `BFP_DATABASE_URL` 仍建議維持為 database mode

### 5.2 Seed 與驗收

- [ ] 執行 [scripts/seed_demo_data.py](/Users/lowhaijer/projects/beta-feedback-platform/scripts/seed_demo_data.py) 成功
- [ ] 依 [LOCAL_DEMO_SEED.md](/Users/lowhaijer/projects/beta-feedback-platform/LOCAL_DEMO_SEED.md) 確認 fixture graph 正常
- [ ] seed fixture 內可看到 developer-only、tester-only、dual-role 三種帳號
- [ ] 依 [MANUAL_QA.md](/Users/lowhaijer/projects/beta-feedback-platform/MANUAL_QA.md) 完成 qualification / participation / request-to-task / feedback regression

## 6. Public Beta 必驗案例

上線前至少要完成以下人工驗收：

- [ ] login / register / logout
- [ ] dual-role register、app shell 工作視角切換與 `/dashboard` 開發者 / 測試者視角切換
- [ ] session-only 模式下的 homepage 與 account summary
- [ ] project create / campaign create
- [ ] tester feedback submit / developer review
- [ ] participation review queue 可正常讀取
- [ ] participation-linked task detail 在正確 actor 下可讀
- [ ] 非本人 / 非擁有者讀取敏感 detail 會出現正確 error state
- [ ] backend 關掉時，frontend 會顯示可理解的錯誤狀態，而不是白頁

### 6.1 Dual-Role Account 必驗

完整測試方式與預期結果請看 [DUAL_ROLE_TEST_PLAN.md](/Users/lowhaijer/projects/beta-feedback-platform/DUAL_ROLE_TEST_PLAN.md)。

- [ ] `roles` 是權限來源，legacy `role` 只作為 primary fallback / 相容欄位
- [ ] dual-role account 可在同一 session 進入 developer-only 與 tester-only 主流程頁
- [ ] single-role account 缺少 capability 時仍看到清楚 role mismatch / permission state
- [ ] active workspace role 只影響 frontend 視角，不會送到 backend 當授權依據
- [ ] active workspace role localStorage persistence 正常，重新整理後仍保留可用視角

## 7. Known Limitations To State Clearly

目前建議在 beta onboarding 或內部發佈說明中明確寫出：

- schema lifecycle 現在依賴 Alembic migration；deploy 需先執行 `upgrade head`
- `X-Actor-Id` 仍保留作為 local QA / seed fallback，不是正式 production identity model
- current beta 僅支援：
  - `Web`
  - `Mobile Web`
  - `PWA`
  - `iOS`
  - `Android`
- 不包含 notification、search overhaul、auto matching、team/org model

## 8. 發佈日當天建議順序

1. 載入正式 beta env vars
2. 啟動 backend
3. 啟動 frontend
4. 確認 health
5. 跑 `public_beta_smoke.py`
6. 跑 `beta_rollout_verification.py` 產出 evidence pack
7. 用真實 beta 帳號手動走 login / project create / feedback review 短流程
8. 再開放對外試用

## 9. 若出問題先做什麼

- 先看 [OPS_RUNBOOK.md](/Users/lowhaijer/projects/beta-feedback-platform/OPS_RUNBOOK.md)
- 先打 health endpoint
- 再跑 `scripts/public_beta_smoke.py`
- 再看最新那份 `evidence_pack.md`
- 再看 backend / frontend process logs

若上面三步還無法定位，再判斷是否需要暫停 beta 開放。
