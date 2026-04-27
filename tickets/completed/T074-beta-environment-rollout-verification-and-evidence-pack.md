# T074 - Beta Environment Rollout Verification and Evidence Pack

## 1. 背景

`T067` 與 `T068` 已把 runbook、manual QA、launch checklist 都寫進 repo，但真正的 public beta readiness 仍要以「目標環境是否真的跑過一次」為準，而不是只停在本地文件。

## 2. 目標

在目標 beta 環境執行一次完整 rollout rehearsal，留下可追溯的驗證結果與 go / no-go evidence。

## 3. 範圍

- 目標環境 health / smoke
- session-only 驗證
- 手動 QA 最小必驗案例
- 已知限制與 rollout note
- go / no-go evidence pack

## 4. 資料模型建議

本票不新增產品資料模型。

## 5. API 路徑建議

沿用既有：

- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- public beta 核心流程相關 routes

## 6. 前端頁面 / 路由建議

至少驗證：

- `/login`
- `/register`
- `/`
- `/projects`
- `/campaigns`
- `/tasks`
- `/review/feedback`

## 7. Acceptance Criteria

- 目標 beta 環境已跑過一次 launch checklist
- smoke output、health payload、主要頁面截點或驗證結果有留存
- 已知限制有整理成發佈說明
- 有一份 go / no-go 結論

## 8. Out of Scope

- 不做 marketing launch campaign
- 不做正式 incident management platform
- 不做 full observability rebuild

## 9. Backend Work Items

- 原則上不新增產品功能
- 如 rollout 過程暴露 blocker，可開新票處理

## 10. Frontend Work Items

- 原則上不新增產品功能
- 若 rollout 過程暴露 onboarding 文案問題，可收斂成小幅文件或提示調整

## 11. Test Items

- target env health check
- `public_beta_smoke.py`
- [PUBLIC_BETA_LAUNCH_CHECKLIST.md](/Users/lowhaijer/projects/beta-feedback-platform/PUBLIC_BETA_LAUNCH_CHECKLIST.md) 必驗項

## 12. Risk / Notes

- 這張票不是本地文件票，而是環境執行票
- 若 rollout rehearsal 失敗，應開新的 blocker ticket，而不是硬說 beta ready

## 13. 依賴關係（Dependencies）

主要依賴：

- `T067`
- `T068`
