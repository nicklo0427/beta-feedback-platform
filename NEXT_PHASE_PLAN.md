# Next Phase Plan

## Status Note

目前 repo 已完成：

- `T011` 到 `T042`
- 前端繁體中文文案整理
- MVP 主流程閉環
- 第一輪產品化補強
- account / ownership / role-aware collaboration baseline

這份文件現在的用途是：

- 寫明目前做到哪裡
- 寫明接下來最值得做什麼
- 列出 `T038` 之後可直接交給 Codex 逐張實作的 tickets

## 1. 目前做到哪裡

目前系統已具備：

- `Project -> Campaign -> Device Profile -> Eligibility -> Task -> Feedback`
- `Campaign Safety`
- `Reputation Summary`
- `Account CRUD`
- `Current Actor Selector`
- `Project / Device Profile` ownership baseline
- tester inbox：`/my/tasks`
- developer workspace：`/my/projects`、`/my/campaigns`
- developer review queue：`/review/feedback`
- role-aware homepage
- role-aware demo seed 與 manual QA 文件

換句話說，repo 已經從：

- 規劃 / shell 建設

走到：

- 可在 UI 中實際走完整主流程
- 可做最小 role-aware collaboration

## 2. 現在最大的缺口

雖然 current actor 與 ownership baseline 已存在，但它目前還沒有完整貫穿到所有 workflow。

最明顯的缺口是：

- account detail 還沒有真正反映 collaboration footprint

所以接下來不應再擴新的核心 domain，而應該補：

- `Account Collaboration Summary`

## 3. 下一階段總體方向

### 3.1 Phase Theme

下一個 phase 建議定義為：

- `Account Collaboration Summary`

### 3.2 為什麼這樣排

目前 repo 已能表達：

- 誰是 developer
- 誰是 tester
- 基本 ownership anchor
- role-aware inbox / review queue / homepage

但還缺：

- account detail 如何呈現 collaboration footprint
- account detail 如何承接 owned resource panels 與 summary

如果不先補這一層，後續不論是：

- 更完整的 collaboration summary
- 更可靠的 reputation
- 更接近 production 的 access model

都會建立在不穩定的權限基礎上。

## 4. 建議優先順序

### P1

- `T043` Account collaboration summary and owned resource panels

判斷理由：

- 當 ownership、workspace 與 role-aware seed 都到位後，account detail 才值得進一步承接 collaboration summary

## 5. 建議 ticket 順序

1. `T038-actor-aware-workflow-guardrails-draft`
2. `T039-actor-aware-campaign-safety-and-eligibility-mutation-guards`
3. `T040-actor-aware-task-and-feedback-action-guards`
4. `T041-developer-workspace-mine-views-and-owned-resource-navigation`
5. `T042-role-aware-demo-seed-and-owned-fixtures`
6. `T043-account-collaboration-summary-and-owned-resource-panels`

## 6. 依賴關係

- `T038` 是文件先行票
- `T039` 依賴 `T038`
- `T040` 依賴 `T038`
- `T041` 建議在 `T039` 後做
- `T042` 建議在 `T039` 與 `T040` 後做
- `T043` 建議在 `T041` 後做，並受益於 `T042`

## 7. 這一階段先不要做的事

以下項目暫不建議在這一批 ticket 中啟動：

- 正式 auth / password / session / OAuth
- RBAC framework
- organization / team model
- notification system
- 即時聊天或 threaded messaging
- 搜尋系統
- 複雜 matching engine
- persistence / migration 重構
- Steam / Desktop / Extension
- 完整公開 reputation ranking

## 8. 最推薦先做哪一張

目前這一輪最推薦先做：

- `T043-account-collaboration-summary-and-owned-resource-panels`

原因：

- 目前 actor-aware mutation guards、workspace 與 role-aware seed 都已完成
- 下一個最有價值的缺口，就是把 account detail 提升成真正可反映 collaboration footprint 的入口

## 9. 一句話結論

下一輪最重要的，不是再做新模組，而是把目前已經做出來的 role-aware collaboration baseline，進一步收斂成可閱讀、可追蹤的 account collaboration summary。
