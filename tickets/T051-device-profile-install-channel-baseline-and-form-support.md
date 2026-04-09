# T051 - Device Profile Install Channel Baseline and Form Support

## 1. 背景

目前 `eligibility rules` 已支援：

- `install_channel`

但 `device_profiles` 還沒有對應欄位。這會造成：

- qualification evaluator 對這類規則幾乎只能回 fail
- campaign qualification panel 的結果失真
- assignment preview / guard 對這類規則無法提供可信判斷

## 2. 目標

為 `Device Profile` 補上 `install_channel` baseline，讓 qualification evaluator 有完整的最小資料來源。

## 3. 範圍

本票只做最小 baseline：

- backend `device_profiles` 資料模型新增 `install_channel`
- frontend create / edit form 補 `install_channel`
- list / detail 顯示 `install_channel`
- actor-aware ownership baseline 不被破壞

## 4. 資料模型建議

新增欄位：

- `install_channel: string | null`

MVP 原則：

- 先不做嚴格 enum
- 允許自由字串，以對齊不同平台的 distribution / install 語意

## 5. API 路徑建議

延用既有：

- `GET /api/v1/device-profiles`
- `POST /api/v1/device-profiles`
- `GET /api/v1/device-profiles/{device_profile_id}`
- `PATCH /api/v1/device-profiles/{device_profile_id}`

## 6. 前端頁面 / 路由建議

涉及：

- `frontend/pages/device-profiles/index.vue`
- `frontend/pages/device-profiles/new.vue`
- `frontend/pages/device-profiles/edit-[deviceProfileId].vue`
- `frontend/pages/device-profiles/[deviceProfileId].vue`

## 7. Acceptance Criteria

- backend `device profile` response / request 已支援 `install_channel`
- frontend create / edit form 可建立與更新 `install_channel`
- list / detail 可顯示 `install_channel`
- ownership / `mine=true` baseline 仍正常
- 既有測試與 E2E 不被破壞

## 8. Out of Scope

- 不做 platform-specific controlled vocabulary
- 不做 install channel 自動推薦
- 不做 migration / persistence 設計

## 9. Backend Work Items

- 更新 `device_profiles` schema / model / service / API tests
- 維持 in-memory repository

## 10. Frontend Work Items

- 更新 `device profile` form type / API / form component
- 補 detail / list 顯示
- 重用既有 form pattern

## 11. Test Items

### 11.1 Backend

- validation
- service
- API

### 11.2 Frontend

- typecheck
- build
- Playwright：
  - device profile create / edit with install_channel
  - list / detail render

## 12. Risk / Notes

- 欄位先採自由字串，避免過早把不同平台分發方式鎖死
- 這張票最重要的是補 qualification signal，不是做 taxonomy 設計

## 13. 依賴關係（Dependencies）

主要依賴：

- `T012-tester-device-profile-crud-and-shell-flows`
- `T045-campaign-qualification-check-api-and-current-tester-shell`

後續支撐：

- `T052-qualification-evaluator-install-channel-fidelity`

