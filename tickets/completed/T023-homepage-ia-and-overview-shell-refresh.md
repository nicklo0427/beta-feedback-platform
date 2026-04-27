# T023 - Homepage IA and Overview Shell Refresh

## 1. 背景

目前專案已完成 MVP 主流程與多個 shell-level 頁面，但首頁與整體資訊架構（IA）仍停留在較早期的工程入口狀態。

當前問題包含：

- 首頁仍偏向初始化說明，沒有清楚表達產品定位與主要入口
- 使用者不容易一眼看出：
  - 這個產品在做什麼
  - 要從哪裡開始
  - `Projects / Campaigns / Device Profiles / Tasks / Feedback` 之間的關係
- 隨著 safety / reputation / form 能力逐步補上，首頁與 IA 若不整理，後續只會越來越零散

因此，本票的目標不是重做品牌網站，而是把首頁與 IA 更新成符合目前 MVP 狀態的產品入口。

## 2. 目標

整理首頁定位文案、主要導航與 overview shell，讓專案從「工程路由入口」升級為「可理解的產品入口」。

本票完成後，應具備以下結果：

- 首頁文案能明確對齊產品定位
- 主要入口與路由關係更清楚
- 可從首頁快速進入 MVP 核心模組
- overview shell 可作為未來 dashboard 的前身

## 3. 範圍

本票只做 MVP 最小集合，範圍如下：

- 重整首頁定位文案
- 整理首頁主要導航與入口卡片
- 補最小 overview shell
- 統一主要列表入口
- 補首頁與導航相關 Playwright 測試

本票可觸及的模組入口以目前已完成的 MVP 為限：

- Projects
- Campaigns
- Device Profiles
- Tasks
- Feedback
- 視情況帶入 Safety / Reputation 的入口或說明

## 4. 資料模型建議

本票不新增新資料模型。

若需要 overview summary，應先以靜態或既有頁面入口聚合為主，不新增新的 backend overview API。

## 5. API 路徑建議

本票原則上不新增 backend API。

若首頁 overview 需要摘要資料，應優先評估：

- 先使用現有頁面入口與靜態文案
- 或以最小前端組裝方式完成

不應在本票中為首頁引入新的 summary backend endpoint。

## 6. 前端頁面 / 路由建議

### 6.1 Target Pages

- `frontend/pages/index.vue`

### 6.2 IA Goals

首頁至少應清楚表達：

- 產品定位
- 非目標邊界
- 第一階段支援平台
- 核心流程入口
- 建議起點

### 6.3 UI Requirements

- 保留目前簡潔的 shell 風格
- 導航入口應清楚可掃描
- overview 區塊可包含：
  - 核心流程說明
  - 模組入口卡片
  - 安全與回饋原則說明
- 補穩定 selector，例如：
  - `data-testid="home-core-flow"`
  - `data-testid="home-primary-nav"`
  - `data-testid="home-overview-section"`

## 7. Acceptance Criteria

- 首頁文案已對齊目前產品定位與 MVP 階段
- 首頁已清楚顯示主要模組入口
- 使用者可從首頁快速導到核心列表頁
- 首頁已明確傳達：
  - 不是互刷平台
  - 不是評論交換平台
  - 不是灌量工具
- frontend typecheck / build 可通過
- Playwright 已補齊首頁與 IA 的最小 E2E 測試
- 本票未重做整站視覺語言或引入完整 design system

## 8. Out of Scope

- 不實作品牌官網
- 不實作 marketing site
- 不實作 auth-based dashboard
- 不實作 analytics overview backend
- 不重做整個 design system
- 不調整 backend schema

## 9. Backend Work Items

本票原則上不改 backend。

若首頁需要資訊，應優先使用現有 frontend 路由與靜態說明，不為此票新增 backend overview API。

## 10. Frontend Work Items

- 重整 `frontend/pages/index.vue`
- 視需要調整首頁導覽卡片與說明區塊
- 若出現跨頁重用樣式，再考慮補到 `assets/scss`
- 若只屬於首頁的局部排版調整，優先使用該頁 scoped style
- 補齊導航與 overview 的穩定 selector

## 11. Test Items

### 11.1 Frontend Tests

- typecheck
- build

### 11.2 E2E Tests

- 首頁可開啟
- 首頁主要入口可導到對應模組頁
- 首頁定位文案與非目標提示存在
- 若新增 overview 區塊，驗證其穩定 selector

### 11.3 Regression Focus

- 既有首頁 smoke test 不可被破壞
- 已存在的 projects / campaigns / tasks 等入口不可失效

## 12. Risk / Notes

- 本票不應演變成設計重做或品牌重塑專案
- 若為首頁新增樣式，必須先判斷：
  - 有跨頁共用價值的 layout / card / section pattern 才放 `assets/scss`
  - 只屬於首頁的局部微調應放 `index.vue` 的 scoped style
- IA 的重點是清楚，不是堆更多入口

## 13. 依賴關係（Dependencies）

主要依賴：

- `T017-campaign-safety-source-labeling-and-risk-flags`
- `T018-device-profile-create-and-edit-forms`
- `T019-eligibility-rule-create-and-edit-forms`
- `T020-task-create-and-edit-forms`
- `T021-feedback-submit-and-edit-forms`
- `T022-reputation-baseline-and-summary-metrics`

可獨立提前做的部分：

- 首頁定位文案整理

但最佳執行時機仍建議放在前述票之後，避免入口與 IA 重做。
