# T067 - Public Beta Ops Baseline

## 1. 背景

就算功能、auth、persistence 都補齊，如果沒有最小 deployment / env / health / smoke runbook，仍不能安心對外開 public beta。這張票負責把 repo 從「可開發」推到「可部署 / 可維護」的最小水位。

## 2. 目標

建立 public beta 的最小營運 baseline，至少讓團隊可以：

- 啟動完整 stack
- 驗證健康狀態
- 跑 smoke checks
- 知道發生問題時先看哪裡

## 3. 範圍

- 環境變數範本
- 啟動 / 部署文件
- health check / smoke runbook
- 最小錯誤監看與 log 路徑說明

## 4. 資料模型建議

本票不新增產品資料模型。

## 5. API 路徑建議

沿用既有：

- `GET /api/v1/health`

必要時可補：

- frontend app health / readiness 檢查方式

## 6. 前端頁面 / 路由建議

本票原則上不新增產品頁面。

如需補最小 maintenance / readiness 顯示，應控制在不影響既有 IA 的範圍內。

## 7. Acceptance Criteria

- repo 有明確的 public beta 啟動方式
- env vars 有 `.env.example` 或同等文件
- 有最小 smoke runbook 可驗證 backend / frontend / database
- 出問題時，至少知道健康檢查、logs、常見故障排查入口

## 8. Out of Scope

- 不做完整 observability platform
- 不做 paging / on-call
- 不做 auto-scaling
- 不做 cloud-vendor-specific 深度整合

## 9. Backend Work Items

- env config 整理
- health / readiness baseline
- deployment / startup docs

## 10. Frontend Work Items

- frontend 啟動與 smoke 路徑說明
- 如有必要，補最小 startup verification

## 11. Test Items

- documented startup smoke
- health endpoint smoke
- end-to-end stack bring-up check

## 12. Risk / Notes

- 這張票是營運 baseline，不是 infra platform 專案
- 優先選 vendor-neutral、repo-local 的做法
- 文件應能讓新加入的人直接照著拉起環境

## 13. 依賴關係（Dependencies）

主要依賴：

- `T066`

