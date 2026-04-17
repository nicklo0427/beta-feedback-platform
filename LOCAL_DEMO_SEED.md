# Local Demo Seed Workflow

## 1. 目的

這份文件對應 `T028-local-demo-data-seeding-workflow`，並一路收斂到 public beta 前的本地 QA fixture workflow。

目前已補上 `T042-role-aware-demo-seed-and-owned-fixtures`、`T049-qualification-aware-demo-seed-and-manual-qa-refresh` 與 `T057-participation-aware-demo-seed-and-docs-refresh`，所以這份 seed 不再只是主流程資料，而是可直接支撐 role-aware、qualification / assignment、以及 participation flow 驗收的 fixture graph。

用途是用一個命令，透過既有 HTTP API 建立一組本地 demo graph，方便手動驗收與錄影 demo。

補充：

- 這份 seed 主要服務的是 `full fixture regression`
- 它不是 `session-only beta smoke`
- 若你要驗證 public beta 真實上線條件，請先看：
  - [OPS_RUNBOOK.md](/Users/lowhaijer/projects/beta-feedback-platform/OPS_RUNBOOK.md)
  - [PUBLIC_BETA_LAUNCH_CHECKLIST.md](/Users/lowhaijer/projects/beta-feedback-platform/PUBLIC_BETA_LAUNCH_CHECKLIST.md)

建立的資料至少包含：

- 1 筆 `developer` account
- 1 筆 `tester` account
- 1 筆 `Project`
- 2 筆 `Campaign`
- 1 筆 `Campaign Safety`
- 2 筆 `Eligibility Rule`
- 3 筆 `Device Profile`
- 3 筆 `Task`
- 1 筆 `Feedback`
- 2 筆 `Participation Request`

## 2. 前置條件

### 2.1 Backend

請先啟動 backend，預設位址為：

- `http://127.0.0.1:8000`

對應 API base URL：

- `http://127.0.0.1:8000/api/v1`

若你要成功建立這份 role-aware fixture，建議 QA 環境設定：

- `BFP_DATABASE_URL` 已設定
- `BFP_AUTH_MODE=session_with_header_fallback`
- `NUXT_PUBLIC_AUTH_MODE=session_with_header_fallback`

原因：

- script 仍會傳 `X-Actor-Id`
- 這是為了快速建立 owned fixture graph
- 它適合本地 QA，不適合拿來代表 public beta 真實登入流程

### 2.2 Frontend

若你想直接用 script 輸出的前端 detail URL 做手動驗收，也請先啟動 frontend，預設位址為：

- `http://127.0.0.1:3000`

## 3. 執行方式

在 repo 根目錄執行：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/seed_demo_data.py
```

若你要指定不同 API / frontend URL，可加參數：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/seed_demo_data.py \
  --api-base-url http://127.0.0.1:8000/api/v1 \
  --frontend-base-url http://127.0.0.1:3000
```

