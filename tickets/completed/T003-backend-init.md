# Title

T003 - Backend Init

## Goal

初始化 `backend/` 專案，建立以 FastAPI 為核心的後端開發骨架，並預留 PostgreSQL 整合方向，只處理初始化與基礎 API 結構，不進入任何業務模組開發。

## Background

本專案需要支援跨平台 Beta 測試媒合與回饋管理流程，後端將承載帳號、Project / Campaign、Task、Feedback、Reputation 與 Safety Layer 等核心模組。但在目前階段，優先目標是建立穩定、清楚、可持續擴充的後端基礎骨架。

目前 `backend/` 目錄已存在，但尚未初始化任何框架。本 ticket 應先完成後端入口、基礎 API 結構與設定分層，為後續業務模組開發留出清楚空間。

## Scope

- 在 `backend/` 內初始化 FastAPI 專案
- 建立基礎應用入口與路由結構
- 預留 PostgreSQL 整合方向
- 建立適合後續模組化開發的後端目錄分層
- 建立最小可運作的健康檢查或基礎 API 驗證方式
- 為後續帳號、Project、Task、Feedback 等模組保留延伸空間

## Out of Scope

- 不開發帳號、Project / Campaign、Task、Feedback、Reputation、Safety Layer 等業務模組
- 不實作完整資料庫 schema
- 不實作驗證、權限、背景工作、通知等進階功能
- 不接入外部服務
- 不處理部署、容器化、CI/CD 或正式營運環境配置

## Acceptance Criteria

- `backend/` 已完成 FastAPI 初始化
- 專案具備清楚的應用入口與基礎路由結構
- 已預留 PostgreSQL 整合方向，但不在本 ticket 完成完整資料模型
- 初始化內容僅包含基礎 API 骨架，不含任何特定業務模組邏輯
- 後端目錄結構可支援後續模組拆分與擴充
- 其他工程師或 AI agent 可在此基礎上繼續實作後續功能

## Deliverables

- `backend/` 內可啟動的 FastAPI 專案骨架
- 一組清楚的後端基礎目錄分層
- PostgreSQL 的整合預留方案
- 一個最小可驗證的 API 入口，不包含業務功能

## Notes / Constraints

- 技術方向固定為 FastAPI / PostgreSQL
- 本 ticket 的重點是建立基礎 API 結構，而不是先做資料模型細節
- 不應在初始化階段預先建立大量空白業務模組，避免造成假性完整
- 結構與命名應能對齊後續 `T004-project-structure-rules`
- 需保持後端骨架簡潔、可維護、易於後續擴充
