# Next Phase Plan

## Status Note

目前 repo 已完成：

- `T011` 到 `T057`
- 前端繁體中文文案整理
- MVP 主流程閉環
- 第一輪產品化補強
- account / ownership / role-aware collaboration baseline
- qualification / assignment clarity baseline
- participation intent baseline
- participation-aware demo seed 與 manual QA 文件

這份文件現在的用途是：

- 寫明目前做到哪裡
- 寫明下一輪最值得補的是什麼
- 作為 `T058` 之後的新 phase 規劃基線

## 1. 目前做到哪裡

目前系統已具備：

- `Project -> Campaign -> Device Profile -> Eligibility -> Task -> Feedback`
- `Campaign Safety`
- `Reputation Summary`
- `Account CRUD`
- `Current Actor Selector`
- `Project / Device Profile` ownership baseline
- tester inbox：`/my/tasks`
- tester eligible campaigns workspace：`/my/eligible-campaigns`
- tester participation requests workspace：`/my/participation-requests`
- developer workspace：`/my/projects`、`/my/campaigns`
- developer review queue：`/review/feedback`
- developer participation review queue：`/review/participation-requests`
- participation request detail：`/review/participation-requests/:requestId`
- account collaboration summary：`/accounts/:accountId`
- role-aware homepage
- campaign detail qualification panel
- task assignment qualification preview / guardrails
- task qualification context / drift warning
- participation-aware demo seed 與 manual QA 文件

換句話說，repo 已經從：

- 規劃 / shell 建設

走到：

- 可在 UI 中實際走完整主流程
- 可做最小 role-aware collaboration
- 可做 qualification visibility 與 assignment clarity
- 可做最小 tester participation request 與 developer review flow

## 2. 現在最大的缺口

participation phase 完成後，最大的缺口已經不是「看不見資格結果」或「無法送出 participation request」，而是：

- participation request 和實際 task assignment 之間還沒有銜接 baseline
- developer 雖然能審查 request，但還沒有跨 request 的 candidate visibility / decision support
- tester request 被接受之後，還沒有清楚的後續行動路徑
- current actor 已可支撐 MVP，但 access / auth 還沒有更進一步的 hardening

所以接下來不應再擴新的核心 domain，而應該補：

- `Participation-to-Assignment Bridge and Candidate Visibility`

## 3. 下一階段總體方向

### 3.1 Phase Theme

下一個 phase 建議定義為：

- `Participation-to-Assignment Bridge and Candidate Visibility`

### 3.2 為什麼這樣排

目前 repo 已能表達：

- campaign eligibility rules
- qualification semantics baseline
- current tester qualification results
- qualified campaigns workspace
- developer assignment preview / guard
- task qualification context / drift warning
- tester participation request create / withdraw
- developer participation review queue / accept / decline
- participation request candidate snapshot detail

但還缺：

- accepted participation request 如何安全轉成 assignment
- developer 如何在 queue 之外看見更完整的 candidate / request overview
- tester 在 request 被 accepted 後，如何理解下一步與對應 task
- 現有 current actor baseline 如何逐步演進成更可靠的 access control

如果不先補這一層，後續不論是：

- participation approval-to-assignment bridge
- developer candidate visibility
- 更可靠的 assignment confidence
- 更接近 production 的 access model

都會被卡在「request 已被接受，但還沒有真正進入 task 執行」。

## 4. 建議優先順序

### P1

- participation accepted -> task assignment bridge
- accepted request 與 task / campaign / device profile 的最小關聯表達
- request decision 後的下一步可操作入口

判斷理由：

- 現在 request 已能送出與審查，但沒有橋接到實際 assignment，會讓 flow 停在半路

### P2

- developer candidate visibility
- request / candidate aggregate views
- request detail 與 assignment 結果的上下文補強

判斷理由：

- 當 request 可以往 assignment 前進後，開發者才需要更清楚的 overview 來做決策

### P3

- access / auth hardening draft
- seed / QA / README / roadmap 收斂

判斷理由：

- access hardening 仍應延後於 flow bridge，但比起再開新 domain 更值得做

## 5. Participation Phase 已完成票

目前已完成：

- `T051` Device Profile Install Channel Baseline and Form Support
- `T052` Qualification Evaluator Install Channel Fidelity
- `T053` Participation Intent Semantics Draft
- `T054` Tester Campaign Participation Request Flow
- `T055` Developer Participation Review Queue and Decision Actions
- `T056` Participation Request Detail and Candidate Snapshot Panels
- `T057` Participation-Aware Demo Seed and Docs Refresh

## 6. 下一輪建議主題

下一輪建議先規劃：

- participation accepted -> task assignment bridge
- request-to-task traceability
- developer candidate overview panels
- access / auth hardening draft

## 7. 這一階段先不要做的事

以下項目暫不建議在這一批 ticket 中啟動：

- 正式 auth / password / session / OAuth
- RBAC framework
- organization / team model
- notification system
- 即時聊天或 threaded messaging
- 搜尋系統
- 複雜 matching engine
- auto matching
- developer candidate recommendation ranking
- tester 申請制 marketplace 大擴張
- persistence / migration 重構
- Steam / Desktop / Extension
- 完整公開 reputation ranking

## 8. 下一輪最推薦先做哪一張

最推薦先做：

- `T058 - Participation Accepted to Task Assignment Bridge`

原因：

- 這是目前 participation flow 最大、最真實的缺口
- 做完後 workflow 才不會停在「request 已被接受，但還沒有真正進入 task 執行」
- 也能讓 developer review queue 與 tester workspaces 形成更完整閉環

## 9. 一句話結論

qualification / assignment / participation 這一輪已完成，下一輪最值得做的，是把 accepted participation request 安全地橋接到 task assignment，並補上 developer candidate visibility。
