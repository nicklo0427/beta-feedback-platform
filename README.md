# beta-feedback-platform

## 1. 專案簡介

`beta-feedback-platform` 是一個跨平台 Beta 測試媒合與回饋管理平台。

它不是互刷平台、不是評論交換平台、也不是灌量工具，而是聚焦在：

- 招募合適測試者
- 設定測試條件
- 派發測試任務
- 收集結構化回饋
- 建立雙向信譽基礎

目前 repo 已完成 MVP 核心閉環：

- `Project -> Campaign -> Device Profile -> Eligibility -> Task -> Feedback`

目前前端入口也已正式分層為：

- `/` 作為 public landing
- `/login`、`/register` 作為 public auth pages
- `/dashboard` 作為登入後首頁

並已進入 role-aware collaboration baseline 階段，包含：

- shell-level 頁面
- 全域 app shell / navigation foundation
- light / dark 雙主題
- create / edit form
- safety metadata
- feedback review baseline
- feedback supplement / resubmission baseline
- reputation summary baseline
- account / ownership baseline
- current actor context
- role-aware homepage / tester inbox / developer review queue
- qualification visibility
- assignment eligibility preview / guardrails
- tester eligible campaigns workspace
- task qualification context / drift warning
- tester participation request flow
- developer participation review queue
- participation request detail / candidate snapshot
- accepted participation request -> task assignment bridge
- request-to-task traceability / linked task status
- developer participation funnel overview
- actor-aware read visibility guards for participation-linked detail routes
- 全站 UI/UX refresh baseline
- workspace/dashboard refresh
- detail context rail
- form UX refresh
- desktop-first responsive pass

### 1.1 目前階段判斷

截至目前為止，repo 可以視為已完成：

- `T011` 到 `T094`
- MVP 主流程閉環
- 第一輪產品化補強
- role-aware collaboration baseline
- qualification / assignment clarity baseline
- participation intent baseline
- public / app 非技術背景文案簡化 baseline
- account collaboration summary 與 owned resource panels
- participation-aware demo seed 與 manual QA 文件
- 全站 UI/UX refresh phase
- public home / auth / dashboard / app shell separation phase

目前最重要的判斷是：

- 系統已不是單純 shell prototype
- 主要 create / edit / review flow 已能在 UI 中操作
- developer / tester 已有最小 role-aware 入口
- actor-aware mutation guards 與 developer owned workspace 已有 baseline
- role-aware demo seed 與 owned fixtures 已可直接支撐手動驗收
- account detail 已能顯示 collaboration footprint 與 owned resource summary
- tester 已能看見自己是否符合某個 campaign
- developer 指派 task 時已會被 qualification guard 阻擋
- task detail 與 tester inbox 已能看見 qualification context 與 drift warning
- tester 已能送出與撤回 participation request
- developer 已能審查 participation request，並查看 candidate snapshot detail
- developer 已能把 accepted participation request 橋接成 task
- tester 與 developer 已能看懂 request-to-task traceability
- participation-linked task detail 已補最小 actor-aware read guard
- session/auth baseline 已可用
- backend 已有 env-gated persistence baseline
- public beta 的 env / health / smoke / ops runbook 已補上
- public beta 的 manual QA / known limitations / launch checklist 已補上
- public beta rollout verification / evidence pack baseline 已補上
- global navigation shell、雙主題與桌機優先 responsive baseline 已補上
- public layout 與 app layout 已正式分層
- public homepage、auth entry flow 與登入後 `/dashboard` 已分開
- 主要 workspace / dashboard 已切到新的產品化資訊架構
- detail 頁已朝 `主欄 + context rail` 收斂
- create / edit forms 已收斂成一致的 sectioned form UX
- 高頻 workspace / queue / list 頁已套進一致的 app template 節奏
- public landing、login / register 與 app 內主流程頁已收斂成更少術語、更接近一般使用者能理解的產品語言

這代表 qualification、participation、participation-to-assignment、Alembic schema lifecycle、UI/UX refresh、以及非技術背景 copy baseline 都已完成，下一步不應回頭補同一批基礎能力，而應轉往：

- target environment rehearsal
- public beta launch decision
- post-beta hardening
- 更完整的 access / support / lifecycle 補強

換句話說：

- **功能型 MVP 已完成**
- **repo 內的 public beta rollout verification baseline 已完成**
- **是否正式 go-live 仍取決於目標環境 rehearsal 結果**

## 2. 第一階段平台範圍

第一階段平台固定支援：

- `Web`
- `Mobile Web`
- `PWA`
- `iOS`
- `Android`

第二階段才考慮：

- `Steam`
- `Desktop`
- `Extension`

## 3. 安全原則

本專案的安全方向固定為：

