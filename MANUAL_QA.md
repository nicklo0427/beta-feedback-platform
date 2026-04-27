# Public Beta Manual QA Checklist

## 1. 目的

這份文件提供目前 repo 在 public beta 前可直接執行的手動驗收清單。

重點是驗證：

- session/auth 與 persistence baseline 是否可用
- MVP 核心閉環是否可操作
- role-aware collaboration 是否可操作
- create / edit / review / resubmit flow 是否串得起來
- summary / empty / error state 是否正常

## 2. 前置條件

### 2.1 建議先載入 `.env.local`

推薦先依 [/.env.example](/Users/lowhaijer/projects/beta-feedback-platform/.env.example) 建立 `.env.local`：

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

- 若你要跑 `session-only beta smoke`，請確認：
  - `BFP_DATABASE_URL` 已設定
  - `BFP_AUTH_MODE=session_only`
  - `NUXT_PUBLIC_AUTH_MODE=session_only`
- 若你要跑完整 seed fixture regression，建議改用本地 QA 環境，並允許：
  - `BFP_AUTH_MODE=session_with_header_fallback`
  - `NUXT_PUBLIC_AUTH_MODE=session_with_header_fallback`

### 2.2 啟動 backend

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
set -a
source ./.env.local
set +a
cd backend
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2.3 啟動 frontend

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
set -a
source ./.env.local
set +a
cd frontend
npm run dev -- --host 127.0.0.1 --port 3000
```

### 2.4 Public beta smoke 前置檢查

若你要先確認 public beta 環境最小 readiness，推薦先執行：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/public_beta_smoke.py --require-database-configured --require-session-only
```

如果這個 smoke 還沒過，就不建議直接進入完整手動驗收。

### 2.5 準備 role-aware 測試資料

推薦先執行：

```bash
cd /Users/lowhaijer/projects/beta-feedback-platform
./backend/.venv/bin/python scripts/seed_demo_data.py --label manual-qa
```

執行後請記下 script 輸出的：

- developer account ID
- tester account ID
- dual-role account ID
- project ID
- dual-role project ID
- qualified campaign ID
- drift campaign ID
- qualified device profile ID
- accepted-request device profile ID
- ineligible device profile ID
- dual-role device profile ID
- qualified task ID
- drift task ID
- accepted-request linked task ID
- feedback ID
- pending participation request ID
- accepted participation request ID

script 現在會同時提供兩條 qualification 驗證線：

- `Qualified campaign`
  - 會搭配一筆 iOS device profile pass
  - 也會搭配一筆 Android device profile fail
- `Drift campaign`
  - 會先建立一筆可成功指派的 task
  - 再更新 eligibility rule，讓 task detail 與 `/my/tasks` 可直接看到 drift warning

script 也會同時提供兩條 participation 驗證線：

- `Pending participation request`
  - 會出現在 tester 的 `/my/participation-requests`
  - 也會出現在 developer 的 `/review/participation-requests`
  - 可手動走 `accept -> create task from request` bridge flow
- `Accepted participation request`
  - 會出現在 tester 的 `/my/participation-requests`
  - 已經有對應 linked task
  - 可直接驗證已處理狀態、request detail 候選人快照、request-to-task traceability、與 actor-aware task detail read

詳細說明請看：

- [LOCAL_DEMO_SEED.md](/Users/lowhaijer/projects/beta-feedback-platform/LOCAL_DEMO_SEED.md)

### 2.6 T095-T101 dual-role 測試矩陣

若這次驗收目標是 dual-role account phase，請先依 [DUAL_ROLE_TEST_PLAN.md](/Users/lowhaijer/projects/beta-feedback-platform/DUAL_ROLE_TEST_PLAN.md) 跑完自動化測試與 smoke，再進入本文件的手動案例。

### 2.7 測試時建議使用的 actor

請優先使用 seed 建立的：

- `Role-Aware Developer <label>`
- `Role-Aware Tester <label>`
- `Role-Aware Dual <label>`

並透過 `/dashboard` 或其他 app 內頁 top bar 的 `Current Actor` selector 切換。

補充：

