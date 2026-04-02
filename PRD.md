# beta-feedback-platform PRD

## 1. Product Overview

`beta-feedback-platform` 是一個跨平台 Beta 測試媒合與回饋管理平台，目標是協助開發者在同一個系統中完成測試者招募、條件設定、任務派發、回饋收集與雙向信譽建立。

本產品不是互刷平台、不是評論交換平台、不是灌量工具。產品方向必須偏向真實測試、真實裝置條件與可執行回饋，而非以交換評論、衝下載量或操縱平台指標為目的。

目前產品方向已完成收斂，MVP 將先支援第一階段平台，並以標準化流程與安全原則作為產品設計前提。

## 2. Problem Statement

目前 Beta 測試常見問題如下：

- 招募來源分散：開發者需要透過社群、朋友、論壇或臨時表單分散招募測試者，效率低且難以追蹤。
- 流程零碎：不同平台有不同測試方式與分發限制，缺乏一致的管理入口。
- 回饋品質不一：測試回報內容格式鬆散，常缺少裝置資訊、重現步驟與版本資訊。
- 測試條件難控：開發者難以快速篩選符合平台、裝置、語系或使用經驗的測試者。
- 缺乏信譽機制：開發者無法評估測試者回饋品質，測試者也難以判斷專案方是否值得投入。
- 安全風險模糊：測試來源與安裝方式若缺乏標示，容易造成使用者對風險與責任界線不清。

這些問題導致 Beta 測試成本偏高、流程不可重複、結果難以量化，也降低開發者與測試者雙方持續參與的意願。

## 3. Product Goals

本產品的核心目標如下：

- 提供跨平台的 Beta 測試媒合流程，降低開發者招募與管理成本。
- 讓開發者可以用一致的方式定義測試條件、管理任務與收集回饋。
- 提升回饋可用性，讓回饋內容更結構化、可追蹤、可執行。
- 建立開發者與測試者雙向信譽機制，累積長期合作基礎。
- 以安全與來源透明為前提，降低不明安裝來源與不當操作風險。
- 長期發展為可擴充到更多平台的跨平台測試基礎設施（testing infrastructure）。

## 4. Non-Goals

現階段不包含以下目標：

- 互刷評論、互換評價、互衝下載或任何灌量導向功能。
- 將平台定位為應用商店評分交換或社群導流工具。
- 支援未經確認需求的廣泛第三方整合。
- 過早設計過多進階營運、商業化或成長玩法。
- 在 PRD 階段定義過細的 UI 版面與互動細節。
- 將產品建立為繞過平台規範的分發工具。

## 5. Target Users

本產品主要面向以下目標使用者：

- 獨立開發者（Indie Developers）：需要快速找到合適測試者並收集真實回饋。
- 小型產品團隊（Small Product Teams）：需要在有限資源下管理多平台測試流程。
- QA 或產品負責人：需要集中追蹤不同平台、不同任務與不同版本的回饋情況。
- 願意提供真實測試回饋的測試者（Testers）：希望依照自身裝置、興趣與可用時間參與測試任務。

## 6. User Roles

MVP 階段先定義兩種主要角色：

### 6.1 Developer

Developer 負責建立專案與測試活動，主要職責包括：

- 建立 Project / Campaign
- 定義測試條件與招募需求
- 派發任務與管理任務狀態
- 接收、整理與追蹤回饋
- 對 Tester 給予信譽評價

### 6.2 Tester

Tester 負責建立個人測試資料並參與任務，主要職責包括：

- 維護裝置與平台資料
- 申請或接受測試任務
- 依任務要求執行測試
- 提交結構化回饋
- 對 Developer 給予信譽評價

## 7. MVP Scope

MVP 範圍聚焦在建立跨平台 Beta 測試的最小可行閉環（minimum viable loop），包含：

- 建立 Developer / Tester 帳號基礎與角色區分
- 建立 Project / Campaign 的基本資料與招募流程
- 建立 Tester Device Profile，以支援條件篩選
- 提供 Eligibility Filter，讓開發者定義參與條件
- 提供 Task 系統以指派與追蹤測試任務
- 提供 Feedback 系統以收集結構化回饋
- 提供 Reputation 系統以建立雙向信譽基礎
- 提供 Safety Layer，標示來源、風險與審核狀態

MVP 目標不是涵蓋所有平台特殊需求，而是建立一套可持續擴充的共通流程骨架。

## 8. Supported Platforms

### 8.1 第一階段（MVP / Phase 1）

第一階段平台範圍如下：

- Web
- H5
- PWA
- iOS
- Android

第一階段重點是驗證跨平台流程是否成立，並確保在行動與瀏覽器情境下能用同一套產品邏輯管理測試任務與回饋。

### 8.2 第二階段（Phase 2）

第二階段預計擴充的平台如下：

