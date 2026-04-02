# beta-feedback-platform Architecture Rules

## 1. Purpose

本文件定義 `beta-feedback-platform` 在 MVP 階段的專案結構規範，作為後續初始化與開發工作的共同依據。

本文件目前只定義「結構規則」，不代表這些目錄或模組都要在現在建立。實際建立時機應由對應 ticket 決定。

## 2. Governing Principles

- 專案方向必須對齊產品定位：真實測試、可執行回饋、安全與來源透明。
- MVP 第一階段只針對 Web / H5 / PWA、iOS、Android 所需的共通流程設計，不預先為第二階段平台建立結構。
- 優先遵守框架慣例（Nuxt 3 / FastAPI），只有在明確提高可維護性時才偏離預設做法。
- 先用清楚、可理解的結構支撐開發，再視實際重複與複雜度做抽象化。
- 不預先建立大量空白資料夾或假性完整模組。

## 3. Canonical Module Names

以下名稱是後續前後端命名的共同基準，避免同一個概念在不同地方出現不同名字。

| Product / PRD Term | Frontend Directory | Backend Module |
| --- | --- | --- |
| Account System | `accounts` | `accounts` |
| Project | `projects` | `projects` |
| Campaign | `campaigns` | `campaigns` |
| Tester Device Profile | `device-profiles` | `device_profiles` |
| Eligibility Filter | `eligibility` | `eligibility` |
| Task | `tasks` | `tasks` |
| Feedback | `feedback` | `feedback` |
| Reputation | `reputation` | `reputation` |
| Safety Layer | `safety` | `safety` |

若後續 ticket 要新增新的業務模組，必須先確認名稱是否與本表一致；若需要新名稱，應先更新本文件。

## 4. Repository-Level Rules

目前 repo 根目錄維持單一前端、單一後端與文件導向的簡單結構：

```text
beta-feedback-platform/
├── frontend/
├── backend/
├── tickets/
├── README.md
├── PRD.md
└── ARCHITECTURE.md
```

根目錄規則如下：

- `frontend/` 只放前端應用程式相關內容。
- `backend/` 只放後端服務相關內容。
- `tickets/` 只放工作 ticket，不放實作文件或臨時筆記。
- 根目錄文件只保留「專案級」文件，例如 `README.md`、`PRD.md`、`ARCHITECTURE.md`。
- 不在根目錄新增與 MVP 無關的應用程式、套件、腳本集合或平台專屬資料夾。
- 第二階段平台如 `steam/`、`desktop/`、`extension/` 不應在 MVP 階段先建立為根目錄資料夾。

## 5. Frontend Recommended Structure

以下為 `frontend/` 的建議結構。這是未來初始化與開發時的目標分層，不代表現在要建立全部內容。

```text
frontend/
├── app.vue
├── pages/
├── layouts/
├── components/
│   ├── base/
│   └── shared/
├── features/
│   ├── accounts/
│   ├── projects/
│   ├── campaigns/
│   ├── device-profiles/
│   ├── eligibility/
│   ├── tasks/
│   ├── feedback/
│   ├── reputation/
│   └── safety/
├── composables/
├── stores/
├── services/
│   └── api/
├── utils/
├── types/
├── constants/
├── assets/
├── public/
└── tests/
```

### Frontend Layer Rules

- `pages/`：只負責路由入口、頁面組裝與頁面層資料協調，不承載大量業務邏輯。
- `layouts/`：只放版型與跨頁面的視覺骨架。
- `components/base/`：無業務語意的基礎 UI 元件，例如按鈕、輸入框、卡片容器。
- `components/shared/`：跨多個 feature 重用，但仍偏展示層的元件。
- `features/<domain>/`：業務功能的主要落點。若某段 UI、composable、型別或 feature-specific service 只屬於單一業務模組，優先放在這裡。
- `composables/`：跨 feature 可重用的 Vue 組合式邏輯。若只被單一 feature 使用，應優先留在該 feature 內。
- `stores/`：Pinia store，只承接前端狀態、互動流程與快取協調，不直接混入畫面組件。
- `services/api/`：HTTP client 與 API 呼叫封裝，不放視圖邏輯。
- `utils/`：純函式工具，避免依賴 Vue runtime 或業務流程。
- `types/`：跨 feature 共用型別。只屬於單一 feature 的型別，應留在該 feature 內。
- `constants/`：跨 feature 共用常數。若是單一 feature 專屬常數，應留在該 feature 內。
- `tests/`：有實際測試時再建立，不為了結構完整感預先建立多層空資料夾。

### Frontend Placement Rules

- 頁面若只是在組裝 `campaigns` 流程，該頁面所依賴的業務元件與邏輯應優先放在 `features/campaigns/`。
- 不要在 `pages/` 內直接堆疊大量 API 呼叫、資料轉換與表單流程。
- 不要把業務元件放進 `components/shared/` 只是因為它看起來可重用；若有明確業務語意，應先留在 feature 內。
- 當同一段邏輯被至少兩個 feature 重用，且責任清楚時，才從 feature 抽到 `composables/`、`types/` 或 `components/shared/`。

## 6. Backend Recommended Structure

