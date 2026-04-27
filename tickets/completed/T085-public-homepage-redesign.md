# T085 - Public Homepage Redesign

## 1. 背景

`T082` 已把首頁入口節奏往登入前 landing / 登入後 workspace 分離方向推進，`T083` 也已補上品牌視覺。但 `/` 仍需要進一步正式收斂成純 public landing，而不是仍殘留 app/dashboard 心智。

## 2. 目標

把 `/` 重做成真正的 public landing：

- 只承接產品介紹與品牌轉換
- 不再承接登入後 dashboard 心智
- 清楚引導使用者進入 `/login` 或 `/register`

## 3. 範圍

- 重做 `/` 的資訊架構與 section hierarchy
- 保留 T083 視覺資產並重新安置
- 移除首頁上的內部資源入口卡
- 保留產品介紹、角色價值、流程、信任訊號與 CTA

## 4. Public Homepage 建議

首頁至少應包含：

- hero
- value proposition
- developer / tester role value
- workflow preview
- trust / safety / beta collaboration messaging
- CTA section

首頁不應再直接暴露：

- `/projects`
- `/campaigns`
- `/device-profiles`
- `/tasks`
- `/accounts`

這些應留給登入後 app 或其他明確場景。

## 5. API / Route 建議

本票不新增 API。

route 維持：

- `/`

但它的定位改為固定 public landing。

## 6. 前端頁面 / 路由建議

主要修改：

- `frontend/pages/index.vue`

視需要調整：

- 首頁專用 visual / CTA component
- 共享 public layout styles

## 7. Acceptance Criteria

- `/` 看起來像 public product homepage，而不是 app 內頁
- 首頁保留品牌視覺、價值敘事與 auth CTA
- 首頁不再直接暴露 app 內部模組導航卡
- `zh-TW / en` 文案都成立
- light / dark 下視覺與 CTA 都合理

## 8. Out of Scope

- 不改登入 / 註冊 form
- 不新增 marketing 多頁站
- 不新增新的圖片資產 pipeline
- 不改 backend API

## 9. Backend Work Items

- 無新的 runtime 工作

## 10. Frontend Work Items

- 重排首頁 section hierarchy
- 調整 hero / visuals / CTA 比例
- 收斂首頁文案與 CTA 命名
- 移除首頁 app resource entry cards
- 補首頁 public regression

## 11. Test Items

- frontend `typecheck`
- frontend `build`
- public homepage smoke
- homepage i18n smoke
- homepage theme smoke
- 390px mobile homepage smoke

## 12. Risk / Notes

- 這張票要避免把首頁做成只剩漂亮視覺、卻失去清楚轉換
- 品牌視覺應服務產品定位，而不是再長成另一個 marketing system

## 13. 依賴關係（Dependencies）

- `T084`
- 建議在 `T083` 完成後實作
