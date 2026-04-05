# Manual QA Checklist

## 1. 目的

這份文件提供目前 repo 可直接在瀏覽器執行的手動驗收清單。

重點是驗證：

- MVP 核心閉環是否可操作
- role-aware collaboration 是否可操作
- create / edit / review / resubmit flow 是否串得起來
- summary / empty / error state 是否正常

## 2. 前置條件

### 2.1 啟動 backend

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform/backend
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2.2 啟動 frontend

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform/frontend
npm run dev -- --host 127.0.0.1 --port 3000
```

### 2.3 準備 role-aware 測試資料

推薦先執行：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/seed_demo_data.py --label manual-qa
```

執行後請記下 script 輸出的：

- developer account ID
- tester account ID
- project ID
- campaign ID
- device profile ID
- task ID
- feedback ID

```
API detail URLs
- developer account detail: http://127.0.0.1:8000/api/v1/accounts/acct_d926ff98d7cc
- tester account detail: http://127.0.0.1:8000/api/v1/accounts/acct_3f4b1daa593c
- project detail: http://127.0.0.1:8000/api/v1/projects/proj_3e656e384223
- campaign detail: http://127.0.0.1:8000/api/v1/campaigns/camp_c2daf471f947
- safety detail: http://127.0.0.1:8000/api/v1/campaigns/camp_c2daf471f947/safety
- eligibility rule detail: http://127.0.0.1:8000/api/v1/eligibility-rules/er_ec32684e0fd6
- device profile detail: http://127.0.0.1:8000/api/v1/device-profiles/dp_7a9a133d8281
- task detail: http://127.0.0.1:8000/api/v1/tasks/task_fd5ccdfb0974
- feedback detail: http://127.0.0.1:8000/api/v1/feedback/fb_c93b0c044d88

Notes
- Use the homepage Current Actor selector to switch between the seeded developer and tester.
- The seeded project and campaign are owned by the developer actor.
- The seeded device profile and inbox task belong to the tester actor.
- Backend data is in-memory. Restarting the backend clears everything.
- The seeded feedback remains in review_status=submitted for manual T027 checks.
- Re-running this script creates a fresh demo graph with a new label.
```

詳細說明請看：

- [LOCAL_DEMO_SEED.md](/Users/lowhaijer/projects/beta-feedback-platform/LOCAL_DEMO_SEED.md)

### 2.4 測試時建議使用的 actor

請優先使用 seed 建立的：

- `Role-Aware Developer <label>`
- `Role-Aware Tester <label>`

並透過首頁的 `Current Actor` selector 切換。

## 3. 測試案例清單

### TC-01 首頁載入與主要導航

測試步驟
1. 開啟 `http://127.0.0.1:3000/`
2. 觀察首頁文案與主要入口
3. 點擊 `Accounts`、`Projects`、`Campaigns`、`Device Profiles`、`Tasks`

預期結果
- 首頁正常載入，沒有 runtime crash
- 首頁顯示繁體中文產品定位文案
- 可看見 `Current Actor` selector
- 主要入口都可正常進入對應列表頁

### TC-02 首頁 role-aware 切換

測試步驟
1. 開啟 `http://127.0.0.1:3000/`
2. 不選 actor，先觀察首頁
3. 選擇 seeded developer account
4. 再切換成 seeded tester account

預期結果
- 未選 actor 時，首頁顯示需先選擇 current actor 的提示
- 切到 developer 後，首頁顯示 developer summary cards
- developer 可看到 `Open my projects`、`Open review queue`、`Open campaigns`
- 切到 tester 後，首頁顯示 tester summary cards
- tester 可看到 `Open my tasks`、`Open my device profiles`、`Open accounts`

### TC-03 帳號列表、建立、詳情、編輯

測試步驟
1. 開啟 `http://127.0.0.1:3000/accounts`
2. 點 `Create account`
3. 建立一筆新的 developer 或 tester account
4. 成功後進入 detail 頁
5. 點 `Edit account` 修改資料並送出

預期結果
- 帳號列表可正常載入
- 建立表單可輸入並成功送出
- 建立成功後會導到 account detail
- detail 頁會顯示帳號基本資料
- 編輯成功後 detail 內容會更新

### TC-04 帳號詳情 collaboration summary

測試步驟
1. 打開 seeded developer account detail
2. 打開 seeded tester account detail
3. 再打開一筆沒有 owned resources 的新 tester account detail

預期結果
- developer account detail 會顯示：
  - 擁有專案數
  - 擁有活動數
  - 待審閱回饋數
  - 最近專案
  - 最近活動