以下為 `backend/` 的建議結構。這是未來初始化與開發時的目標分層，不代表現在要建立全部內容。

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── deps.py
│   │   └── router.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── common/
│   │   ├── exceptions.py
│   │   └── responses.py
│   └── modules/
│       ├── health/
│       │   └── router.py
│       ├── accounts/
│       ├── projects/
│       ├── campaigns/
│       ├── device_profiles/
│       ├── eligibility/
│       ├── tasks/
│       ├── feedback/
│       ├── reputation/
│       └── safety/
└── tests/
```

單一業務模組的建議內部結構如下：

```text
modules/campaigns/
├── router.py
├── schemas.py
├── service.py
├── repository.py
└── models.py
```

### Backend Layer Rules

- `app/main.py`：FastAPI 啟動入口。
- `api/router.py`：集中註冊 router 與 API prefix，不承載業務流程。
- `api/deps.py`：集中放 FastAPI dependency 組裝。
- `core/`：全域設定、環境變數讀取、logging 等基礎能力。
- `db/`：資料庫連線、session 與 base 定義，不放業務查詢流程。
- `common/`：跨多模組共用的後端基礎程式碼；只有在至少兩個模組需要時才可新增內容。
- `modules/<domain>/router.py`：HTTP 層，負責 request / response 對接、參數驗證與呼叫 service。
- `modules/<domain>/schemas.py`：Pydantic schema 或 API contract。
- `modules/<domain>/service.py`：業務用例（use case）與流程協調。
- `modules/<domain>/repository.py`：資料存取邏輯，不承擔業務決策。
- `modules/<domain>/models.py`：資料持久化模型。
- `tests/`：有實際測試案例時再建立內容，不預先塞入空白測試模組。

### Backend Placement Rules

- `router.py` 不應直接寫 SQL 或 ORM 操作。
- `service.py` 不應依賴 FastAPI request object 才能運作。
- `repository.py` 不應處理 HTTP response 或權限文案。
- `models.py` 與 `schemas.py` 必須分開，不混用同一份檔案承擔資料庫模型與 API 契約。
- 模組與模組之間若需要互動，優先透過 service 層協調；避免直接跨模組呼叫對方 repository。

## 7. Naming Rules

### Repository and Docs

- 根目錄文件名稱使用固定大寫格式：`README.md`、`PRD.md`、`ARCHITECTURE.md`。
- ticket 檔名格式固定為 `T###-short-name.md`。

### Frontend

- 目錄名稱使用 `kebab-case`，例如 `device-profiles`。
- Vue 元件檔名使用 `PascalCase.vue`，例如 `CampaignCard.vue`。
- composable 檔名使用 `useXxx.ts`，例如 `useCampaignFilters.ts`。
- Pinia store 檔名使用 `useXxxStore.ts`，例如 `useCampaignStore.ts`。
- 一般 TypeScript 檔名預設使用 `kebab-case`。
- feature 名稱必須對齊本文件的 canonical module names。

### Backend

- Python 模組、檔名、資料夾名稱使用 `snake_case`。
- backend module 名稱必須對齊本文件的 canonical module names。
- API path 使用小寫與 `kebab-case` 風格，例如 `/device-profiles`。
- Python 類別名稱使用 `PascalCase`。
- 常數名稱使用 `UPPER_SNAKE_CASE`。

## 8. Shared Logic vs Business Logic

### Shared Logic

以下情況才應抽到全域共用層：

- 至少被兩個以上業務模組重用
- 責任穩定且命名明確
- 抽出後不會讓依賴方向變得更混亂

前端共用邏輯可放在：

- `components/shared/`
- `composables/`
- `services/api/`
- `types/`
- `constants/`
- `utils/`

後端共用邏輯可放在：

- `common/`
- `core/`
- `db/`

### Business Logic

以下情況應優先留在業務模組內，不要過早抽成共用：

- 只服務單一模組的流程
- 帶有明確業務語意，例如 `campaigns`、`feedback`、`reputation`
- 還在快速調整中的欄位、流程或驗證規則

規則如下：

- 前端業務邏輯優先放在 `features/<domain>/`
- 後端業務邏輯優先放在 `modules/<domain>/service.py`
- 單一模組專屬型別、常數、helper 優先與該模組共置
- 不可把 `shared` / `common` 當作未分類程式碼的暫存區

## 9. MVP Anti-Complexity Rules

MVP 階段必須避免以下做法：

- 不建立多前端應用或多後端服務
- 不拆成 monorepo packages、internal SDK 或共用 library repo
- 不預先建立第二階段平台專屬資料夾，例如 `steam`、`desktop`、`extension`
- 不引入 microservices、event bus、plugin system、workflow engine
- 不在前端預先建立大型 design system 或完整元件庫
- 不在後端預先建立過度抽象的 base service、base repository、generic CRUD framework
- 不為了未來可能性而先建立大量空白模組
- 不使用 `misc`、`helpers`、`temp`、`shared` 等籠統命名作為業務程式碼落點

簡化原則如下：

- 同一模式至少出現第二個明確使用點後，再考慮抽象化
- 若框架預設已足夠，優先使用預設慣例
- 若某層尚未出現真實需求，就先不要建立該層

## 10. Change Control

- 後續若有 ticket 要新增新的根目錄資料夾、跨模組共用層或新的命名規則，必須先更新本文件。
- `T002-frontend-init` 與 `T003-backend-init` 執行時，應以本文件為結構依據。
- 若實作上發現某條規則與框架慣例衝突，應優先選擇更簡單、可維護的一側，並回寫到本文件。
- 本文件是目前 MVP 階段的結構規範來源，直到有新 ticket 明確更新它為止。