- developer-only account 應只看到開發者能力
- tester-only account 應只看到測試者能力
- dual-role account 應顯示 `開發者視角 / 測試者視角` 切換器
- active workspace role 只影響 frontend 呈現，不是 backend 授權來源；實際能力仍由 account `roles` 判斷

若你在 `session-only` beta 模式下驗收，請另外用：

- `/register`
- `/login`

建立一組 developer / tester 帳號做 auth 流程驗證。

## 3. 測試案例清單

### TC-00B Public shell、App shell 與主題切換

測試步驟
1. 開啟 `http://127.0.0.1:3000/`
2. 觀察 public header、品牌區、locale/theme controls 與 auth CTA
3. 點擊主題切換按鈕
4. 重新整理頁面
5. 登入後開啟 `http://127.0.0.1:3000/dashboard`
6. 觀察 app shell 的 side navigation、top bar 與 session/account 區塊
7. 依序點擊：
   - `Dashboard`
   - `我的專案`
   - `我的任務`
   - `回饋審查`
   - `帳號`

預期結果
- public shell 與 app shell 都能正常載入，沒有 layout 崩壞
- public shell 不顯示 app sidebar
- 登入後的 app shell 可見 side navigation，top bar 可見頁面標題、theme toggle、session/account 區塊
- light / dark 主題可切換，重新整理後仍保留最後選擇
- 導覽可在既有 route 間正常切換，不會改變 URL contract

### TC-00C Responsive mobile smoke

測試步驟
1. 將瀏覽器寬度調整到約 `390px`
2. 開啟首頁、`/login`、`/dashboard`、`/my/tasks`、`/projects`
3. 點開 mobile navigation drawer
4. 進入一個 detail 頁與一個 form 頁

預期結果
- public header 在手機寬度下仍可操作，auth CTA 不爆版
- mobile navigation 可正常開關
- 主要頁面不爆版、不出現不可操作的橫向溢出
- detail 頁 context 區會合理下移
- form 頁仍可完成主要輸入與送出流程

### TC-00 Public beta health 與 smoke

測試步驟
1. 打開 `http://127.0.0.1:8000/api/v1/health`
2. 觀察回傳內容
3. 執行：
   - `./backend/.venv/bin/python scripts/public_beta_smoke.py --require-database-configured --require-session-only`

預期結果
- health 回傳 `status = ok`
- `database_configured = true`
- `persistence_mode = database`
- `auth_mode = session_only`
- smoke script 成功通過

### TC-00A Login / Register / Logout

測試步驟
1. 打開 `http://127.0.0.1:3000/register`
2. 註冊一筆同時勾選開發者與測試者身份的帳號
3. 確認登入狀態已建立
4. 打開首頁與 account detail
5. 執行 logout
6. 再打開需要 session 的頁面

預期結果
- register 成功
- `/auth/me` 或頁面 session 狀態會保留 `developer / tester` 雙身份
- 已登入時，頁面可顯示 session account 狀態
- logout 成功後，受保護的 session flow 會要求重新登入或顯示 unauthenticated 對應提示
- session cookie 可驅動至少一筆 create flow

### TC-01 Public 首頁載入與 auth 入口

測試步驟
1. 開啟 `http://127.0.0.1:3000/`
2. 觀察首頁文案、品牌視覺與主要 CTA
3. 點擊 `登入工作區`、`建立帳號`、`了解如何運作`

預期結果
- 首頁正常載入，沒有 runtime crash
- 首頁顯示繁體中文 public landing 文案與品牌視覺
- 可看見 public header、locale/theme controls 與 auth CTA
- 看不到 app sidebar 或內部資源入口卡
- auth CTA 與頁內入口可正常導到對應流程

### TC-02 Dashboard role-aware / dual-role 工作區切換

測試步驟
1. 開啟 `http://127.0.0.1:3000/dashboard`
2. 不選 actor 或未登入時，先觀察頁面
3. 進入 app shell 後選擇 seeded developer account
4. 再切換成 seeded tester account
5. 再切換成 seeded dual-role account
6. 在 app shell 中切換 `開發者視角 / 測試者視角`
7. 重新整理頁面，確認最後選擇的視角仍保留