- tester account detail 會顯示：
  - 擁有裝置數
  - 指派任務數
  - 已提交回饋數
  - 最近裝置
  - 最近任務
  - 最近回饋
- 若帳號沒有 collaboration footprint，會顯示 zero-state，而不是頁面崩潰

### TC-05 Developer 我的專案工作區

測試步驟
1. 把 current actor 切到 seeded developer
2. 開啟 `http://127.0.0.1:3000/my/projects`
3. 點進任一 project detail
4. 再把 current actor 切到 tester，重新開啟 `/my/projects`

預期結果
- developer 可看到自己的 owned projects
- 每張 card 可進 project detail
- 頁面可見 `Create project`、`My campaigns` 等入口
- tester 進 `/my/projects` 時會顯示 role mismatch

### TC-06 Developer 我的活動工作區

測試步驟
1. 把 current actor 切到 seeded developer
2. 開啟 `http://127.0.0.1:3000/my/campaigns`
3. 點進任一 campaign detail
4. 點回對應 project
5. 把 current actor 切到 tester，再開啟 `/my/campaigns`

預期結果
- developer 可看到自己擁有專案底下的 campaigns
- 可從 campaign card 進 detail
- 可由 card 回到上游 project
- tester 進 `/my/campaigns` 時會顯示 role mismatch

### TC-07 專案列表、建立、mine filter、詳情、編輯

測試步驟
1. 開啟 `http://127.0.0.1:3000/projects`
2. 把 current actor 切到 developer
3. 點 `Create project`
4. 建立一筆新 project
5. 回到列表頁，切 `Show mine only`
6. 點進 detail，再做 `Edit project`

預期結果
- 專案列表可正常載入
- developer 可成功建立 project
- 建立成功後會進入 detail
- detail 可看到 `owner_account_id`
- `Show mine only` 會只顯示屬於目前 developer 的 project
- 編輯成功後 detail 內容更新

### TC-08 活動建立、編輯與詳情

測試步驟
1. 從某個 project detail 點 `Create campaign`
2. 建立一筆 campaign
3. 進入 campaign detail
4. 點 `Edit campaign` 更新資料

預期結果
- 可從 project context 建立 campaign
- 建立成功後導到 campaign detail
- detail 可看到基本欄位與平台顯示
- 編輯成功後 detail 更新
- 平台顯示用語為 `網頁 / 行動網頁 / PWA / iOS / Android`

### TC-09 Campaign Safety 建立與編輯

測試步驟
1. 開啟某個 campaign detail
2. 若 safety 尚未建立，點 `Create safety profile`
3. 填寫 safety 表單並送出
4. 回到 campaign detail
5. 點 `Edit safety profile` 修改內容

預期結果
- safety empty state 可進入建立流程
- 建立成功後回到 campaign detail
- safety 區塊會顯示：
  - distribution channel
  - source label
  - source URL
  - risk level
  - review status
  - official channel only
  - risk note
- 編輯成功後頁面會反映更新內容

### TC-10 Eligibility Rule 建立、詳情、編輯

測試步驟
1. 在 campaign detail 的 eligibility 區塊點建立
2. 建立一筆 eligibility rule
3. 進入 rule detail
4. 再點編輯並更新內容

預期結果
- eligibility section 可正常載入
- rule 可成功建立
- 可從 campaign detail 進入 rule detail
- 編輯成功後 rule detail 內容更新

### TC-11 Device Profile 建立、mine filter、詳情、編輯

測試步驟
1. 把 current actor 切到 seeded tester
2. 開啟 `http://127.0.0.1:3000/device-profiles`
3. 點 `Create device profile`
4. 建立一筆新的 device profile
5. 回列表切 `Show mine only`
6. 進 detail 後點 `Edit device profile`

預期結果
- tester 可成功建立 device profile
- 建立成功後會進入 detail
- detail 可看到 `owner_account_id`
- `Show mine only` 會只顯示屬於目前 tester 的 device profile
- detail 頁會顯示 reputation summary
- 編輯成功後 detail 內容更新

### TC-12 Task 建立、詳情、編輯

測試步驟
1. 把 current actor 切到 developer
2. 從 campaign detail 點 `Create task`
3. 指派到某個 device profile
4. 送出後進入 task detail
5. 點 `Edit task` 調整狀態或指派內容

預期結果
- task 可成功建立
- 建立成功後導到 task detail
- detail 可看到 campaign / device profile 關聯
- 編輯成功後 detail 更新

### TC-13 Tester Inbox

測試步驟
1. 開啟 `http://127.0.0.1:3000/my/tasks`
2. 未選 actor 先觀察頁面
3. 切到 developer account
4. 切到 tester account
5. 切換不同狀態 filters
6. 若有 assigned task，執行 quick action

