# Local Demo Seed Workflow

## 1. 目的

這份文件對應 `T028-local-demo-data-seeding-workflow`。

用途是用一個命令，透過既有 HTTP API 建立一組本地 demo graph，方便手動驗收與錄影 demo。

建立的資料至少包含：

- 1 筆 `Project`
- 1 筆 `Campaign`
- 1 筆 `Campaign Safety`
- 1 筆 `Device Profile`
- 1 筆 `Task`
- 1 筆 `Feedback`

## 2. 前置條件

### 2.1 Backend

請先啟動 backend，預設位址為：

- `http://127.0.0.1:8000`

對應 API base URL：

- `http://127.0.0.1:8000/api/v1`

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

- `Project`
  - `Manual QA Sandbox <label>`
- `Campaign`
  - `Closed Beta Round 1 <label>`
  - `target_platforms = ["h5", "ios"]`
- `Campaign Safety`
  - `distribution_channel = "testflight"`
  - `review_status = "approved"`
- `Device Profile`
  - 一筆 iOS 測試裝置
- `Task`
  - 指派到上面的 device profile
  - create 時狀態為 `assigned`
- `Feedback`
  - 建立後由既有 backend flow 推進 task 狀態
  - feedback 會保留 `review_status = submitted`，方便手動驗證 `T027`

## 5. Script 輸出內容

成功執行後，script 會輸出：

- backend health 狀態
- 建立出的每筆 record ID
- 可直接打開的 frontend detail URL
- 對應的 backend API detail URL

你可以直接用它列出的 URL 做手動驗收。

若你要完整的瀏覽器驗收順序，請再對照：

- [MANUAL_QA.md](/Users/lowhaijer/projects/beta-feedback-platform/MANUAL_QA.md)

## 6. 手動 smoke 驗證建議

script 成功後，至少確認以下頁面：

1. `Project detail`
2. `Campaign detail`
3. `Campaign safety section`
4. `Device profile detail`
5. `Task detail`
6. `Feedback detail`

推薦直接打開 script 輸出的 frontend URLs。

## 7. 重要限制

- backend 目前仍是 in-memory repository
- backend process restart 後，所有 seed data 都會消失
- 這是本地 demo workflow，不是正式 fixture system
- 這支 script 只調用現有 product API，不會直接碰 repository internals

## 8. 實作備註

- 對外顯示文案用 `Mobile Web`
- internal / API enum value 仍維持 `h5`
- 每次重跑 script 都會建立一組新的 demo graph