預期結果
- 未登入時，`/dashboard` 會要求登入或導向登入流程
- 進入 app shell 後，developer 會看到 developer dashboard summary / queues / CTA
- developer 可看到 `我的專案`、`我的活動`、審查相關入口
- 切到 tester 後，會看到 tester dashboard summary / queues / CTA
- tester 可看到 `我的任務`、`符合資格的活動`、`我的 participation requests`
- dual-role account 會看到工作視角切換器
- dual-role 切到開發者視角時，dashboard 顯示 developer summary / queues / CTA
- dual-role 切到測試者視角時，dashboard 顯示 tester summary / queues / CTA
- 重新整理後 active workspace role 仍保留
- 切換視角不會呼叫 mutation API，也不會修改 account `roles`

### TC-02A Login / Register 視覺與流程

測試步驟
1. 開啟 `http://127.0.0.1:3000/login`
2. 再開啟 `http://127.0.0.1:3000/register`
3. 觀察品牌區塊、表單結構與 helper text
4. 實際完成一輪 register / login / logout

預期結果
- login / register 會使用一致的品牌語言與 auth shell
- 表單分段清楚，沒有舊式獨立 landing page 的割裂感
- register / login 成功後都會進 `/dashboard`
- 已登入時再進 `/login` 或 `/register`，會被導回 `/dashboard`
- logout 後才會回到未登入的 public / auth 節奏

### TC-03 帳號列表、建立、詳情、編輯

測試步驟
1. 開啟 `http://127.0.0.1:3000/accounts`
2. 點 `Create account`
3. 建立一筆新的 dual-role account，勾選開發者與測試者身份
4. 成功後進入 detail 頁
5. 點 `Edit account` 修改資料，測試保留雙身份或改成單身份後送出

預期結果
- 帳號列表可正常載入
- 建立表單可輸入並成功送出
- 建立成功後會導到 account detail
- detail 頁會顯示帳號基本資料與身份集合
- 編輯成功後 detail 內容會更新
- 至少保留一種身份；若取消所有身份，表單應顯示 validation，不應送出

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

### TC-11 Campaign 資格檢查 panel（pass / fail）

測試步驟
1. 把 current actor 切到 seeded tester
2. 打開 seeded qualified campaign detail
3. 找到「目前測試者資格檢查」區塊

預期結果
- 同一個 campaign detail 內至少會看到 2 筆 qualification result
- iOS device profile 應顯示 `符合資格`
- Android device profile 應顯示 `不符合資格`
- fail 的結果應顯示原因摘要
- 若切回 developer actor，這個區塊應顯示 role mismatch 或對應提示

### TC-12 Tester 符合資格活動工作區

測試步驟
1. 把 current actor 切到 seeded tester
2. 開啟 `http://127.0.0.1:3000/my/eligible-campaigns`
3. 觀察 campaign cards
4. 點進 qualified campaign detail

預期結果
- tester 可看到符合資格的 campaigns
- 至少會看到 seeded qualified campaign
- card 會顯示命中的 device profile chips
- card 會顯示 qualification summary
- 若切回 developer actor，頁面應顯示 role mismatch

### TC-13 Tester 建立參與意圖

測試步驟
1. 把 current actor 切到 seeded tester
2. 打開 seeded qualified campaign detail，或打開 `/my/eligible-campaigns`
3. 找到 participation request 表單
4. 選擇一筆符合資格的 iOS device profile
5. 填寫備註並送出

預期結果
- tester 可成功建立 participation request
- 建立成功後會顯示成功訊息或回到對應頁面
- 若選擇不符合資格的 Android device profile，送出應被擋下
- 若同一個 `campaign / tester / device_profile` 已有 pending request，應看到 duplicate pending 錯誤

### TC-14 我的參與意圖工作區

測試步驟
1. 把 current actor 切到 seeded tester
2. 開啟 `http://127.0.0.1:3000/my/participation-requests`
3. 觀察 seeded pending 與 accepted requests
4. 若有 pending request，點撤回

