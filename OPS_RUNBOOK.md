# Public Beta Ops Runbook

## 1. 目的

這份文件提供目前 repo 的最小 public beta 營運 baseline。

重點是讓團隊可以快速完成：

- 載入環境變數
- 啟動 backend / frontend
- 驗證 health 與 smoke
- 知道第一時間該看哪裡排查問題

## 2. 環境變數

repo 已提供一份範本：

- [.env.example](/Users/lowhaijer/projects/beta-feedback-platform/.env.example)

建議先複製成：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
cp .env.example .env.local
```

再用 shell 載入：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
set -a
source ./.env.local
set +a
```

補充：

- 目前 backend / frontend 都是直接從 process environment 讀值
- repo 沒有額外加 dotenv runtime，因此 `.env.local` 必須先由 shell 載入，或交給你的 process manager / deployment platform 載入

### 2.1 最小 public beta 建議值

- `BFP_APP_ENV=development` 或你的 beta 環境名稱
- `BFP_DATABASE_URL=sqlite+pysqlite:///./data/beta-feedback-platform.sqlite3`
- `BFP_AUTH_MODE=session_only`
- `BFP_AUTH_SESSION_COOKIE_SECURE=false`
  - 本機 HTTP 測試時維持 `false`
  - 若部署到 HTTPS beta 網址，請改成 `true`
- `NUXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1`
- `NUXT_PUBLIC_AUTH_MODE=session_only`

## 3. 本機 Public Beta 啟動方式

### 3.1 啟動 backend

建議先執行 migration：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform/backend
./.venv/bin/alembic -c alembic.ini upgrade head
```

再啟動 backend：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
set -a
source ./.env.local
set +a
mkdir -p runtime_logs
cd backend
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 2>&1 | tee ../runtime_logs/backend.log
```

補充：

- backend startup 現在也會用 Alembic baseline 自動補齊 schema
- 但對 beta / staging / production，仍建議把 `upgrade head` 當成 deploy 前明確步驟

### 3.2 啟動 frontend

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
set -a
source ./.env.local
set +a
mkdir -p runtime_logs
cd frontend
npm run dev -- --host 127.0.0.1 --port 3000 2>&1 | tee ../runtime_logs/frontend.log
```

### 3.3 主要檢查 URL

- backend health: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)
- backend docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- frontend app: [http://127.0.0.1:3000/](http://127.0.0.1:3000/)

## 4. Health Baseline

目前 `GET /api/v1/health` 會回傳最小 ops 訊號：

- `status`
- `service`
- `environment`
- `database_configured`
- `persistence_mode`
- `auth_mode`

public beta 本機 smoke 最理想的值應接近：

```json
{
  "status": "ok",
  "service": "beta-feedback-platform-backend",
  "environment": "development",
  "database_configured": true,
  "persistence_mode": "database",
  "auth_mode": "session_only"
}
```

## 5. Smoke Runbook

### 5.1 快速 smoke

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/public_beta_smoke.py --require-database-configured --require-session-only
```

這支 smoke script 目前會驗證：

- backend health 可用
- frontend root shell 可用
- auth register / me / logout 可用
- session cookie 可直接驅動 project create

### 5.1A Rollout evidence pack

若你要留下可交接的 rollout rehearsal 證據，建議直接跑：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/beta_rollout_verification.py --environment-label local-rehearsal --require-database-configured --require-session-only
```

這支腳本會輸出：

- `summary.json`
- `health.json`
- `page_checks.json`
- `smoke_stdout.txt`
- `smoke_stderr.txt`
- `evidence_pack.md`

預設輸出目錄：

- `runtime_artifacts/rollout-verification/<label>-<timestamp>/`

補充：

- 若 `--manual-qa-status` 不是 `pass`，evidence pack 會保守給出 `no_go`
- 這是刻意的，因為 public beta release gate 不應把 manual QA 視為已完成

### 5.2 Demo fixture smoke

若你也要驗證 seed / manual QA baseline：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/seed_demo_data.py --label public-beta-smoke
```

seed 完成後，請再搭配：

- [LOCAL_DEMO_SEED.md](/Users/lowhaijer/projects/beta-feedback-platform/LOCAL_DEMO_SEED.md)
- [MANUAL_QA.md](/Users/lowhaijer/projects/beta-feedback-platform/MANUAL_QA.md)
- [PUBLIC_BETA_LAUNCH_CHECKLIST.md](/Users/lowhaijer/projects/beta-feedback-platform/PUBLIC_BETA_LAUNCH_CHECKLIST.md)

## 6. Logs 與第一時間排查

### 6.1 預設 log 來源

目前 repo 沒有導入集中式 observability platform，所以第一時間請先看：

- backend process stdout / stderr
- frontend dev server stdout / stderr
- 瀏覽器 DevTools network / console

若照本文件的啟動指令跑，log 會在：

- `runtime_logs/backend.log`
- `runtime_logs/frontend.log`

補充：

- `runtime_logs/` 已加入 `.gitignore`
- 如果你不是用 `tee` 啟動，log 仍只會存在於當前 terminal session

### 6.2 常見故障排查順序

1. 先打 backend health
   - 確認 `status = ok`
   - 確認 `database_configured` 是否符合預期
   - 確認 `auth_mode` 是否為預期模式
   - 若是 database mode，確認 deploy 前是否已跑 `alembic upgrade head`
2. 再看 frontend root 是否 `200`
3. 再跑一次 `scripts/public_beta_smoke.py`
4. 如果 smoke fail：
   - 看 backend log 的 traceback
   - 看 frontend dev server log
   - 看 browser network response body
5. 如果你已經跑了 rollout evidence：
   - 先打開 `evidence_pack.md`
   - 先看 `Go / No-Go Rationale`
   - 再對照 `smoke_stderr.txt` 與 `page_checks.json`

### 6.3 常見故障類型

- `database_configured=false`
  - 通常代表 `BFP_DATABASE_URL` 沒有被載入到 process environment
- `auth_mode=session_with_header_fallback`
  - 通常代表你目前仍在 local QA / seed 模式
  - 若你預期是 beta/staging/production，請確認 `BFP_AUTH_MODE=session_only`
- frontend 無法連到 API
  - 先確認 `NUXT_PUBLIC_API_BASE_URL` 是否指向正確 backend
  - 再確認 backend CORS origins 是否包含 frontend origin
- 資料重啟後消失
  - 先確認 backend 是否真的啟動在 `database` persistence mode，而不是 memory fallback
- 啟動後出現 schema / table 缺失
  - 先手動跑一次 `./.venv/bin/alembic -c alembic.ini upgrade head`
  - 再重新確認 backend health 與 app startup

## 7. 本票刻意不做的事

這份 baseline 目前刻意不擴成：

- 完整 observability platform
- paging / on-call
- cloud vendor deployment template
- auto-scaling
- secret manager integration

它的目標只有一個：

- 讓新加入的人可以照 repo 文件，把目前系統拉起來、驗證、排查第一層問題

## 8. 發佈前最後核對

若你準備真的對外開 beta，請再逐項完成：

- [PUBLIC_BETA_LAUNCH_CHECKLIST.md](/Users/lowhaijer/projects/beta-feedback-platform/PUBLIC_BETA_LAUNCH_CHECKLIST.md)
