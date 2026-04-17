<script setup lang="ts">
definePageMeta({
  path: '/review/participation-requests/:requestId'
})

import { computed } from 'vue'

import ActivityTimelinePanel from '~/features/activity-events/ActivityTimelinePanel.vue'
import { fetchParticipationRequestTimeline } from '~/features/activity-events/api'
import { fetchAccounts } from '~/features/accounts/api'
import {
  getActorAwareReadErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import { formatCampaignStatusLabel } from '~/features/campaigns/types'
import { formatQualificationStatusLabel } from '~/features/eligibility/types'
import {
  formatParticipationAssignmentStatusLabel,
  formatParticipationRequestStatusLabel
} from '~/features/participation-requests/types'
import { fetchParticipationRequestDetail } from '~/features/participation-requests/api'
import { formatPlatformLabel } from '~/features/platform-display'

useCurrentActorPersistence()

const route = useRoute()
const requestId = computed(() => String(route.params.requestId))
const currentActorId = useCurrentActorId()

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('review-participation-detail-accounts', () => fetchAccounts(), {
  server: false,
  default: () => ({
    items: [],
    total: 0
  })
})

const accounts = computed(() => accountResponse.value.items)
const currentActor = computed(
  () => accounts.value.find((account) => account.id === currentActorId.value) ?? null
)
const isDeveloperActor = computed(() => currentActor.value?.role === 'developer')

const {
  data: participationRequest,
  pending,
  error,
  refresh
} = useAsyncData(
  () =>
    `review-participation-request-detail-${requestId.value}-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
  async () => {
    if (!currentActorId.value || !isDeveloperActor.value) {
      return null
    }

    return fetchParticipationRequestDetail(requestId.value, currentActorId.value)
  },
  {
    server: false,
    watch: [requestId, currentActorId, currentActor],
    default: () => null
  }
)

const testerSummary = computed(
  () => participationRequest.value?.tester_account_summary.tester_summary ?? null
)
const canCreateTaskFromRequest = computed(
  () =>
    participationRequest.value?.status === 'accepted'
    && !participationRequest.value.linked_task_id
)
const detailErrorMessage = computed(() =>
  getActorAwareReadErrorMessage(error.value, '找不到指定的參與意圖。')
)
const {
  data: timelineResponse,
  pending: timelinePending,
  error: timelineError
} = useAsyncData(
  () =>
    `review-participation-request-timeline-${requestId.value}-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
  async () => {
    if (!currentActorId.value || !isDeveloperActor.value) {
      return {
        items: [],
        total: 0
      }
    }

    return fetchParticipationRequestTimeline(requestId.value, currentActorId.value)
  },
  {
    server: false,
    watch: [requestId, currentActorId, currentActor],
    default: () => ({
      items: [],
      total: 0
    })
  }
)
const timelineEvents = computed(() => timelineResponse.value.items)
const timelineErrorMessage = computed(() =>
  timelineError.value
    ? getActorAwareReadErrorMessage(timelineError.value, '目前無法載入參與意圖時間線。')
    : null
)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/review/participation-requests">
          參與意圖審查佇列
        </NuxtLink>
        <h1 class="resource-shell__title">參與意圖詳情</h1>
        <p class="resource-shell__description">
          這個頁面提供開發者查看單一 participation request 的候選人快照，包含測試者摘要、裝置設定檔、資格判斷與活動上下文。
        </p>
      </header>

      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="participation-request-detail-actor-error"
      >
        <h2 class="resource-state__title">無法取得操作情境</h2>
        <p class="resource-state__description">{{ accountsError.message }}</p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshAccounts()">
            重試
          </button>
        </div>
      </section>

      <section
        v-else-if="accountsPending"
        class="resource-state"
        data-testid="participation-request-detail-actor-loading"
      >
        <h2 class="resource-state__title">載入開發者情境中</h2>
        <p class="resource-state__description">
          正在確認目前操作帳號與這筆 participation request 的可見範圍。
        </p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="participation-request-detail-select-actor"
      >
        <h2 class="resource-state__title">請選擇開發者帳號</h2>
        <p class="resource-state__description">
          先選擇目前操作帳號，系統才知道要用哪一位開發者的 owned campaigns 驗證這筆 participation request。
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="participation-request-detail-actor-missing"
      >
        <h2 class="resource-state__title">找不到已選擇的帳號</h2>
        <p class="resource-state__description">
          目前找不到你選擇的帳號，請重新選擇一筆可用的開發者帳號。
        </p>
      </section>

      <section
        v-else-if="!isDeveloperActor"
        class="resource-state"
        data-testid="participation-request-detail-role-mismatch"
      >
        <h2 class="resource-state__title">參與意圖詳情需要開發者帳號</h2>
        <p class="resource-state__description">
          目前選到的是{{ formatAccountRoleLabel(currentActor.role) }}帳號。請切換到開發者帳號，再查看這筆 participation request 的候選人快照。
        </p>
      </section>

      <section
        v-else-if="pending"
        class="resource-state"
        data-testid="participation-request-detail-loading"
      >
        <h2 class="resource-state__title">載入參與意圖詳情中</h2>
        <p class="resource-state__description">
          正在整理測試者、裝置設定檔、資格判斷與活動上下文。
        </p>
      </section>

      <section
        v-else-if="error || !participationRequest"
        class="resource-state"
        data-testid="participation-request-detail-error"
      >
        <h2 class="resource-state__title">無法載入參與意圖詳情</h2>
        <p class="resource-state__description">
          {{ detailErrorMessage }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試
          </button>
          <NuxtLink class="resource-action" to="/review/participation-requests">
            返回參與意圖審查佇列
          </NuxtLink>
        </div>
      </section>

      <template v-else>
        <div class="detail-layout" data-testid="participation-request-detail-layout">
          <div class="detail-layout__main">
        <section
          class="resource-section"
          data-testid="participation-request-detail-panel"
        >
          <span class="resource-section__eyebrow">Participation Request</span>
          <h2 class="resource-section__title">{{ participationRequest.campaign_name }}</h2>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              :to="`/campaigns/${participationRequest.campaign_id}`"
            >
              查看活動
            </NuxtLink>
            <NuxtLink
              v-if="canCreateTaskFromRequest"
              class="resource-action"
              data-testid="participation-request-create-task-link"
              :to="`/review/participation-requests/${participationRequest.id}/tasks/new`"
            >
              從 request 建立任務
            </NuxtLink>
            <NuxtLink
              v-else-if="participationRequest.linked_task_id"
              class="resource-action"
              data-testid="participation-request-linked-task-link"
              :to="`/tasks/${participationRequest.linked_task_id}`"
            >
              查看對應任務
            </NuxtLink>
            <NuxtLink class="resource-action" to="/review/participation-requests">
              返回審查佇列
            </NuxtLink>
          </div>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              狀態 {{ formatParticipationRequestStatusLabel(participationRequest.status) }}
            </span>
            <span class="resource-shell__meta-chip">
              裝置 {{ participationRequest.device_profile_name }}
            </span>
            <span class="resource-shell__meta-chip">
              任務橋接 {{ formatParticipationAssignmentStatusLabel(participationRequest.assignment_status) }}
            </span>
          </div>
          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">參與意圖 ID</span>
              <span class="resource-key-value__value">{{ participationRequest.id }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">測試者備註</span>
              <span class="resource-key-value__value">
                {{ participationRequest.note || '目前沒有補充說明。' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">處理備註</span>
              <span class="resource-key-value__value">
                {{ participationRequest.decision_note || '目前尚未提供處理備註。' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">建立時間</span>
              <span class="resource-key-value__value">{{ participationRequest.created_at }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">更新時間</span>
              <span class="resource-key-value__value">{{ participationRequest.updated_at }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">處理時間</span>
              <span class="resource-key-value__value">
                {{ participationRequest.decided_at || '尚未處理。' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">對應任務</span>
              <NuxtLink
                v-if="participationRequest.linked_task_id"
                class="resource-key-value__value"
                :to="`/tasks/${participationRequest.linked_task_id}`"
              >
                {{ participationRequest.linked_task_id }}
              </NuxtLink>
              <span v-else class="resource-key-value__value">
                尚未建立。
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">建立任務時間</span>
              <span class="resource-key-value__value">
                {{ participationRequest.assignment_created_at || '尚未建立。' }}
              </span>
            </div>
          </div>
        </section>

        <ActivityTimelinePanel
          title="參與意圖時間線"
          description="這裡會整理這筆 participation request 的關鍵操作事件，方便開發者回顧接受、婉拒或任務橋接是怎麼發生的。"
          :pending="timelinePending"
          :error-message="timelineErrorMessage"
          :events="timelineEvents"
          empty-message="這筆 participation request 目前還沒有可顯示的關鍵事件。"
          test-id-prefix="participation-request-timeline"
        />

        <section
          class="resource-section"
          data-testid="participation-request-tester-panel"
        >
          <h2 class="resource-section__title">測試者快照</h2>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              :to="`/accounts/${participationRequest.tester_account.id}`"
            >
              查看帳號詳情
            </NuxtLink>
          </div>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              {{ participationRequest.tester_account.display_name }}
            </span>
            <span class="resource-shell__meta-chip">
              {{ formatAccountRoleLabel(participationRequest.tester_account.role) }}
            </span>
          </div>
          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">帳號 ID</span>
              <span class="resource-key-value__value">{{ participationRequest.tester_account.id }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">語系</span>
              <span class="resource-key-value__value">
                {{ participationRequest.tester_account.locale || '尚未提供。' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">簡介</span>
              <span class="resource-key-value__value">
                {{ participationRequest.tester_account.bio || '尚未提供。' }}
              </span>
            </div>
            <div
              v-if="testerSummary"
              class="resource-key-value__row"
            >
              <span class="resource-key-value__label">裝置設定檔數</span>
              <span class="resource-key-value__value">{{ testerSummary.owned_device_profiles_count }}</span>
            </div>
            <div
              v-if="testerSummary"
              class="resource-key-value__row"
            >
              <span class="resource-key-value__label">已指派任務數</span>
              <span class="resource-key-value__value">{{ testerSummary.assigned_tasks_count }}</span>
            </div>
            <div
              v-if="testerSummary"
              class="resource-key-value__row"
            >
              <span class="resource-key-value__label">已提交回饋數</span>
              <span class="resource-key-value__value">{{ testerSummary.submitted_feedback_count }}</span>
            </div>
          </div>
        </section>

        <section
          class="resource-section"
          data-testid="participation-request-device-profile-panel"
        >
          <h2 class="resource-section__title">裝置設定檔快照</h2>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              :to="`/device-profiles/${participationRequest.device_profile.id}`"
            >
              查看裝置設定檔
            </NuxtLink>
          </div>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              {{ formatPlatformLabel(participationRequest.device_profile.platform) }}
            </span>
            <span class="resource-shell__meta-chip">
              安裝渠道 {{ participationRequest.device_profile.install_channel || '尚未提供' }}
            </span>
          </div>
          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">裝置設定檔 ID</span>
              <span class="resource-key-value__value">{{ participationRequest.device_profile.id }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">裝置型號</span>
              <span class="resource-key-value__value">{{ participationRequest.device_profile.device_model }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">作業系統</span>
              <span class="resource-key-value__value">
                {{ participationRequest.device_profile.os_name }} {{ participationRequest.device_profile.os_version || '' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">提交率</span>
              <span class="resource-key-value__value">
                {{ participationRequest.device_profile_reputation.submission_rate.toFixed(2) }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">已指派任務數</span>
              <span class="resource-key-value__value">{{ participationRequest.device_profile_reputation.tasks_assigned_count }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">已提交回饋數</span>
              <span class="resource-key-value__value">{{ participationRequest.device_profile_reputation.feedback_submitted_count }}</span>
            </div>
          </div>
        </section>

          </div>

          <aside class="detail-layout__rail">

        <section
          class="resource-section"
          data-testid="participation-request-qualification-panel"
        >
          <span class="resource-section__eyebrow">Qualification</span>
          <h2 class="resource-section__title">資格判斷快照</h2>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              狀態 {{ formatQualificationStatusLabel(participationRequest.qualification_snapshot.qualification_status) }}
            </span>
          </div>
          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">命中規則</span>
              <span class="resource-key-value__value">
                {{ participationRequest.qualification_snapshot.matched_rule_id || '目前沒有命中的資格規則。' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">資格摘要</span>
              <span class="resource-key-value__value">
                {{ participationRequest.qualification_snapshot.reason_summary || '目前沒有額外的資格摘要。' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">原因代碼</span>
              <span class="resource-key-value__value">
                {{
                  participationRequest.qualification_snapshot.reason_codes.length > 0
                    ? participationRequest.qualification_snapshot.reason_codes.join(', ')
                    : '目前沒有失敗原因代碼。'
                }}
              </span>
            </div>
          </div>
        </section>

        <section
          class="resource-section"
          data-testid="participation-request-campaign-panel"
        >
          <span class="resource-section__eyebrow">Campaign Snapshot</span>
          <h2 class="resource-section__title">活動快照</h2>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              :to="`/campaigns/${participationRequest.campaign.id}`"
            >
              查看活動詳情
            </NuxtLink>
          </div>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              {{ formatCampaignStatusLabel(participationRequest.campaign.status) }}
            </span>
            <span class="resource-shell__meta-chip">
              平台
              {{
                participationRequest.campaign.target_platforms
                  .map((platform) => formatPlatformLabel(platform))
                  .join(' / ')
              }}
            </span>
          </div>
          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">活動 ID</span>
              <span class="resource-key-value__value">{{ participationRequest.campaign.id }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">版本標籤</span>
              <span class="resource-key-value__value">
                {{ participationRequest.campaign.version_label || '尚未提供。' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">已關閉任務數</span>
              <span class="resource-key-value__value">{{ participationRequest.campaign_reputation.tasks_closed_count }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">收到回饋數</span>
              <span class="resource-key-value__value">{{ participationRequest.campaign_reputation.feedback_received_count }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">結案率</span>
              <span class="resource-key-value__value">
                {{ participationRequest.campaign_reputation.closure_rate.toFixed(2) }}
              </span>
            </div>
          </div>
        </section>
          </aside>
        </div>
      </template>
    </section>
  </main>
</template>
