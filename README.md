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

並已進入 role-aware collaboration baseline 階段，包含：

- shell-level 頁面
- create / edit form
- safety metadata
- feedback review baseline
- feedback supplement / resubmission baseline
- reputation summary baseline
- account / ownership baseline
- current actor context
- role-aware homepage / tester inbox / developer review queue

### 1.1 目前階段判斷

截至目前為止，repo 可以視為已完成：

- `T011` 到 `T042`
- MVP 主流程閉環
- 第一輪產品化補強
- role-aware collaboration baseline
- 前端繁體中文文案整理

目前最重要的判斷是：

- 系統已不是單純 shell prototype
- 主要 create / edit / review flow 已能在 UI 中操作
- developer / tester 已有最小 role-aware 入口
- actor-aware mutation guards 與 developer owned workspace 已有 baseline
- role-aware demo seed 與 owned fixtures 已可直接支撐手動驗收

這代表下一步不應再擴新的核心 domain，而應優先補：

- account collaboration summary

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

- `accounts`
- `projects`
- `campaigns`
- `device_profiles`
- `eligibility`
- `tasks`
- `feedback`
- `safety`
- `reputation`

實作模式固定為：

- in-memory repository
- `validation / service / API` 三層 pytest
- 一致的錯誤格式：
  - `code`
  - `message`
  - `details`

### 4.2 Frontend

目前 frontend 已完成：

- homepage role-aware overview shell
- `accounts` list / detail / create / edit
- homepage IA / overview shell
- `projects` list / detail / create / edit
- `campaigns` list / detail / create / edit
- `campaign safety` create / edit
- `device profiles` list / detail / create / edit
- `eligibility rules` list / detail / create / edit
- `tasks` list / detail / create / edit
- `/my/tasks` tester inbox
- `feedback` list / detail / submit / edit
- `feedback review` panel
- `/review/feedback` developer review queue
- feedback supplement / resubmission flow
- `reputation summary` shell
- current actor selector

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
- `Uvicorn`
- `pytest`

### 5.3 補充說明

- `PostgreSQL` 目前尚未正式接入 runtime
- backend 目前仍是 in-memory 實作

## 6. 目錄結構

```text
beta-feedback-platform/
├── backend/
├── frontend/
├── scripts/
├── tickets/
├── NEXT_PHASE_PLAN.md
├── API_CONVENTIONS.md
├── ARCHITECTURE.md
├── DATA_MODEL_DRAFT.md
├── LOCAL_DEMO_SEED.md
├── MANUAL_QA.md
├── PRD.md
└── README.md
```

重點用途如下：

- `backend/`：FastAPI service
- `frontend/`：Nuxt 3 application
- `scripts/`：本地工具，例如 demo seed workflow
- `tickets/`：逐張開發票與工作拆解
- `NEXT_PHASE_PLAN.md`：`T029` 之後的下一階段規劃與 ticket 順序
- `LOCAL_DEMO_SEED.md`：本地 demo seed 使用說明
- `MANUAL_QA.md`：瀏覽器手動驗收清單

## 7. 本機啟動方式

### 7.1 啟動 backend

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform/backend
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

主要 URL：

- API base: `http://127.0.0.1:8000/api/v1`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/v1/health`

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
- `/my/tasks`
- `/review/feedback`

關聯 detail route 會依資料建立結果而定，例如：

- `/accounts/:accountId`
- `/projects/:projectId`
- `/campaigns/:campaignId`
- `/device-profiles/:deviceProfileId`
- `/tasks/:taskId`
- `/tasks/:taskId/feedback/:feedbackId`

## 10. 手動驗收文件

若你要直接在瀏覽器上做驗收，請看：

- [MANUAL_QA.md](/Users/lowhaijer/projects/beta-feedback-platform/MANUAL_QA.md)

這份文件會列出：

- 前置條件
- demo seed 方式
- current actor 與 role-aware 驗收前置

## 11. 接下來建議做什麼

下一個 phase 建議聚焦在：

- `Account Collaboration Summary`
- `Owned Resource Panels`

建議優先順序：

1. 補 account collaboration summary 與 owned resource panels
2. 再規劃下一輪 role-aware hardening 或更接近 production 的 access model

對應 tickets 為：

- `T043`

完整規劃請看：

- [NEXT_PHASE_PLAN.md](/Users/lowhaijer/projects/beta-feedback-platform/NEXT_PHASE_PLAN.md)
- 可以在網頁直接測試的主要清單
- 推薦驗收順序

## 11. 目前已知限制

- backend 仍是 in-memory repository
- backend restart 後資料會消失
- 目前尚未導入正式 auth
- current actor 目前只是 `X-Actor-Id` / localStorage baseline，不是 session 或 RBAC
- role-aware `mine=true` filters 只覆蓋目前已落地的 ownership baseline
- 目前尚未導入正式 persistence / migration
- 目前不做 notification、search、Steam / Desktop / Extension

## 12. 文件導覽

- [PRD.md](/Users/lowhaijer/projects/beta-feedback-platform/PRD.md)
- [ARCHITECTURE.md](/Users/lowhaijer/projects/beta-feedback-platform/ARCHITECTURE.md)
- [API_CONVENTIONS.md](/Users/lowhaijer/projects/beta-feedback-platform/API_CONVENTIONS.md)
- [DATA_MODEL_DRAFT.md](/Users/lowhaijer/projects/beta-feedback-platform/DATA_MODEL_DRAFT.md)
- [LOCAL_DEMO_SEED.md](/Users/lowhaijer/projects/beta-feedback-platform/LOCAL_DEMO_SEED.md)
- [MANUAL_QA.md](/Users/lowhaijer/projects/beta-feedback-platform/MANUAL_QA.md)