預期結果
- 未選 actor 時，頁面提示先選 tester
- developer 進入時顯示 role mismatch
- tester 進入時可看到屬於自己 owned device profiles 的 tasks
- 可切 `assigned / in_progress / submitted / closed`
- assigned task 的 quick action 可推進到 `in_progress`

### TC-14 Feedback 提交與編輯

測試步驟
1. 開啟某個 task detail
2. 點 `Submit feedback`
3. 填寫 feedback 表單並送出
4. 進 feedback detail
5. 點 `Edit feedback` 修改內容

預期結果
- task detail 中可看到 feedback section
- feedback 可成功提交
- 提交成功後導到 feedback detail
- detail 可看到結構化欄位
- 編輯成功後 detail 內容更新

### TC-15 Developer Review Queue

測試步驟
1. 開啟 `http://127.0.0.1:3000/review/feedback`
2. 未選 actor 先觀察頁面
3. 切到 tester account
4. 切到 developer account
5. 切換 `submitted / needs_more_info / reviewed`
6. 點進某筆 feedback detail

預期結果
- 未選 actor 時，頁面提示先選 developer
- tester 進入時顯示 role mismatch
- developer 進入時可看到自己擁有 campaigns 底下的 feedback
- review status filter 可正常工作
- 可從 queue 進入 feedback detail

### TC-16 Feedback Review

測試步驟
1. 打開 `/tasks/:taskId/feedback/:feedbackId`
2. 在 review panel 切換 `review_status`
3. 填寫 `developer_note`
4. 儲存

預期結果
- review panel 可見
- 可切換：
  - `已提交`
  - `需補充資訊`
  - `已審閱`
- 可儲存 `developer_note`
- 儲存成功後 detail 會顯示更新後的狀態與 note

### TC-17 Feedback 補件與重新提交

測試步驟
1. 先把某筆 feedback 標成 `needs_more_info`
2. 在 feedback detail 確認出現補件提示
3. 點 `Respond to supplement request` 或 `Resubmit feedback`
4. 用 tester 更新內容並送出

預期結果
- feedback detail 會出現 supplement request banner
- edit 頁會顯示 resubmission context
- tester 送出後：
  - `review_status` 會回到 `submitted`
  - `resubmitted_at` 會出現
  - `developer_note` 仍保留

### TC-18 Reputation Summary

測試步驟
1. 打開 `/device-profiles/:deviceProfileId`
2. 打開 `/campaigns/:campaignId`
3. 觀察 reputation 區塊

預期結果
- 兩個 detail 頁都可看見 reputation panel
- 若有 seed data，應看到非零 summary
- 若資料不足，應看到 zero-state，而不是白頁或 crash

### TC-19 Error State 抽查

測試步驟
1. 停掉 backend
2. 重新整理 `/accounts`、`/projects`、`/campaigns`、`/device-profiles`、`/tasks`
3. 再打開不存在的 detail route，例如：
   - `/accounts/acct_missing`
   - `/projects/proj_missing`
   - `/campaigns/camp_missing`
   - `/device-profiles/dp_missing`
   - `/tasks/task_missing`
   - `/tasks/task_missing/feedback/fb_missing`

預期結果
- backend 不可達時，列表或 detail 應顯示 error state
- 不存在的 resource 應顯示 not found / detail error state
- 頁面不應出現空白頁或未捕捉錯誤

## 4. 推薦驗收順序

若你想要快速驗完整條主流程，建議照這個順序：

1. 先跑 role-aware seed
2. 首頁與 current actor 切換
3. Accounts flow
4. Account collaboration summary
5. Developer workspace：`/my/projects`、`/my/campaigns`
6. Projects
7. Campaigns
8. Campaign Safety
9. Device Profiles
10. Eligibility Rules
11. Tasks
12. Tester Inbox
13. Feedback submit / edit
14. Developer Review Queue
15. Feedback resubmission
16. Reputation summary
17. Error state 抽查

## 5. 重要限制

- backend 目前是 in-memory repository
- backend restart 後，資料會全部消失
- current actor 目前只是最小 baseline，不是正式 auth
- role-aware seed 會建立 owned fixtures，但不會取代正式 fixture framework
- 若資料消失，請重新執行：
  - [scripts/seed_demo_data.py](/Users/lowhaijer/projects/beta-feedback-platform/scripts/seed_demo_data.py)

## 6. 補充說明

- 對外顯示用語使用 `Mobile Web`
- internal / API enum value 仍是 `h5`
- 這份文件以目前已完成功能為準
