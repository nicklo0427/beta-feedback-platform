# Title

T004 - Project Structure Rules

## Goal

定義 `beta-feedback-platform` 前後端的目錄分層、命名原則與後續 ticket 開發時必須遵守的基本結構規範，並將規範落成可直接遵守的文件，確保專案可維護、可擴充，且避免過早複雜化。

## Background

本專案目前正處於初始化與骨架建立階段。若沒有先定義基本結構規範，後續在前端與後端持續新增模組時，容易出現目錄命名不一致、責任邊界混亂、功能散落、共用邏輯無法收斂等問題。

由於專案第一階段需支援 Web / Mobile Web / PWA、iOS、Android 的共同測試流程，結構規劃必須優先考慮共通能力的抽象與可擴充性；同時也不能在尚未確認需求前導入過多分層或過度工程化設計。

目前 `README.md`、`PRD.md` 與 `T001-project-bootstrap.md` 已確認以下前提：

- 產品定位是跨平台 Beta 測試媒合與回饋管理平台
- 產品方向偏向真實測試與可執行回饋，而不是互刷、灌量或交換評論
- 目前處於初始化前階段，尚未開始前後端框架實作
- 初始化的重點是建立可持續開發的骨架，而不是直接堆疊商業功能

## Scope

- 定義 repo 根目錄的結構邊界
- 定義 `frontend/` 的建議目錄分層與各層責任
- 定義 `backend/` 的建議目錄分層與各層責任
- 定義前後端共通的命名規則
- 定義 PRD 核心模組對應的目錄命名基準
- 定義共用邏輯與業務邏輯的分離原則
- 定義 MVP 階段避免過早複雜化的約束
- 將以上規範落成根目錄文件 `ARCHITECTURE.md`
- 在本 ticket 中引用 `ARCHITECTURE.md` 作為後續執行依據

## Out of Scope

- 不設計具體 UI 版面或視覺規範
- 不定義特定業務模組的完整資料模型
- 不引入過細的 DDD、微服務、事件驅動等進階架構規範
- 不限制未來必要的重構空間
- 不處理部署、基礎設施或營運流程規範
- 不初始化 `frontend/` 或 `backend/`
- 不建立實際業務模組資料夾
- 不修改 `README.md` 或 `PRD.md`

## Acceptance Criteria

- 根目錄存在 `ARCHITECTURE.md`
- `ARCHITECTURE.md` 已定義 repo 級規則、frontend 結構、backend 結構、命名規則、模組命名基準、共用邏輯分離原則與 MVP 限制
- `ARCHITECTURE.md` 已清楚說明哪些結構是「建議目標」，哪些內容不應在現階段預先建立
- 本 ticket 已明確指出 `ARCHITECTURE.md` 是後續 `T002-frontend-init` 與 `T003-backend-init` 的結構依據
- 規範內容足以讓後續工程師或 AI agent 依同一標準建立新模組，而不需自行猜測目錄與命名方式
- 本次修改未初始化 `frontend/` 或 `backend/`
- 本次修改未建立 `ARCHITECTURE.md` 以外的其他新檔案

## Deliverables

- 更新後的 `tickets/T004-project-structure-rules.md`
- 一份根目錄結構規範文件：`ARCHITECTURE.md`
- 一套前端結構規範
- 一套後端結構規範
- 一套命名與分層原則
- 一組後續 ticket 可直接遵守的最低結構要求

## Notes / Constraints

- 結構規範應以可維護、可擴充、低耦合為優先
- 規範必須足夠清楚，但不能過度設計
- MVP 階段應優先採用簡單、可理解、可演進的結構
- 若某項分層暫時沒有明確用途，不應為了完整感而預先建立
- 規範需支援後續核心模組，例如帳號、Project / Campaign、Tester Device Profile、Eligibility Filter、Task、Feedback、Reputation、Safety Layer 的逐步加入
- 所有後續 ticket 在新增結構前，都應先檢查是否符合本規範，避免重複與命名漂移
- 若後續需要新增新的根目錄資料夾、跨模組共用層或新的命名規則，應先更新 `ARCHITECTURE.md`
- 本 ticket 只負責定義規範，不負責實際初始化框架與建立對應目錄