- 優先採用各平台官方測試 / 分發方式
- 不鼓勵來源不明安裝檔
- 不鼓勵關閉裝置安全防護
- 必須能表達來源標示、風險提示與最小 review 欄位

目前 `Campaign Safety` 已能表達：

- distribution channel
- source label / source URL
- risk level
- review status
- official channel only
- risk note

## 4. 目前已完成能力

### 4.1 Backend

目前 backend 已有以下模組與 API baseline：

- `auth`
- `accounts`
- `projects`
- `campaigns`
- `device_profiles`
- `eligibility`
- `tasks`
- `feedback`
- `safety`
- `reputation`
- `participation_requests`

實作模式固定為：

- in-memory + database persistence dual mode
- `validation / service / API` 三層 pytest
- 一致的錯誤格式：
  - `code`
  - `message`
  - `details`

### 4.2 Frontend

目前 frontend 已完成：

- public homepage landing
- global app shell with top bar / side navigation / mobile drawer
- public layout + app layout split
- light / dark theme toggle with persistence
- `login` / `register` session auth flow
- auth success redirect -> `/dashboard`
- `/dashboard` signed-in home
- public copy simplification for non-technical users
- in-product terminology simplification on high-frequency flows
- `accounts` list / detail / create / edit
- account collaboration summary / owned resource panels
- homepage IA / overview shell
- `projects` list / detail / create / edit
- `campaigns` list / detail / create / edit
- `campaign safety` create / edit
- `device profiles` list / detail / create / edit
- `eligibility rules` list / detail / create / edit
- `tasks` list / detail / create / edit
- `/my/tasks` tester inbox
- `/my/eligible-campaigns` tester 符合資格活動工作區
- `/my/participation-requests` tester participation workspace
- `feedback` list / detail / submit / edit
- `feedback review` panel
- `/review/feedback` developer review queue
- `/review/participation-requests` developer participation review queue
- `/review/participation-requests/:requestId` participation request detail / candidate snapshot
- `/review/participation-requests/:requestId/tasks/new` accepted request -> task bridge route
- feedback supplement / resubmission flow
- `reputation summary` shell
- current actor selector
- campaign detail qualification panel
- task assignment qualification preview / guardrails
- task qualification context / drift warning
- participation request create / review / detail
- participation accepted -> task bridge
- request-to-task traceability
- developer participation funnel overview
- actor-aware read visibility guard for participation-linked task detail
- workspace/dashboard refresh
- app shell redesign
- core app template harmonization for high-frequency workspace / queue / list pages
- detail context rail baseline
- sectioned form UX baseline
- responsive navigation / mobile smoke baseline

### 4.3 測試

目前 repo 已有：

- backend `pytest`
- frontend `Playwright E2E`
- frontend `typecheck`
- frontend `build`

## 5. 技術棧

### 5.1 Frontend

- `Nuxt 3`
- `Vue 3`
- `TypeScript`
- `Pinia`
- `SCSS`
- `Playwright`

### 5.2 Backend

- `FastAPI`
- `Pydantic`
- `SQLAlchemy`
- `Uvicorn`
- `pytest`

### 5.3 補充說明

- backend 目前已有 `BFP_DATABASE_URL` 驅動的 persistence mode
- session/auth 已有 HttpOnly cookie baseline
- schema lifecycle 已升級為 Alembic versioned migration baseline

## 6. 目錄結構

```text
beta-feedback-platform/
├── backend/
├── frontend/
├── scripts/
├── tickets/
├── .env.example
├── NEXT_PHASE_PLAN.md
├── API_CONVENTIONS.md
├── ARCHITECTURE.md
├── DATA_MODEL_DRAFT.md
├── LOCAL_DEMO_SEED.md
├── MANUAL_QA.md
├── OPS_RUNBOOK.md
├── PUBLIC_BETA_LAUNCH_CHECKLIST.md
├── PRD.md
└── README.md
```

重點用途如下：

- `backend/`：FastAPI service
- `frontend/`：Nuxt 3 application
- `scripts/`：本地工具，例如 demo seed workflow
- `tickets/`：逐張開發票與工作拆解
- `NEXT_PHASE_PLAN.md`：最新 roadmap 與目前 phase summary
- `LOCAL_DEMO_SEED.md`：本地 demo seed 使用說明
- `MANUAL_QA.md`：瀏覽器手動驗收清單
- `.env.example`：public beta 啟動用的環境變數範本
- `OPS_RUNBOOK.md`：public beta 啟動 / health / smoke / troubleshooting runbook
- `PUBLIC_BETA_LAUNCH_CHECKLIST.md`：public beta 上線前逐項核對清單

## 6.1 Qualification and Participation-to-Assignment Phase 已完成

