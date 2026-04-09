# T052 - Qualification Evaluator Install Channel Fidelity

## 1. 背景

`T051` 會先把 `device_profile.install_channel` 補齊，但 qualification evaluator 與各個 qualification-related UI 也需要同步更新，否則：

- `install_channel` 仍不會真正參與判斷
- qualification panel / eligible campaigns / assignment preview 的結果仍不可信

## 2. 目標

讓 qualification evaluator 正式支援 `install_channel`，並把結果同步反映到所有現有 qualification UI。

## 3. 範圍

本票只做 evaluator fidelity 補強：

- backend evaluator 支援 `install_channel`
- qualification result / summary 對齊新欄位
- frontend qualification panel / eligible campaigns / assignment preview 顯示更新後結果

## 4. 資料模型建議

不新增新 domain，但需確保 evaluator 對以下欄位一致判斷：

- `platform`
- `os_name`
- `os_version_min`
- `os_version_max`
- `install_channel`

## 5. API 路徑建議

延用既有 qualification routes：

- `GET /api/v1/campaigns/{campaign_id}/qualification-results?mine=true`
- `GET /api/v1/campaigns/{campaign_id}/qualification-check?device_profile_id=...`
- `GET /api/v1/campaigns?qualified_for_me=true`
- `GET /api/v1/tasks`
- `GET /api/v1/tasks/{task_id}`

## 6. 前端頁面 / 路由建議

涉及：

- `frontend/pages/campaigns/[campaignId].vue`
- `frontend/pages/campaigns/task-new-[campaignId].vue`
- `frontend/pages/tasks/edit-[taskId].vue`
- `frontend/pages/my/eligible-campaigns.vue`
- `frontend/pages/tasks/[taskId].vue`
- `frontend/pages/my/tasks.vue`

## 7. Acceptance Criteria

- `install_channel` 會被 qualification evaluator 正式使用
- qualification pass / fail 會正確反映 `install_channel`
- assignment preview 與 assignment guard 結果對齊 evaluator
- task qualification context / drift warning 也能反映新的 signal

## 8. Out of Scope

- 不做新 rule dimension
- 不做 matching engine
- 不做 recommendation ranking

## 9. Backend Work Items

- 更新 `eligibility` evaluator
- 視需要更新 `tasks` derived qualification context
- 補 service / API tests

## 10. Frontend Work Items

- 更新 qualification-related API types
- 補 qualification summary 文案
- 重用既有 resource section / card pattern

## 11. Test Items

### 11.1 Backend

- qualification results with install_channel pass / fail
- assignment preview with install_channel pass / fail
- task qualification context / drift with install_channel

### 11.2 Frontend

- campaign qualification panel
- eligible campaigns workspace
- task assignment preview
- task detail / inbox qualification context

## 12. Risk / Notes

- 這張票要避免順手加更多 eligibility dimensions
- 目標是讓現有 qualification 結果更可信，而不是重寫 evaluator

## 13. 依賴關係（Dependencies）

主要依賴：

- `T051-device-profile-install-channel-baseline-and-form-support`

後續支撐：

- `T054-tester-campaign-participation-request-flow`
- `T055-developer-participation-review-queue-and-decision-actions`

