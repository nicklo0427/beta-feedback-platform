# Title

T009 - Backend Testing Baseline

## Goal

為 `backend/` 建立可持續擴充的 pytest 測試基線，明確定義 backend 測試分層策略、fixture 規範、命名規則與測試資料清理方式，讓後續模組開發能在不導入正式資料庫整合測試的前提下，維持穩定的自動化驗證能力。

## Background

目前 backend 已具備以下基礎：

- FastAPI 專案初始化完成
- `/api/v1/health` health check 已存在
- `projects` / `campaigns` 最小 CRUD 已建立
- 已有 pytest 基礎與 API tests，例如：
  - health check test
  - projects API test
  - campaigns API test
- 目前資料層仍以 in-memory 為主，尚未接入正式 PostgreSQL

在這個階段，backend 已經開始有實際業務 API，因此需要把測試策略從「先有幾支 smoke test」提升為「可直接沿用的 baseline」。若沒有先定義測試分層與命名約定，後續很容易出現：

- 測試層級混雜，service / validation / API 責任不清
- fixture 命名與資料清理方式不一致
- in-memory state 汙染彼此測試
- 新模組開發時不知道應該補哪一層測試

本 ticket 主要是建立 backend 測試方法與結構規範，不是導入完整測試金字塔，也不是開始做正式資料庫整合測試。

前置條件：

- `T007-projects-and-campaigns-backend-crud` 已完成或至少已有可運作的 backend module 與 pytest 基礎

## Scope

- 定義 backend 測試分層策略，至少涵蓋：
  - schema / validation tests
  - service tests
  - API tests
- 明確說明每一層測試的責任邊界與推薦覆蓋內容
- 定義 pytest fixture 的放置原則與命名規則
- 定義 in-memory 測試資料的清理方式
- 定義測試檔案與測試函式命名規則
- 補足目前 `projects` / `campaigns` 模組在 service / validation 層的最低測試基線
- 保持測試架構簡潔，不導入過度複雜的 plugin 或多套框架組合

## Out of Scope

- 不導入正式 PostgreSQL integration test
- 不建立 migration 測試
- 不導入 end-to-end browser 測試
- 不擴張到 auth、RBAC、登入流程、通知、聊天、支付、推薦系統
- 不導入 coverage gate、mutation testing、load testing、contract testing
- 不建立複雜的 factory framework 或假資料平台

## Acceptance Criteria

- backend 測試分層已被明確定義，至少包含 validation、service、API 三層
- 已定義 fixture 放置位置、命名規則與資料清理方式
- 已定義 test file 與 test case 命名規則
- 現有 in-memory state 有一致的 reset / cleanup 策略，避免測試互相污染
- `projects` / `campaigns` 至少補上：
  - schema / validation baseline
  - service baseline
  - API baseline 維持可通過
- pytest 執行方式與最小本地驗證方式有明確說明
- 不需要正式資料庫即可在本地與 CI 類情境中執行核心 backend tests

## Deliverables

- 一份 backend 測試分層與命名規範
- 一組整理後的 pytest fixture baseline
- `projects` / `campaigns` 的 validation / service / API 最小測試覆蓋
- 一套可被後續 backend 模組直接沿用的測試慣例

## Notes / Constraints

- 必須遵守 `ARCHITECTURE.md` 的 backend 結構與命名原則
- 既有 API tests 不應被大幅重寫成複雜框架形式；應以整理與補強為主
- 推薦的測試分層如下：
  - validation test：驗證 Pydantic schema、enum、required / optional field、extra field 拒收
  - service test：驗證主要業務流程、關聯檢查、衝突處理與錯誤拋出
  - API test：驗證 route、status code、response shape、error response baseline
- fixture 原則：
  - 共用 fixture 優先放在 `backend/tests/conftest.py`
  - 單模組專屬 fixture 可放在對應 test file 內，避免過早抽成全域 fixture
  - in-memory repository reset 應使用 autouse fixture 或等效方式，確保每個 test case 彼此隔離
- 命名原則：
  - test file：`test_<domain>_<layer>.py` 或在簡單情況下維持 `test_<domain>_api.py`
  - test function：`test_<unit>_<behavior>_<expected_result>()`
- 測試資料原則：
  - 優先使用小型、明確、可讀的 inline data
  - 不建立大量通用 factory，除非至少有第二個模組重用需求
- 本 ticket 目標是建立穩定 baseline，不是把 backend 測試一次擴成完整 enterprise testing stack