- Steam
- Desktop
- Extension

第二階段是否啟動，取決於第一階段流程穩定度、平台需求明確度與安全機制可行性。

## 9. Core Modules

### 9.1 帳號系統（Account System）

- 支援 Developer / Tester 兩種主要角色
- 提供基本身分管理與角色切換邏輯基礎
- 為後續權限控管提供延伸空間

### 9.2 Project / Campaign

- Project 用於承載產品或測試主體
- Campaign 用於承載特定階段、版本或目標的測試活動
- 需能表示招募狀態、平台範圍與測試目的

### 9.3 Tester Device Profile

- 記錄 Tester 可用裝置與平台資訊
- 作為 Eligibility Filter 的基礎資料來源
- 支援跨平台測試媒合需要的裝置條件描述

### 9.4 招募條件（Eligibility Filter）

- 讓 Developer 定義哪些 Tester 可參與某項 Campaign 或 Task
- 條件應以平台、裝置、版本、區域、語言或經驗等共通欄位為優先
- 目標是提升媒合精準度，而非增加過度複雜的規則引擎

### 9.5 任務系統（Task）

- 定義測試者需要執行的任務內容
- 管理任務狀態、截止時間與提交要求
- 作為回饋與信譽的前置依據

### 9.6 回饋系統（Feedback）

- 收集結構化回饋內容
- 至少支援問題描述、重現步驟、裝置環境與結果狀態等核心資訊
- 讓 Developer 能追蹤、篩選與整理回饋

### 9.7 信譽系統（Reputation）

- 建立 Developer 與 Tester 雙向評價基礎
- 反映回饋品質、任務完成度與合作可靠性
- 目標是支持後續更穩定的媒合決策

### 9.8 安全與來源標示（Safety Layer）

- 標示測試來源、分發方式與基本風險
- 提供必要的提醒與審核流程入口
- 作為平台安全原則落地的核心模組

## 10. Core User Flows

### 10.1 Developer 發起測試流程

1. Developer 建立 Project
2. Developer 建立 Campaign
3. Developer 選擇平台並設定招募條件
4. Developer 建立 Task 與回饋要求
5. 系統依條件媒合或展示合適 Tester
6. Tester 參與任務後提交回饋
7. Developer 檢視回饋、更新處理狀態並給予評價

### 10.2 Tester 參與測試流程

1. Tester 建立帳號與 Device Profile
2. Tester 查看符合條件的 Campaign 或 Task
3. Tester 申請或接受任務
4. Tester 依需求完成測試
5. Tester 提交結構化回饋
6. Tester 接收結果狀態或後續要求
7. Tester 完成合作後給予 Developer 評價

### 10.3 回饋處理流程

1. Feedback 被提交
2. Developer 依條件檢視與篩選回饋
3. Developer 標記回饋狀態，例如待處理、需補充、已確認
4. 若資訊不足，系統支持要求補充
5. 回饋完成後可進入信譽累積或後續分析流程

## 11. Functional Requirements

以下需求為 MVP 階段的核心功能需求。

### 11.1 帳號與角色

- FR-001：系統應支援 Developer 與 Tester 兩種主要角色。
- FR-002：系統應能區分不同角色可執行的主要操作範圍。
- FR-003：系統應保留角色擴充空間，以支援後續管理或審核需求。

### 11.2 Project / Campaign 管理

- FR-004：Developer 應可建立與管理 Project。
- FR-005：Developer 應可在 Project 下建立一個或多個 Campaign。
- FR-006：Campaign 應可描述目標平台、測試目的、招募條件與基本狀態。

### 11.3 Tester Device Profile

- FR-007：Tester 應可建立與維護 Device Profile。
- FR-008：Device Profile 應至少支援平台、裝置類型與基本環境資訊。
- FR-009：系統應可將 Device Profile 作為媒合與過濾依據。

### 11.4 招募條件與媒合

- FR-010：Developer 應可設定 Campaign 或 Task 的 Eligibility Filter。
- FR-011：系統應能依條件篩選符合資格的 Tester。
- FR-012：系統應能清楚表示 Tester 是否符合或不符合參與條件。

### 11.5 任務系統

- FR-013：Developer 應可建立 Task 並指定基本測試要求。
- FR-014：Task 應可記錄狀態、截止資訊與提交條件。
- FR-015：Tester 應可查看自身可參與或已分配的 Task。
- FR-016：系統應能追蹤 Task 的執行與完成狀態。

### 11.6 回饋系統

- FR-017：Tester 應可提交結構化 Feedback。
- FR-018：Feedback 應至少包含問題描述、重現步驟、裝置資訊與結果說明等核心欄位。
- FR-019：Developer 應可檢視、篩選與更新 Feedback 狀態。
- FR-020：系統應支援要求 Tester 補充回饋資訊。

### 11.7 信譽系統

