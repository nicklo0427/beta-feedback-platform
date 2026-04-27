# T105 - Operational Safety Baseline

## 背景

Public beta 開放後，最小營運安全需要比本地 demo 更清楚：如何檢查健康狀態、如何排查錯誤、如何避免 seed/demo 資料污染、如何備份與回復資料。這張票建立 beta 期間可執行的 operational safety baseline。

## 目標

補齊 public beta 最小營運安全：

- health / smoke / evidence 操作方式清楚
- seed 與真實環境隔離
- database migration / backup / restore 注意事項清楚
- 常見故障排查有 runbook

## 範圍

- OPS runbook 更新
- launch checklist operational section
- seed/demo data safety notes
- smoke / evidence pack usage guidance
- basic incident checklist

## API / Route / Data 建議

- 不新增 backend API
- 可補強既有 health / smoke 文件說明
- 不新增 logging vendor integration

## Backend Work Items

- 檢查 health response 是否已足夠支援 beta readiness 判斷。
- 確認 migration 指令、backup 注意事項、database configured 判斷寫入 docs。
- 若 scripts 的錯誤訊息不足，可小幅改善 CLI output。

## Frontend Work Items

- 確認 backend unavailable 時 frontend error state 不白頁。
- 如需補文件，記錄 frontend dev / preview / production 啟動排查方式。

## Acceptance Criteria

- `OPS_RUNBOOK.md` 可直接指引 beta 啟動、health、smoke、rollout evidence、故障排查。
- `PUBLIC_BETA_LAUNCH_CHECKLIST.md` 明確要求 migration、backup、smoke、evidence。
- `LOCAL_DEMO_SEED.md` 明確說明 seed 不應跑在真實 public beta database。
- 常見 incident 有第一時間處理順序。

## Out of Scope

- 不導入完整 observability 平台。
- 不做 automated backup service。
- 不做 multi-environment deploy automation。
- 不做 production GA 安全審計。

## Test Items

- docs link check by inspection
- `public_beta_smoke.py`
- `beta_rollout_verification.py`
- frontend backend-offline manual smoke

## Risk / Notes

- 這張票偏文件與操作安全，實作時不要把 scope 擴成完整 DevOps 平台。
- 若 target env 已有實際 provider，文件需使用該 provider 的具體操作名稱。

## Dependencies

- `T102`
- `T103`