目前已完成 qualification / assignment clarity、participation baseline、以及 participation-to-assignment bridge，包含：

- `T044` Qualification and assignment semantics draft
- `T045` Campaign qualification check API and current tester shell
- `T046` Task assignment eligibility preview and guardrails
- `T047` Tester eligible campaigns workspace
- `T048` Qualification context panels for task detail and inbox
- `T049` Qualification-aware demo seed and manual QA refresh
- `T051` Device Profile Install Channel Baseline and Form Support
- `T052` Qualification Evaluator Install Channel Fidelity
- `T053` Participation Intent Semantics Draft
- `T054` Tester Campaign Participation Request Flow
- `T055` Developer Participation Review Queue and Decision Actions
- `T056` Participation Request Detail and Candidate Snapshot Panels
- `T057` Participation-Aware Demo Seed and Docs Refresh
- `T058` Participation Accepted Request to Task Assignment Bridge
- `T059` Participation Request to Task Traceability and Status Panels
- `T060` Developer Candidate Overview and Participation Funnel Panels
- `T061` Access and Auth Hardening Draft
- `T062` Actor-Aware Read Visibility Guards
- `T063` Participation Assignment Seed and Docs Refresh
- `T064` Actor-Aware Read Visibility Expansion
- `T065` Session/Auth Baseline
- `T066` Persistence Baseline
- `T067` Public Beta Ops Baseline
- `T068` Public Beta QA and Launch Checklist
- `T069` Alembic Migration and Schema Lifecycle Baseline

這代表 `Eligibility -> Assignment -> Tester 參與 -> Developer Review -> Request-to-Task Bridge` 這段現在已具備：

- qualification read-only visibility
- assignment preview 與 mutation guard
- tester workspace entry
- assignment 後的 qualification context 與 drift warning
- participation request create / withdraw
- developer review queue / decision actions
- participation detail candidate snapshot
- accepted request -> task creation bridge
- request-to-task traceability
- candidate / participation funnel summary
- actor-aware read visibility baseline for participation-linked detail
- participation-aware seed 與手動驗收文件

## 7. 本機啟動方式

### 7.1 啟動 backend

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform/backend
./.venv/bin/alembic -c alembic.ini upgrade head
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

主要 URL：

- API base: `http://127.0.0.1:8000/api/v1`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/v1/health`

補充：

- database mode 現在以 Alembic migration 為 schema source of truth
- backend startup 也會自動嘗試補齊到 `head`
- 但對 beta / staging / production，仍建議把 `alembic upgrade head` 當成明確 deploy step

### 7.2 啟動 frontend

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform/frontend
npm run dev -- --host 127.0.0.1 --port 3000
```

主要 URL：

- frontend app: `http://127.0.0.1:3000`

### 7.3 本地 demo seed

若你需要快速建立一組可手動驗收的資料，請參考：

- [LOCAL_DEMO_SEED.md](/Users/lowhaijer/projects/beta-feedback-platform/LOCAL_DEMO_SEED.md)

最短指令：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/seed_demo_data.py
```

### 7.4 Public beta ops runbook

若你要用更接近 public beta 的方式啟動 / 驗證 stack，請看：

- [OPS_RUNBOOK.md](/Users/lowhaijer/projects/beta-feedback-platform/OPS_RUNBOOK.md)
- [PUBLIC_BETA_LAUNCH_CHECKLIST.md](/Users/lowhaijer/projects/beta-feedback-platform/PUBLIC_BETA_LAUNCH_CHECKLIST.md)

最短 smoke 指令：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/public_beta_smoke.py --require-database-configured --require-session-only
```

若你要直接產生 rollout evidence pack，請執行：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/beta_rollout_verification.py --environment-label local-rehearsal --require-database-configured --require-session-only
```

## 8. 常用驗證指令

### 8.1 Backend

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
PYTHONPATH=/Users/lowhaijer/projects/beta-feedback-platform/backend ./backend/.venv/bin/pytest -q -p no:cacheprovider
```

