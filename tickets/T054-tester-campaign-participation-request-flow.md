# T054 - Tester Campaign Participation Request Flow

## 1. 背景

tester 現在已能看見：

- campaign detail qualification panel
- `/my/eligible-campaigns`

但還不能在符合資格時做下一步動作。這會讓 tester flow 停在 read-only。

## 2. 目標

建立 tester 端最小 participation request flow，讓 tester 能基於 qualified device profile 對 campaign 表達參與意圖。

## 3. 範圍

本票只做最小集合：

- backend `ParticipationRequest` create / list mine / withdraw
- frontend 在 campaign detail 與 eligible campaigns workspace 提供 submit CTA
- frontend 新增 `/my/participation-requests`

## 4. 資料模型建議

延用 `T053`：

- `campaign_id`
- `tester_account_id`
- `device_profile_id`
- `status`
- `note`
- `decision_note`

MVP 限縮：

- create 時 `status = pending`
- tester 僅能把自己的 pending request withdraw

## 5. API 路徑建議

- `GET /api/v1/participation-requests?mine=true`
- `POST /api/v1/campaigns/{campaign_id}/participation-requests`
- `PATCH /api/v1/participation-requests/{request_id}`

## 6. 前端頁面 / 路由建議

涉及：

- `frontend/pages/campaigns/[campaignId].vue`
- `frontend/pages/my/eligible-campaigns.vue`
- `frontend/pages/my/participation-requests.vue`

## 7. Acceptance Criteria

- tester 可用 owned 且 qualified 的 `device_profile` 對 campaign 建立 participation request
- request 建立後可在 `/my/participation-requests` 看到
- tester 可 withdraw 自己的 pending request
- developer actor / missing actor / ineligible device profile 都會被 guard 擋住

## 8. Out of Scope

- 不做 developer accept / decline
- 不做 task auto-creation
- 不做 messaging / notification

## 9. Backend Work Items

- 新增 `participation_requests` module
- create / list mine / patch withdraw
- actor-aware 與 qualification-aware guards

## 10. Frontend Work Items

- 新增 request types / API helpers
- campaign detail / eligible campaigns CTA
- `/my/participation-requests` shell-level list

## 11. Test Items

### 11.1 Backend

- create happy path
- duplicate pending guard
- ineligible request blocked
- withdraw own pending request

### 11.2 Frontend

- campaign detail submit flow
- eligible campaigns submit flow
- my participation requests list / withdraw

## 12. Risk / Notes

- request 建立時必須嚴格沿用 qualification evaluator，不要複製第二套邏輯
- 這張票不要順手做 developer review queue

## 13. 依賴關係（Dependencies）

主要依賴：

- `T052-qualification-evaluator-install-channel-fidelity`
- `T053-participation-intent-semantics-draft`

後續支撐：

- `T055-developer-participation-review-queue-and-decision-actions`