預期結果
- tester 可看到自己的 participation requests
- 頁面至少有一筆 `pending` 和一筆 `accepted`
- accepted request 會顯示 developer decision note / decided_at
- pending request 可成功撤回，狀態更新為 `withdrawn`
- 若切到 developer actor，頁面顯示 role mismatch

### TC-15 Developer 參與意圖審查佇列

測試步驟
1. 把 current actor 切到 seeded developer
2. 開啟 `http://127.0.0.1:3000/review/participation-requests`
3. 觀察 pending requests
4. 對其中一筆送出 `accepted` 或 `declined`

預期結果
- developer 可看到自己擁有活動底下的 pending requests
- queue 頂部會顯示 participation funnel summary
- queue 中不應出現已經建立 linked task 的 accepted request
- developer 可成功 accept / decline pending request
- 若把 pending request accept，queue 會刷新，並可繼續從這筆 request 建立 task
- 若切到 tester actor，頁面顯示 role mismatch

### TC-16 Accepted request 橋接成 task

測試步驟
1. 把 current actor 切到 seeded developer
2. 開啟 `http://127.0.0.1:3000/review/participation-requests`
3. 對 seeded pending request 送出 `accepted`
4. 從 queue 或 detail 進入 `/review/participation-requests/:requestId/tasks/new`
5. 填寫 task 表單並送出

預期結果
- accepted request 會出現 `從 request 建立任務` 入口
- create-task 頁會鎖定 campaign / device profile 上下文
- 送出成功後會導到新建的 task detail
- request 之後會帶 `linked_task_id`
- request 之後會帶 `assignment_created_at`

### TC-17 參與意圖詳情與候選人快照

測試步驟
1. 把 current actor 切到 seeded developer
2. 從 `/review/participation-requests` 點進 seeded accepted participation request detail
3. 觀察 tester snapshot、device profile snapshot、qualification snapshot、campaign snapshot

預期結果
- 可正常進入 `/review/participation-requests/:requestId`
- detail 會顯示：
  - request 基本資訊
  - tester account 與 collaboration summary
  - device profile 與 reputation summary
  - qualification snapshot
  - campaign 與 campaign reputation
- 若該 request 已 linked 到 task，detail 會顯示 linked task 與 assignment created at
- 若 request 不屬於目前 developer 的 owned campaign，應顯示 error state

### TC-18 Request-to-task traceability 與 actor-aware read guard

測試步驟
1. 把 current actor 清空，直接打開 seeded accepted-request linked task detail
2. 觀察頁面狀態
3. 切到 seeded tester 或 seeded developer
4. 再次觀察 task detail 的 participation request context
5. 切到不相干的帳號，或手動建立另一個 tester 後再打開同一頁

預期結果
- 未選 actor 時，participation-linked task detail 會提示先選目前操作帳號
- 切到正確的 tester / developer 後，可正常讀取 task detail
- task detail 會顯示 participation request context：
  - request id
  - tester account
  - request status
  - assignment created at
- 不相干 actor 應看到 ownership mismatch / 對應 error state

### TC-19 Developer 候選人總覽與 participation funnel

測試步驟
1. 把 current actor 切到 seeded developer
2. 開啟 `http://127.0.0.1:3000/my/campaigns`
3. 觀察 qualified campaign card 上的 participation summary

預期結果
- campaign card 會顯示：
  - 待處理
  - 已接受待建任務
  - 已建立任務
- 至少會看得到 recent participation requests 摘要
- 可從 campaign card 進一步進到 review queue 或 detail

### TC-20 Device Profile 建立、mine filter、詳情、編輯

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
- detail 可看到 `install_channel`
- `Show mine only` 會只顯示屬於目前 tester 的 device profile
- detail 頁會顯示 reputation summary
- 編輯成功後 detail 內容更新

### TC-21 Task 建立、詳情、編輯

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

### TC-22 Task assignment preview 與 ineligible assignment guard

測試步驟
1. 把 current actor 切到 seeded developer
2. 打開 seeded qualified campaign 的 task create form
3. 先選擇 seeded qualified iOS device profile
4. 觀察 assignment qualification preview
5. 再改選 seeded ineligible Android device profile
6. 再觀察 assignment qualification preview 與送出按鈕

