# T068 - Public Beta QA and Launch Checklist

## 1. 背景

在 public beta 前，光有功能與部署還不夠。manual QA、seed fixture、README、已知限制、beta onboarding 文案若不同步，對外試用時很容易出現誤解或驗收落差。

## 2. 目標

把 public beta 前最後一輪文件與驗收清單整理到可發佈水位。

## 3. 範圍

- 更新 `MANUAL_QA.md`
- 更新 seed / demo 文件
- 更新 `README.md`
- 補 public beta launch checklist
- 補 beta onboarding / known limitations 文案

## 4. 資料模型建議

本票不新增產品資料模型。

## 5. API 路徑建議

本票不新增 API。

重點是文件與 QA 需要對齊：

- auth / session
- persistence mode
- public beta 核心使用路徑

## 6. 前端頁面 / 路由建議

文件至少涵蓋：

- login / register
- homepage
- account / project / campaign / participation / task / feedback 主流程
- public beta 中保留的已知限制與 fallback

## 7. Acceptance Criteria

- `MANUAL_QA.md` 可直接支撐 public beta 前最終驗收
- `README.md` 已明確反映 public beta 狀態與啟動方式
- seed / demo 文件與實際 env / persistence / auth 模式一致
- 有一份 launch checklist 可供上線前逐項確認

## 8. Out of Scope

- 不做 marketing site
- 不做正式客服/支援文件中心
- 不做完整 contributor guide 大重寫

## 9. Backend Work Items

- 原則上無新的產品功能
- 如 checklist 需要最小 smoke endpoint 說明，可同步到文件

## 10. Frontend Work Items

- 原則上無新的產品功能
- 如 onboarding 文案需小幅同步，可控制在 public beta 說明範圍內

## 11. Test Items

- seed smoke
- manual QA walk-through
- README / launch checklist 指令可用性檢查

## 12. Risk / Notes

- 這張票是 public beta 前的收斂票，不應再順手擴新功能
- 文件必須反映已完成能力，不預寫未完成項目

## 13. 依賴關係（Dependencies）

主要依賴：

- `T064`
- `T065`
- `T066`
- `T067`
