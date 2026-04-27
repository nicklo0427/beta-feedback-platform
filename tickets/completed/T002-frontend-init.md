# Title

T002 - Frontend Init

## Goal

初始化 `frontend/` 專案，建立以 Nuxt 3 + TypeScript 為基礎的前端開發骨架，並預留 Tailwind CSS 與 Pinia 的整合方向，但不進入任何業務頁面與業務功能開發。

## Background

本專案為跨平台 Beta 測試媒合與回饋管理平台。第一階段需支援 Web / Mobile Web / PWA、iOS、Android 對應的測試流程管理情境，因此前端需先建立可擴充、可維護、適合後續模組化開發的基礎架構。

目前 `frontend/` 目錄已存在，但尚未初始化任何框架。本 ticket 的目的是建立前端基礎骨架，而不是直接開始開發登入、專案管理、任務管理、回饋管理等業務頁面。

## Scope

- 在 `frontend/` 內初始化 Nuxt 3 專案
- 啟用 TypeScript 作為主要開發語言
- 建立適合後續擴充的基礎目錄結構
- 預留 Tailwind CSS 的整合方向
- 預留 Pinia 的整合方向
- 建立最小可運行的前端入口與基礎設定
- 確保初始化結果不綁定任何單一業務模組

## Out of Scope

- 不開發登入、註冊、Project、Campaign、Task、Feedback、Reputation 等業務頁面
- 不定義過細的設計系統與 UI 元件規格
- 不實作完整狀態管理邏輯
- 不接任何正式後端 API
- 不處理 SEO、成長追蹤、通知、聊天、支付等非初始化範圍內容

## Acceptance Criteria

- `frontend/` 已完成 Nuxt 3 + TypeScript 初始化
- 專案可作為後續功能開發基礎，具備清楚的基礎目錄分層
- 已預留 Tailwind CSS 整合位置或設定方向，但不必在此 ticket 完成完整樣式系統
- 已預留 Pinia 整合位置或設定方向，但不必在此 ticket 實作業務 store
- 初始化內容不包含任何特定業務頁面或業務流程邏輯
- 專案命名、目錄分層與檔案放置方式可與後續結構規範 ticket 對齊
- 初始化完成後，其他工程師或 AI agent 可以在此基礎上繼續開發

## Deliverables

- `frontend/` 內可正常啟動的 Nuxt 3 + TypeScript 專案骨架
- 一組清楚的前端基礎目錄分層
- Tailwind CSS 與 Pinia 的整合預留方案
- 一個最小可驗證的前端啟動結果，不包含業務功能

## Notes / Constraints

- 技術方向固定為 Nuxt 3 / Vue 3 / TypeScript / Tailwind CSS / Pinia
- 此 ticket 重點是初始化與基礎結構，不是功能頁面開發
- 不應為了方便而直接把後續業務模組全部先建立出來
- 命名與分層應偏向可維護與可擴充，而不是一次性快速堆疊
- 若需建立示範頁面，僅能作為最小啟動驗證用途，不應帶入產品功能假設
