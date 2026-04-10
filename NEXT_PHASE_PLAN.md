# Next Phase Plan

## Status Note

目前 repo 已完成：

- `T011` 到 `T068`
- MVP 主流程閉環
- role-aware collaboration baseline
- qualification / assignment clarity baseline
- participation-to-assignment bridge baseline
- participation-aware demo seed 與 manual QA 文件
- public beta ops baseline
- public beta QA / launch checklist baseline

這代表：

- **功能型 MVP 已完成**
- **repo 內的 public beta readiness baseline 已完成**
- **下一步不再是補同一批基礎能力，而是進入 post-beta hardening 與運營期能力**

## 1. 現在先做哪一件事

如果你的目標是「這週就要對外開 beta」：

- 先執行 [PUBLIC_BETA_LAUNCH_CHECKLIST.md](/Users/lowhaijer/projects/beta-feedback-platform/PUBLIC_BETA_LAUNCH_CHECKLIST.md)
- 不要先開新功能票

如果你的目標是「在 beta 前後繼續把產品做穩」：

- 下一個 phase 建議直接切到：
  - `Post-Beta Hardening and Lifecycle`

## 2. 下一階段主題

下一階段建議聚焦：

- schema lifecycle hardening
- session-only environment hardening
- global actor-aware read visibility
- assignment 後的 task resolution 與 outcome
- audit trail / timeline
- 目標 beta 環境的 rollout evidence

## 3. 建議 Tickets

### T069 - Alembic Migration and Schema Lifecycle Baseline

- 把目前 `SQLAlchemy create_all` 的 persistence baseline 升級成 versioned migration baseline
- 導入 Alembic 與初始 migration
- 收斂 local / beta 的 schema upgrade 流程

### T070 - Session-Only Environment Mode and Header Fallback Decommission

- 把 `X-Actor-Id` fallback 正式隔離到 local QA / seed 環境
- 讓 beta / staging / production 預設走 session-only
- 收斂 auth / seed / docs 的環境切換策略

### T071 - Global Actor-Aware Read Visibility Hardening

- 把目前只做一部分的 read guard 擴到更多 summary / detail / queue
- 定義哪些資料是 public、哪些是 related-actor-only、哪些是 owner-only
- 補齊一致的 read-side error semantics

### T072 - Task Resolution and Outcome Workflow Baseline

- 在 assignment / feedback review 之後補 developer resolution workflow
- 讓 task 有明確 outcome、resolution note、resolved timestamp
- 讓 tester 也能看見任務的最終處理結果

### T073 - Audit Trail and Activity Timeline Baseline

- 為 participation request、task bridge、feedback review / resubmission、task resolution 補 activity events
- 在 detail 頁顯示最小 timeline / history
- 讓運營期與 beta support 有可追蹤上下文

### T074 - Beta Environment Rollout Verification and Evidence Pack

- 以目標 beta 環境為準，真正執行一次 rollout rehearsal
- 留下 health、smoke、manual QA、已知限制、go/no-go 結果
- 產出可交接的驗證證據包

## 4. 建議順序

1. `T069`
2. `T070`
3. `T071`
4. `T072`
5. `T073`
6. `T074`

## 5. 為什麼這樣排

- `T069` 先做，因為 persistence 已經進產品路徑，但 schema lifecycle 還沒正式版本化
- `T070` 接著做，因為 session-only 是 public beta / beta 後營運的真實模式
- `T071` 再把 read visibility 補完整，避免越做越多 feature、越難補讀取邊界
- `T072` 之後補 task resolution，讓 beta 期間的任務真正有收尾
- `T073` 再把 history 補上，支撐 support / review / dispute handling
- `T074` 最後在目標環境留下真正可驗證、可交接的 evidence

## 6. 這一輪先不要做的事

以下項目暫不建議在這一輪啟動：

- notification system
- 搜尋系統 overhaul
- auto matching
- developer candidate recommendation ranking
- organization / team model
- 完整 OAuth 套件
- RBAC framework 大擴張
- Steam / Desktop / Extension

## 7. 一句話結論

public beta readiness 這一輪已完成；接下來最合理的方向，是把資料生命周期、session-only 模式、read visibility、task resolution、audit trail 和真正的 beta rollout evidence 補齊。
