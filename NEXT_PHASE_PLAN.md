# Next Phase Plan

## Status Note

目前 repo 已完成：

- `T011` 到 `T049`
- 前端繁體中文文案整理
- MVP 主流程閉環
- 第一輪產品化補強
- account / ownership / role-aware collaboration baseline
- account collaboration summary 與 owned resource panels
- qualification / assignment clarity baseline
- qualification-aware demo seed 與 manual QA 文件

這份文件現在的用途是：

- 寫明目前做到哪裡
- 寫明接下來最值得做什麼
- 作為下一輪 phase 規劃的起點，而不是停留在已完成的舊計畫

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
- developer workspace：`/my/projects`、`/my/campaigns`
- developer review queue：`/review/feedback`
- account collaboration summary：`/accounts/:accountId`
- role-aware homepage
- role-aware demo seed 與 manual QA 文件
- campaign detail qualification panel
- task assignment qualification preview / guardrails
- task qualification context / drift warning

換句話說，repo 已經從：

- 規劃 / shell 建設

走到：

- 可在 UI 中實際走完整主流程
- 可做最小 role-aware collaboration
- 可做最小 qualification visibility 與 assignment clarity

## 2. 現在最大的缺口

雖然 `eligibility rules`、campaign qualification panel、assignment preview、tester eligible campaigns workspace 與 task qualification context 都已存在，但這一輪做完之後，新的缺口也更明確了。

最明顯的缺口是：

- `install_channel` 仍沒有 device profile 對應欄位，qualification fidelity 還不完整
- tester 目前只能看到「自己符合哪些 campaign」，但還沒有最小參與 / 申請流程
- developer 仍缺少 candidate visibility，但又不適合直接跳進 auto matching
- qualification phase 已完成，接下來需要把 read-only clarity 逐步推向可操作 participation flow

所以接下來不應再擴新的核心 domain，而應該補：

- `Qualification Fidelity and Participation Workflow`

## 3. 下一階段總體方向

### 3.1 Phase Theme

下一個 phase 建議定義為：

- `Qualification Fidelity and Participation Workflow`

### 3.2 為什麼這樣排

目前 repo 已能表達：

- campaign eligibility rules
- qualification semantics baseline
- current tester qualification results
- qualified campaigns workspace
- tester owned device profiles
- developer task create / assignment with eligibility guard
- tester task inbox / feedback submit
- developer review queue / supplement request
- task qualification context / drift warning

但還缺：

- `install_channel` 等 qualification signal 的完整資料對齊
- tester 在看見 qualified campaign 之後，如何進一步表達參與意圖
- developer 如何在不引入 auto matching 的前提下看見更清楚的 candidate baseline
- qualification result 如何逐步演進成 participation / assignment 前的可操作資訊

如果不先補這一層，後續不論是：

- tester 參與流程
- developer candidate clarity
- 更可靠的 assignment confidence
- 後續更接近 production 的 access model

都會被卡在「只看得到結果，但還不能順著結果繼續操作」。

## 4. 建議優先順序

### P1

- device profile `install_channel` baseline
- qualification evaluator fidelity 補強
- 讓 campaign qualification / assignment guard 的資料來源更完整

判斷理由：

- 如果 `install_channel` 繼續缺席，qualification evaluator 對這類規則永遠只能回 fail，這會讓後續 qualification 與 participation 流程失真

### P2

- tester participation baseline
- developer candidate visibility baseline

判斷理由：

- qualification 結果現在已可見，下一步最合理的是讓 tester 與 developer 都能在這個結果上做出最小可操作行為
- 但仍應避免直接跳進 application marketplace 或 auto matching

### P3

- qualification phase 完成後的文件與 roadmap 收斂
- 下一輪 participation phase 的 tickets 拆分

判斷理由：

- 這一輪文件已同步完成，下一步應以新的 phase 為基準另開下一批票，而不是再沿用 `T044` 到 `T050` 的規劃描述

## 5. 建議 ticket 順序

`T044` 到 `T050` 已全部完成。

下一輪建議不要沿用這一段 ticket 編號繼續寫在這份文件裡，而是另開新的 phase plan，專門收斂：

1. qualification fidelity
2. tester participation workflow
3. developer candidate visibility
4. 文件與 QA 再同步

## 6. 依賴關係

qualification phase 的實際依賴關係已完成如下：

- `T044` 文件先行，定義 qualification semantics
- `T045` 依賴 `T044`，補 current tester qualification visibility
- `T046` 依賴 `T044` / `T045`，補 assignment preview 與 guard
- `T047` 依賴 `T044` / `T045`，補 tester eligible campaigns workspace
- `T048` 依賴 `T045` / `T046`，補 task detail 與 inbox qualification context
- `T049` 依賴 `T045` 到 `T048`，補 qualification-aware seed 與 QA
- `T050` 作為這一輪文件收斂票

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
- tester 申請制 marketplace
- developer candidate recommendation
- persistence / migration 重構
- Steam / Desktop / Extension
- 完整公開 reputation ranking

## 8. Qualification Phase 完成摘要

這一輪最重要的完成點是：

- tester 現在可以在 campaign detail 看見自己 owned device profiles 的 qualification pass / fail
- developer 指派 task 時現在會被 qualification preview 與 `assignment_not_eligible` guard 擋住
- tester 現在有 `/my/eligible-campaigns`
- task detail 與 `/my/tasks` 現在會顯示 qualification context 與 drift warning
- seed 與 manual QA 已能直接覆蓋 qualification / assignment 驗收

這代表本 repo 的 qualification phase 已從「文件與概念」落到「可操作、可驗證、可手測」。

## 9. 一句話結論

qualification / assignment clarity 這一輪已完成，下一輪最值得做的，不是再擴核心 domain，而是把目前已經可見的 qualification 結果，往更完整的 participation workflow 與 qualification fidelity 推進。