### 8.2 Frontend

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform/frontend
npm run typecheck
npm run build
npx playwright test --reporter=list --workers=1
```

## 9. 主要頁面入口

目前可直接打開的主要頁面包含：

- `/`
- `/accounts`
- `/projects`
- `/campaigns`
- `/device-profiles`
- `/tasks`
- `/my/projects`
- `/my/campaigns`
- `/my/eligible-campaigns`
- `/my/participation-requests`
- `/my/tasks`
- `/review/feedback`
- `/review/participation-requests`
- `/review/participation-requests/:requestId/tasks/new`

關聯 detail route 會依資料建立結果而定，例如：

- `/accounts/:accountId`
- `/projects/:projectId`
- `/campaigns/:campaignId`
- `/device-profiles/:deviceProfileId`
- `/tasks/:taskId`
- `/tasks/:taskId/feedback/:feedbackId`
- `/review/participation-requests/:requestId`

## 10. 手動驗收文件

若你要直接在瀏覽器上做驗收，請看：

- [MANUAL_QA.md](/Users/lowhaijer/projects/beta-feedback-platform/MANUAL_QA.md)

這份文件會列出：

- 前置條件
- demo seed 方式
- current actor 與 role-aware 驗收前置
- qualification / assignment 驗收路徑
- participation request / review / detail 驗收路徑
- participation-to-assignment bridge 與 request-to-task traceability 驗收路徑

## 11. 接下來建議做什麼

如果以目前這個 repo 狀態來看：

- 功能型 MVP：已完成
- public beta readiness 文件與驗收 baseline：已完成
- rollout verification / evidence pack baseline：已完成
- 是否正式對外開放：仍取決於你是否在目標環境跑完 launch checklist

以目前「逐張 ticket 推進、邊做邊驗收」的節奏估算，較合理的公開 beta 目標窗是：

- **2026 年 5 月 8 日**
- **到 2026 年 5 月 22 日前**

目前 public beta readiness 這一輪已完成：

- `T064` Actor-Aware Read Visibility Expansion
- `T065` Session/Auth Baseline
- `T066` Persistence Baseline
- `T067` Public Beta Ops Baseline
- `T068` Public Beta QA and Launch Checklist
- `T069` Alembic Migration and Schema Lifecycle Baseline
- `T070` Session-Only Environment Mode and Header Fallback Decommission
- `T071` Global Actor-Aware Read Visibility Hardening
- `T072` Task Resolution and Outcome Workflow Baseline
- `T073` Audit Trail and Activity Timeline Baseline
- `T074` Beta Environment Rollout Verification and Evidence Pack

接下來最值得優先補的方向：

1. 在真正的 beta target environment 跑一次完整 rehearsal，並保存產出的 evidence pack
2. 把 rollout rehearsal 暴露出的 blocker 收斂成 post-beta hardening ticket
3. 視需要再擴 auth / access hardening、task lifecycle、support tooling

這一輪公開 beta readiness 的收斂文件，請看：

- [NEXT_PHASE_PLAN.md](/Users/lowhaijer/projects/beta-feedback-platform/NEXT_PHASE_PLAN.md)
- [OPS_RUNBOOK.md](/Users/lowhaijer/projects/beta-feedback-platform/OPS_RUNBOOK.md)
- [PUBLIC_BETA_LAUNCH_CHECKLIST.md](/Users/lowhaijer/projects/beta-feedback-platform/PUBLIC_BETA_LAUNCH_CHECKLIST.md)
- [MANUAL_QA.md](/Users/lowhaijer/projects/beta-feedback-platform/MANUAL_QA.md)
- [tickets/T074-beta-environment-rollout-verification-and-evidence-pack.md](/Users/lowhaijer/projects/beta-feedback-platform/tickets/T074-beta-environment-rollout-verification-and-evidence-pack.md)

## 12. 目前已知限制

- 若未設定 `BFP_DATABASE_URL`，backend 仍會 fallback 到 in-memory mode
- database mode 現在依賴 Alembic migration；deploy 前應先執行 `upgrade head`
- `X-Actor-Id` 仍保留作為 local dev / seed fallback，不是正式 production identity model
- role-aware `mine=true` filters 只覆蓋目前已落地的 ownership baseline
- 目前不做 notification、search、Steam / Desktop / Extension

## 13. 文件導覽

- [PRD.md](/Users/lowhaijer/projects/beta-feedback-platform/PRD.md)
- [ARCHITECTURE.md](/Users/lowhaijer/projects/beta-feedback-platform/ARCHITECTURE.md)
- [API_CONVENTIONS.md](/Users/lowhaijer/projects/beta-feedback-platform/API_CONVENTIONS.md)
- [DATA_MODEL_DRAFT.md](/Users/lowhaijer/projects/beta-feedback-platform/DATA_MODEL_DRAFT.md)
- [LOCAL_DEMO_SEED.md](/Users/lowhaijer/projects/beta-feedback-platform/LOCAL_DEMO_SEED.md)
- [MANUAL_QA.md](/Users/lowhaijer/projects/beta-feedback-platform/MANUAL_QA.md)
- [OPS_RUNBOOK.md](/Users/lowhaijer/projects/beta-feedback-platform/OPS_RUNBOOK.md)
- [PUBLIC_BETA_LAUNCH_CHECKLIST.md](/Users/lowhaijer/projects/beta-feedback-platform/PUBLIC_BETA_LAUNCH_CHECKLIST.md)