預期結果
- 選 iOS device profile 時，preview 顯示 `符合資格`
- preview 會顯示命中規則或 qualification summary
- 選 Android device profile 時，preview 顯示 `不符合資格`
- 預覽會顯示 fail reason summary
- 若規則要求 `install_channel = testflight`，使用 Android `play-store` fixture 也應維持不符合
- 表單送出按鈕應被阻擋，不能建立不符合資格的 task

### TC-23 Tester Inbox

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

### TC-24 Task 資格上下文與 drift warning

測試步驟
1. 打開 seeded qualified task detail
2. 觀察 qualification context 區塊
3. 再打開 seeded drift task detail
4. 回到 `/my/tasks`，切到 tester actor 並觀察 drift task card

預期結果
- qualified task detail 會顯示 qualification context
- context 至少包含：
  - 指派裝置設定檔
  - qualification status
  - matched rule 或對應 fallback
  - reason summary
- drift task detail 會顯示 drift warning
- `/my/tasks` 的 drift task card 也會顯示 `資格已漂移` 與對應提示

### TC-25 Feedback 提交與編輯

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

### TC-26 Developer Review Queue

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

### TC-27 Feedback Review

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

### TC-28 Feedback 補件與重新提交

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

### TC-29 Reputation Summary

測試步驟
1. 打開 `/device-profiles/:deviceProfileId`
2. 打開 `/campaigns/:campaignId`
3. 觀察 reputation 區塊

預期結果
- 兩個 detail 頁都可看見 reputation panel
- 若有 seed data，應看到非零 summary
- 若資料不足，應看到 zero-state，而不是白頁或 crash

### TC-30 Error State 抽查

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
2. app shell current actor 切換
3. Accounts flow
4. Account collaboration summary
5. Dual-role workspace role switch：`/dashboard` 開發者 / 測試者視角
6. Developer workspace：`/my/projects`、`/my/campaigns`
7. Projects
8. Campaigns
9. Campaign Safety
10. Device Profiles
11. Eligibility Rules
12. Campaign qualification panel
13. Tester eligible campaigns workspace
14. Tester participation request create
15. My participation requests
16. Developer participation review queue
17. Participation request detail snapshot
18. Task assignment preview / guard
19. Tasks
20. Tester Inbox
21. Task qualification drift
22. Feedback submit / edit
23. Developer Review Queue
24. Feedback resubmission
25. Reputation summary
26. Error state 抽查

## 5. 重要限制

- 若未設定 `BFP_DATABASE_URL`，backend 仍會 fallback 到 in-memory mode
- database schema lifecycle 以 Alembic migration 為 source of truth，deploy 前仍應明確執行 `alembic upgrade head`
- seed fixture 仍使用 current actor / `X-Actor-Id` baseline 建立 owned fixtures
- session-only public beta smoke 與 fallback-enabled 完整 fixture regression 是兩種不同驗收模式
- role-aware seed 會建立 owned fixtures，但不會取代正式 fixture framework
- qualification-aware seed 會額外建立 pass / fail / drift fixtures，但不會自動幫你送出 ineligible assignment；那一段需要在 UI 上手動驗證
- participation-aware seed 會額外建立 pending / accepted participation requests，方便直接驗收 tester workspace、developer review queue 與 detail snapshot
- dual-role seed 會額外建立一筆同時具備 developer / tester capability 的帳號，方便驗 active workspace role switch
- 若資料消失，請重新執行：
  - [scripts/seed_demo_data.py](/Users/lowhaijer/projects/beta-feedback-platform/scripts/seed_demo_data.py)

## 6. 補充說明

- 對外顯示用語使用 `Mobile Web`
- internal / API enum value 仍是 `h5`
- 這份文件以目前已完成功能為準
- public beta 發佈前的最後核對，請搭配：
  - [PUBLIC_BETA_LAUNCH_CHECKLIST.md](/Users/lowhaijer/projects/beta-feedback-platform/PUBLIC_BETA_LAUNCH_CHECKLIST.md)
