# Manual QA Checklist

## 1. 目的

這份文件提供目前 repo 的高價值手動驗收清單。

重點是讓你可以直接在瀏覽器中驗證：

- MVP 核心閉環是否可操作
- create / edit / review flow 是否串得起來
- shell-level 狀態是否正常

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

### 2.3 準備 demo data

推薦先跑 seed：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/seed_demo_data.py --label manual-qa
```

詳細說明請看：

- [LOCAL_DEMO_SEED.md](/Users/lowhaijer/projects/beta-feedback-platform/LOCAL_DEMO_SEED.md)

## 3. 可以在網頁測試的清單

### 3.1 首頁與導航

打開：

- `http://127.0.0.1:3000/`

確認：

- 首頁可正常載入
- 產品定位文案正確
- 可點進：
  - `/projects`
  - `/campaigns`
  - `/device-profiles`
  - `/tasks`

### 3.2 Project Flow

打開：

- `http://127.0.0.1:3000/projects`

確認：

- list 可載入
- 可點 `Create project`
- create 成功後可進入 detail
- detail 可點 `Edit project`
- edit 成功後 detail 內容會更新

### 3.3 Campaign Flow

從 `Project detail` 進入：

- `/projects/:projectId`

確認：

- 可點 `Create campaign`
- create form 可送出
- create 成功後導到 `Campaign detail`
- `Campaign detail` 可點 `Edit campaign`
- edit 成功後 detail 更新

### 3.4 Campaign Safety Flow

打開：

- `/campaigns/:campaignId`

確認：

- safety empty state 時可點 `Create safety profile`
- create 成功後回到 campaign detail
- safety panel 會顯示：
  - distribution channel
  - source label
  - source URL
  - risk level
  - review status
  - official channel only
  - risk note
- safety panel 可點 `Edit safety profile`
- edit 成功後會反映更新內容

### 3.5 Device Profile Flow

打開：

- `http://127.0.0.1:3000/device-profiles`

確認：

- list 可載入
- 可點 `Create device profile`
- create 成功後可進入 detail
- detail 可點 `Edit device profile`
- edit 成功後 detail 內容更新
- detail 頁可看到 reputation summary

### 3.6 Eligibility Rule Flow

打開：

- `/campaigns/:campaignId`

確認：

- eligibility section 可見
- 可建立 eligibility rule
- 可從 campaign detail 進入 rule detail
- 可從 rule detail 進入 edit
- edit 成功後 detail 更新

### 3.7 Task Flow

從 `Campaign detail` 進入：

- `/campaigns/:campaignId`

確認：

- 可點 `Create task`
- create 成功後導到 task detail
- task detail 可點 `Edit task`
- 可調整 status 與 device profile assignment
- edit 成功後 detail 更新

### 3.8 Feedback Submit / Edit Flow

打開：

- `/tasks/:taskId`

確認：

- feedback section 可見
- 可點 `Submit feedback`
- create 成功後導到 feedback detail
- feedback detail 可點 `Edit feedback`
- edit 成功後 detail 更新

### 3.9 Feedback Review Flow

打開：

- `/tasks/:taskId/feedback/:feedbackId`

確認：

- review panel 可見
- 可切換 review status：
  - `submitted`
  - `needs_more_info`
  - `reviewed`
- 可填寫 `developer note`
- save 後 detail 頁會顯示更新後的：
  - review status
  - developer note

### 3.10 Reputation Summary

打開：

- `/device-profiles/:deviceProfileId`
- `/campaigns/:campaignId`

確認：

- reputation panel 可見
- 若有 seed data，應看到非零 summary
- 若資料不足，應看到 zero state，而不是頁面崩潰

## 4. 推薦驗收順序

若你要快速驗證整條主流程，建議順序如下：

1. 首頁
2. Project create / edit
3. Campaign create / edit
4. Campaign safety create / edit
5. Device profile create / edit
6. Eligibility rule create / edit
7. Task create / edit
8. Feedback submit / edit
9. Feedback review
10. Reputation summary

## 5. Error / Empty State 檢查

除了 happy path，也建議檢查以下狀態：

- backend 未啟動時，頁面應顯示 error state
- 某些關聯資料尚未建立時，應顯示 empty state
- 不存在的 detail route 應顯示 error state

可抽查：

- `/projects`
- `/campaigns`
- `/device-profiles`
- `/tasks`
- `/campaigns/:campaignId`
- `/tasks/:taskId/feedback/:feedbackId`

## 6. 重要限制

- backend 目前是 in-memory repository
- backend restart 後，資料會全部消失
- 這不是 bug，是目前 MVP 階段的刻意限制
- 若資料消失，請重新執行：
  - [seed_demo_data.py](/Users/lowhaijer/projects/beta-feedback-platform/scripts/seed_demo_data.py)

## 7. 補充說明

- 對外顯示用語使用 `Mobile Web`
- internal / API enum value 仍是 `h5`
- 這份文件以目前已完成的功能為準，不包含未完成的後續票