若你想自訂本次 seed label：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/seed_demo_data.py --label local-qa
```

## 4. 建立出的資料內容

這支 script 目前會建立：

- `Account`
  - `Role-Aware Developer <label>`
  - `Role-Aware Tester <label>`
- `Project`
  - `Owned Project Sandbox <label>`
  - owner 會是上面的 developer
- `Campaign`
  - `Qualified Campaign Round <label>`
  - 用來驗證 qualification pass / fail 與 assignment preview / guard
  - owner 由 project 推導
  - `target_platforms = ["ios", "android"]`
- `Campaign`
  - `Qualification Drift Round <label>`
  - 用來驗證 task detail / inbox 的 drift warning
  - owner 由 project 推導
  - `target_platforms = ["ios", "android"]`
- `Campaign Safety`
  - `distribution_channel = "testflight"`
  - `review_status = "approved"`
- `Eligibility Rule`
  - qualified campaign 底下有一筆 iOS 規則
  - `platform = "ios"`
  - `os_version_min = "17.0"`
  - `install_channel = "testflight"`
- `Eligibility Rule`
  - drift campaign 底下先建立一筆 iOS 規則，再立即更新成 Android 規則
  - 用來讓既有 task 產生 qualification drift
- `Device Profile`
  - 一筆 iOS 測試裝置
  - owner 會是上面的 tester
  - 這筆會通過 qualified campaign 的資格檢查
- `Device Profile`
  - 第二筆 iOS 測試裝置
  - owner 會是上面的 tester
  - 這筆會通過 qualified campaign 的資格檢查，並用來建立已接受的 participation request
- `Device Profile`
  - 一筆 Android 測試裝置
  - owner 會是上面的 tester
  - 這筆會在 qualified campaign 上顯示 qualification fail，也可用來驗證 assignment guard
- `Task`
  - qualified task 會成功指派到 iOS device profile
  - 建立 feedback 後可直接拿來驗證 review queue / submitted flow
- `Task`
  - drift task 也會先成功指派到 iOS device profile
  - 之後因 drift campaign 的 eligibility rule 被更新，這筆 task 會顯示 qualification drift
- `Task`
  - accepted-request linked task 會由已 accepted 的 participation request 橋接建立
  - 用來驗證 request-to-task traceability、actor-aware task detail read、以及 candidate snapshot 到 task detail 的鏈路
- `Feedback`
  - 建立後由既有 backend flow 推進 task 狀態
  - feedback 會保留 `review_status = submitted`，方便手動驗證 `T027`
- `Participation Request`
  - 一筆 `pending` request
  - 會出現在 tester 的 `/my/participation-requests` 與 developer 的 `/review/participation-requests`
- `Participation Request`
  - 一筆 `accepted` request
  - 會出現在 tester 的 `/my/participation-requests`
  - 而且已經橋接建立對應 task
  - 可直接用來驗證已處理狀態、request detail 快照、linked task 與 traceability

這代表：

- 這支 seed 已可直接驗證主流程與 role-aware baseline
- 可以直接拿來驗證：
  - `/my/projects`
  - `/my/campaigns`
- `/my/eligible-campaigns`
- `/my/participation-requests`
- `/my/tasks`
- `/review/feedback`
- `/review/participation-requests`
- `/review/participation-requests/:requestId`
- 首頁 current actor 切換與 role-aware summary
- campaign detail qualification panel
- task assignment qualification preview
- task qualification drift panel
- participation request create / review / detail
- participation accepted -> task assignment bridge
- request-to-task traceability
- participation-linked task detail read guard
- developer participation funnel summary

## 5. Script 輸出內容

成功執行後，script 會輸出：

- backend health 狀態
- developer / tester actor IDs
- 建立出的每筆 record ID
- 可直接打開的 frontend detail URL
- qualification / assignment 驗證用頁面 URL
- role-aware workspace URLs
- 對應的 backend API detail URL

你可以直接用它列出的 URL 做手動驗收。

若你要完整的瀏覽器驗收順序，請再對照：

- [MANUAL_QA.md](/Users/lowhaijer/projects/beta-feedback-platform/MANUAL_QA.md)

## 6. 手動 smoke 驗證建議

script 成功後，至少確認以下頁面：

1. `Qualified campaign detail`
2. `Qualified campaign qualification panel`
3. `Qualified campaign task create form`
4. `Drift task detail`
5. `Tester eligible campaigns workspace`
6. `Tester inbox`
7. `Tester participation requests workspace`
8. `Developer participation review queue`
9. `Participation request detail`
10. `Participation-linked task detail`
11. `Pending participation request task-bridge route`

若要驗收 role-aware flow，建議再補：

12. `Accounts detail`
13. 首頁 current actor 切換
14. `/my/projects`
15. `/my/campaigns`
16. `/review/feedback`
17. `Feedback detail`

推薦直接打開 script 輸出的 frontend URLs。

## 7. 重要限制

- 若未設定 `BFP_DATABASE_URL`，backend 仍可能跑在 in-memory mode
- 若你真的用 in-memory mode 跑 seed，backend restart 後資料仍會消失
- 這是本地 demo workflow，不是正式 fixture system
- 這支 script 只調用現有 product API，不會直接碰 repository internals
- 這支 script 會傳 `X-Actor-Id`，用既有 current actor baseline 建立 ownership fixture
- 這表示它需要 fallback-enabled QA 環境，不適合當成 strict `session_only` beta smoke
- 目前 seed 已使用 `install_channel` 驗證 qualification fidelity，因此 iOS fixture 會使用 `testflight`，Android fixture 會使用 `play-store`

## 8. 實作備註

- 對外顯示文案用 `Mobile Web`
- internal / API enum value 仍維持 `h5`
- 每次重跑 script 都會建立一組新的 demo graph
- 若你要驗收 role-aware flow，請在首頁 `Current Actor` selector 中選擇 script 輸出的 developer / tester account
- 若你要驗證 ineligible assignment fail，請用 developer actor 打開 qualified campaign 的 task create form，並選擇那筆 Android device profile
- 若你要驗證 drift warning，請直接打開 script 輸出的 drift task detail 與 `/my/tasks`
- 若你要驗證 participation review queue，請切到 developer actor 打開 `/review/participation-requests`
- 若你要驗證已接受的 participation request 狀態與 linked task，請切到 tester actor 打開 `/my/participation-requests`
- 若你要驗證 manual bridge flow，請先在 developer review queue 接受 pending request，再開 `/review/participation-requests/:requestId/tasks/new`
- 若你要驗證 public beta 上線條件，不要只跑 seed；請另外執行：
  - [scripts/public_beta_smoke.py](/Users/lowhaijer/projects/beta-feedback-platform/scripts/public_beta_smoke.py)