- FR-021：任務完成後，Developer 與 Tester 應可進行雙向評價。
- FR-022：系統應可累積基本信譽紀錄，作為後續媒合參考。
- FR-023：信譽資料應與任務或合作紀錄建立關聯。

### 11.8 安全與來源標示

- FR-024：系統應標示測試來源與分發方式。
- FR-025：系統應提供風險提示，協助使用者理解安裝或參與風險。
- FR-026：系統應具備基本審核機制，以降低不明來源或不適當內容進入平台。
- FR-027：系統應能對高風險來源或不符合原則的內容進行限制、下架或人工審查。

## 12. Non-Functional Requirements

- NFR-001：系統設計應支援多平台擴充，不應將流程綁死於單一平台。
- NFR-002：資料模型應能支援 Project、Campaign、Task、Feedback、Reputation 之間的清楚關聯。
- NFR-003：系統應優先採用結構化資料欄位，降低後續分析與管理成本。
- NFR-004：權限設計應具備可擴充性，以支持後續審核、客服或管理角色。
- NFR-005：關鍵資料異動應具備基本可追溯性（traceability）。
- NFR-006：產品文案與流程應盡量降低使用者對測試來源與風險的誤解。
- NFR-007：MVP 架構應以可維護與可拆分為原則，利於後續前後端分工與模組化開發。

## 13. Safety Principles

本產品的安全原則如下，屬於產品設計的硬限制：

- 優先採用各平台官方測試 / 分發機制。
- 不鼓勵來源不明安裝檔。
- 不鼓勵關閉裝置安全防護。
- 必須做來源標示、風險提示、審核機制。

進一步原則說明如下：

- 所有測試活動應明確標示分發來源與取得方式。
- 若平台有官方 Beta 或測試分發機制，產品設計應優先導向該機制。
- 對於可能要求使用者安裝非官方來源內容的流程，系統應明確提高風險提示與審核門檻。
- 不應以產品流程鼓勵使用者繞過平台安全限制、關閉系統保護、或安裝來源不明檔案。
- Safety Layer 應成為招募、任務與回饋流程中的基礎能力，而非事後補充。

## 14. Success Metrics

MVP 階段的成功指標以流程可用性與回饋品質為主，先不以流量或商業化指標為核心。

建議追蹤以下指標：

- Campaign 建立後成功招募到符合條件 Tester 的比例
- Tester 從加入任務到成功提交回饋的完成率
- Feedback 中符合結構化欄位要求的比例
- 需要補件的回饋比例
- Developer 對回饋可用性的主觀評分
- Tester 對任務清晰度與合作體驗的主觀評分
- 完成合作後產生雙向評價的比例
- 因安全審核被攔截、下架或標示風險的案件數

## 15. Milestones

### Milestone 0：方向收斂（已完成）

- 已完成產品定位收斂，不再定義為互刷 TestFlight 平台
- 已確認產品方向偏向真實測試與可執行回饋
- 已確認 MVP 第一階段平台為 Web / H5 / PWA、iOS、Android

### Milestone 1：PRD 與模組定義

- 完成 PRD 初版
- 確認 Core Modules 與 Core User Flows
- 將 MVP 拆解為可執行的 tickets

### Milestone 2：系統設計

- 定義前後端責任邊界
- 定義核心資料模型與關聯
- 定義安全審核與來源標示的最小流程

### Milestone 3：MVP 開發

- 依模組分階段實作帳號、Project / Campaign、Task、Feedback、Reputation、Safety Layer
- 建立第一階段平台支援所需的共用流程
- 完成最小可驗證的 end-to-end 測試閉環

### Milestone 4：MVP 驗證與下一階段評估

- 驗證第一階段平台流程是否可用
- 收斂流程瓶頸與資料缺口
- 評估第二階段平台（Steam / Desktop / Extension）擴充條件

## 16. Open Questions

以下問題仍需在後續設計與拆工前進一步確認：

- Campaign 與 Task 的責任邊界要如何定義，避免模型重疊？
- Eligibility Filter 在 MVP 階段要支援到哪一層條件複雜度？
- Feedback 的最小必填欄位應如何定義，才能兼顧可用性與填寫負擔？
- Reputation 的初版計分方式要採分數、標籤、文字評價，或其組合？
- Safety Layer 的審核流程哪些可自動化，哪些必須保留人工審查？
- 第一階段各平台在分發方式與回饋欄位上，哪些差異需要被抽象，哪些需要保留平台特性？
- 第二階段平台擴充時，現有資料模型是否足以承接 Steam / Desktop / Extension 的差異？
- 技術方向雖已初步確認為 Frontend：Nuxt 3 / Vue 3 / TypeScript / Tailwind CSS / Pinia，Backend：FastAPI + PostgreSQL，但實際專案初始化時的模組切分與部署策略仍待定義。
