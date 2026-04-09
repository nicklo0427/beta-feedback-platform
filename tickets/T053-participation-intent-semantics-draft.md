# T053 - Participation Intent Semantics Draft

## 1. 背景

qualification phase 已完成，但 tester 目前只能看見：

- 哪些 campaign 自己符合資格

系統還沒有正式定義：

- tester 如何表達參與意圖
- developer 如何處理這個意圖
- 需要哪些最小 status 與 guardrails

如果沒有先文件化，後續 runtime flow 很容易長出不一致的角色規則與錯誤契約。

## 2. 目標

建立 `Participation Intent` 的最小文件基線，作為後續：

- `T054`
- `T055`
- `T056`

的直接實作依據。

## 3. 範圍

本票只做文件層面的最小定義：

- participation request 最小資料模型
- status baseline
- role / ownership / qualification guards
- create / withdraw / accept / decline baseline

## 4. 資料模型建議

新增概念：

- `ParticipationRequest`

建議最小欄位：

- `id`
- `campaign_id`
- `tester_account_id`
- `device_profile_id`
- `status`
- `note`
- `decision_note`
- `created_at`
- `updated_at`
- `decided_at`

### 4.1 Status Baseline

建議最小集合：

- `pending`
- `accepted`
- `declined`
- `withdrawn`

### 4.2 Guardrails Baseline

文件需明確定義：

- 只有 `tester` 可建立 / withdraw 自己的 request
- 只有擁有 campaign 的 `developer` 可 accept / decline
- request 建立時必須使用符合資格的 owned `device_profile`
- 同一 tester / device_profile / campaign 只能有一筆 active pending request

## 5. API 路徑建議

本票不新增 runtime code，但文件中應先為後續票標示：

- `GET /api/v1/participation-requests?mine=true`
- `POST /api/v1/campaigns/{campaign_id}/participation-requests`
- `GET /api/v1/participation-requests?review_mine=true`
- `PATCH /api/v1/participation-requests/{request_id}`
- `GET /api/v1/participation-requests/{request_id}`

## 6. 前端頁面 / 路由建議

本票不新增頁面，但文件需標明後續會涉及：

- `frontend/pages/campaigns/[campaignId].vue`
- `frontend/pages/my/eligible-campaigns.vue`
- `frontend/pages/my/participation-requests.vue`
- `frontend/pages/review/participation-requests.vue`
- `frontend/pages/review/participation-requests/[requestId].vue`

## 7. Acceptance Criteria

- `DATA_MODEL_DRAFT.md` 或等價文件已明確寫出 participation request baseline
- 已定義 status、actor guard、ownership guard、qualification guard
- 後續 `T054` 到 `T056` 可直接引用，不需再重定義

## 8. Out of Scope

- 不做 chat / threaded messaging
- 不做 notifications
- 不做 auto task creation
- 不做 marketplace matching

## 9. Backend Work Items

- 無 runtime code
- 補 participation semantics 文件

## 10. Frontend Work Items

- 無 runtime code
- 視需要補 current actor / request flow 文件說明

## 11. Test Items

- 無 runtime tests
- 文件術語需與 `README.md`、`DATA_MODEL_DRAFT.md`、`NEXT_PHASE_PLAN.md` 對齊

## 12. Risk / Notes

- 這張票最重要的是保持 participation baseline 極小
- 只定 request / review / withdraw，不要長成完整 marketplace 設計

## 13. 依賴關係（Dependencies）

主要依賴：

- `T044-qualification-and-assignment-semantics-draft`
- `T052-qualification-evaluator-install-channel-fidelity`

後續支撐：

- `T054-tester-campaign-participation-request-flow`
- `T055-developer-participation-review-queue-and-decision-actions`
- `T056-participation-request-detail-and-candidate-snapshot-panels`

