# T093 - Public Copy Simplification for Non-Technical Users

## 1. 背景

`T092` 已把 public landing 的資訊架構、視覺與 CTA 節奏收斂成更像正式產品首頁的形狀，但目前首頁與 auth pages 的文字仍偏工程、QA、系統流程導向。

如果目標受眾包含：

- 沒有開發背景的人
- 主要靠直覺、vibe、實際使用情境來理解產品的人
- 想快速知道「這是做什麼的、我能不能用、下一步該按哪裡」的人

那目前的語言仍然太重：

- `campaign`
- `qualification`
- `participation request`
- `structured feedback`
- `role-aware`
- `session`

這些詞在登入前會提高理解成本，直接影響首頁轉換。

## 2. 目標

先把 public 面的語言改成沒有開發背景也能快速理解的產品語言：

- 首先知道這個工具是做什麼的
- 再知道自己是不是適合使用
- 最後知道下一步該去登入還是註冊

## 3. 範圍

- `/`
- `/login`
- `/register`
- public header 的 CTA 文案
- 首頁與 auth page 直接相關的 i18n key

## 4. 文案方向建議

整體原則：

- 先講好處，再講流程
- 先講人話，再講系統詞
- 先講使用情境，再講功能名稱

建議替換方向：

- `campaign` -> `測試活動`
- `qualification` -> `是否適合參與`
- `participation request` -> `報名參與`
- `structured feedback` -> `整理好的回饋`
- `developer` -> `發起測試的人`
- `tester` -> `參與測試的人`

如果必須保留系統詞，應：

- 先用主標題寫人話
- 再用次要說明補上原本系統概念

## 5. 首頁資訊架構建議

首頁應優先回答：

1. 這個工具是做什麼的
2. 為什麼它比自己拼 Notion / 表單 / 訊息更方便
3. 你會怎麼用它
4. 下一步要按哪個按鈕

首頁應避免：

- 把自己寫成規格文件
- 用太多流程管理術語
- 一開始就要求使用者理解資料模型

## 6. API / Route 建議

本票不新增 API。

route 維持：

- `/`
- `/login`
- `/register`

## 7. 前端頁面 / 路由建議

主要修改：

- `frontend/pages/index.vue`
- `frontend/pages/login.vue`
- `frontend/pages/register.vue`
- `frontend/layouts/public.vue`
- `frontend/features/i18n/use-app-i18n.ts`

## 8. Acceptance Criteria

- public landing 的主要文案不再依賴工程或 QA 術語
- 沒有開發背景的人能從首頁理解：
  - 這是做什麼的
  - 我能不能用
  - 下一步要按哪個按鈕
- `/login`、`/register` 的文案與首頁語氣一致
- `zh-TW / en` 兩套文案同步成立
- 不改 route、不改 backend API

## 9. Out of Scope

- 不改 app 內頁的大量文案
- 不改 dashboard 資訊架構
- 不新增 marketing 子頁
- 不做全站 i18n 完成票

## 10. Backend Work Items

- 無新的 runtime 工作

## 11. Frontend Work Items

- 重寫首頁 hero、trust、flow、role value、final CTA 文案
- 重寫 public header 的 CTA label
- 對齊 `/login`、`/register` 的入口語言
- 收斂首頁與 auth page 的中英文 i18n key
- 移除不必要的工程導向名詞

## 12. Test Items

- frontend `typecheck`
- frontend `build`
- `home.spec.ts`
- `auth-shell.spec.ts`
- `i18n-shell.spec.ts`
- 驗證首頁與 auth pages 在 `zh-TW / en` 下都能以非技術語言成立

## 13. Risk / Notes

- 這張票的風險不是功能錯，而是文案改太空泛，導致產品反而變得不清楚
- 目標不是把所有系統概念隱藏，而是降低第一眼理解成本
- 英文文案也要避免內部工具感，不能只是把舊術語直譯

## 14. 依賴關係（Dependencies）

- `T092`

