<script setup lang="ts">
import { computed } from 'vue'

import { fetchCampaignDetail } from '~/features/campaigns/api'
import { formatCampaignStatusLabel } from '~/features/campaigns/types'
import { fetchCampaignEligibilityRules } from '~/features/eligibility/api'
import { formatPlatformLabel } from '~/features/platform-display'
import { fetchCampaignReputation } from '~/features/reputation/api'
import { fetchCampaignSafety } from '~/features/safety/api'
import {
  formatDistributionChannelLabel,
  formatReviewStatusLabel,
  formatRiskLevelLabel
} from '~/features/safety/types'
import { fetchTasks } from '~/features/tasks/api'
import { formatTaskStatusLabel } from '~/features/tasks/types'

const route = useRoute()
const campaignId = computed(() => String(route.params.campaignId))

const {
  data: campaign,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `campaign-detail-${campaignId.value}`,
  () => fetchCampaignDetail(campaignId.value),
  {
    server: false,
    watch: [campaignId],
    default: () => null
  }
)

const {
  data: eligibilityRuleResponse,
  pending: eligibilityPending,
  error: eligibilityError,
  refresh: refreshEligibility
} = useAsyncData(
  () => `campaign-eligibility-${campaignId.value}`,
  () => fetchCampaignEligibilityRules(campaignId.value),
  {
    server: false,
    watch: [campaignId],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const eligibilityRules = computed(() => eligibilityRuleResponse.value.items)

const {
  data: safety,
  pending: safetyPending,
  error: safetyError,
  refresh: refreshSafety
} = useAsyncData(
  () => `campaign-safety-${campaignId.value}`,
  () => fetchCampaignSafety(campaignId.value),
  {
    server: false,
    watch: [campaignId],
    default: () => null
  }
)

const {
  data: taskResponse,
  pending: tasksPending,
  error: tasksError,
  refresh: refreshTasks
} = useAsyncData(
  () => `campaign-tasks-${campaignId.value}`,
  () =>
    fetchTasks({
      campaignId: campaignId.value
    }),
  {
    server: false,
    watch: [campaignId],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const tasks = computed(() => taskResponse.value.items)

const {
  data: reputation,
  pending: reputationPending,
  error: reputationError,
  refresh: refreshReputation
} = useAsyncData(
  () => `campaign-reputation-${campaignId.value}`,
  () => fetchCampaignReputation(campaignId.value),
  {
    server: false,
    watch: [campaignId],
    default: () => null
  }
)

const hasReputationSignals = computed(() => {
  if (!reputation.value) {
    return false
  }

  return (
    reputation.value.tasks_total_count > 0
    || reputation.value.tasks_closed_count > 0
    || reputation.value.feedback_received_count > 0
    || reputation.value.last_feedback_at !== null
  )
})
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/campaigns">活動列表</NuxtLink>
        <h1 class="resource-shell__title">活動詳情</h1>
        <p class="resource-shell__description">
          這個頁面先承接單一活動的核心欄位，包含所屬專案、版本、平台與活動狀態。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="campaign-detail-loading"
      >
        <h2 class="resource-state__title">載入活動詳情中</h2>
        <p class="resource-state__description">
          正在從 API 載入活動詳情。
        </p>
      </section>

      <section
        v-else-if="error || !campaign"
        class="resource-state"
        data-testid="campaign-detail-error"
      >
        <h2 class="resource-state__title">無法載入活動詳情</h2>
        <p class="resource-state__description">
          {{ error?.message || '找不到指定的活動。' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試
          </button>
          <NuxtLink class="resource-action" to="/campaigns">
            返回活動列表
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="campaign-detail-panel"
      >
        <h2 class="resource-section__title">{{ campaign.name }}</h2>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="campaign-edit-link"
            :to="`/campaigns/${campaign.id}/edit`"
          >
            編輯活動
          </NuxtLink>
        </div>

        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">狀態 {{ formatCampaignStatusLabel(campaign.status) }}</span>
          <span
            v-for="platform in campaign.target_platforms"
            :key="platform"
            class="resource-shell__meta-chip"
          >
            {{ formatPlatformLabel(platform) }}
          </span>
        </div>

        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">活動 ID</span>
            <span class="resource-key-value__value">{{ campaign.id }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">專案 ID</span>
            <NuxtLink
              class="resource-key-value__value"
              :to="`/projects/${campaign.project_id}`"
            >
              {{ campaign.project_id }}
            </NuxtLink>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">版本標記</span>
            <span class="resource-key-value__value">
              {{ campaign.version_label || '目前尚未提供版本標記。' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">更新時間</span>
            <span class="resource-key-value__value">{{ campaign.updated_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">建立時間</span>
            <span class="resource-key-value__value">{{ campaign.created_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">描述</span>
            <span class="resource-key-value__value">
              {{ campaign.description || '目前尚未提供活動描述。' }}
            </span>
          </div>
        </div>
      </section>

      <section
        v-if="!pending && !error && campaign"
        class="resource-section"
        data-testid="campaign-reputation-section"
      >
        <h2 class="resource-section__title">協作摘要</h2>

        <div
          v-if="reputationPending"
          class="resource-state"
          data-testid="campaign-reputation-loading"
        >
          <h3 class="resource-state__title">載入協作摘要中</h3>
          <p class="resource-state__description">
            正在根據任務與回饋推導這個活動的最小協作摘要。
          </p>
        </div>

        <div
          v-else-if="reputationError"
          class="resource-state"
          data-testid="campaign-reputation-error"
        >
          <h3 class="resource-state__title">無法載入協作摘要</h3>
          <p class="resource-state__description">
            {{ reputationError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshReputation()">
              重試
            </button>
          </div>
        </div>

        <div
          v-else-if="reputation && !hasReputationSignals"
          class="resource-state"
          data-testid="campaign-reputation-zero"
        >
          <h3 class="resource-state__title">目前還沒有協作訊號</h3>
          <p class="resource-state__description">
            這個活動還沒有累積任務完成或回饋紀錄，目前摘要維持在零狀態。
          </p>
        </div>

        <div
          v-else-if="reputation"
          class="resource-section"
          data-testid="campaign-reputation-panel"
        >
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              關閉率 {{ reputation.closure_rate.toFixed(2) }}
            </span>
            <span class="resource-shell__meta-chip">
              回饋數 {{ reputation.feedback_received_count }}
            </span>
          </div>

          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">任務總數</span>
              <span class="resource-key-value__value">
                {{ reputation.tasks_total_count }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">已關閉任務數</span>
              <span class="resource-key-value__value">
                {{ reputation.tasks_closed_count }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">收到的回饋數</span>
              <span class="resource-key-value__value">
                {{ reputation.feedback_received_count }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">最近回饋時間</span>
              <span class="resource-key-value__value">
                {{ reputation.last_feedback_at || '目前尚未收到任何回饋。' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">更新時間</span>
              <span class="resource-key-value__value">{{ reputation.updated_at }}</span>
            </div>
          </div>
        </div>
      </section>

      <section
        v-if="!pending && !error && campaign"
        class="resource-section"
        data-testid="campaign-safety-section"
      >
        <h2 class="resource-section__title">安全與來源</h2>

        <div
          v-if="safetyPending"
          class="resource-state"
          data-testid="campaign-safety-loading"
        >
          <h3 class="resource-state__title">載入活動安全資訊中</h3>
          <p class="resource-state__description">
            正在載入這個活動的來源標示與風險資訊。
          </p>
        </div>

        <div
          v-else-if="safetyError"
          class="resource-state"
          data-testid="campaign-safety-error"
        >
          <h3 class="resource-state__title">無法載入活動安全資訊</h3>
          <p class="resource-state__description">
            {{ safetyError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshSafety()">
              重試
            </button>
          </div>
        </div>

        <div
          v-else-if="!safety"
          class="resource-state"
          data-testid="campaign-safety-empty"
        >
          <h3 class="resource-state__title">目前還沒有安全設定</h3>
          <p class="resource-state__description">
            目前這個活動尚未設定來源標示與風險資訊。後續建立安全設定後，這個區塊會直接承接顯示。
          </p>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              data-testid="campaign-safety-create-link"
              :to="`/campaigns/${campaignId}/safety/new`"
            >
              建立安全設定
            </NuxtLink>
          </div>
        </div>

        <div
          v-else
          class="resource-section"
          data-testid="campaign-safety-panel"
        >
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              data-testid="campaign-safety-edit-link"
              :to="`/campaigns/${campaignId}/safety/edit`"
            >
              編輯安全設定
            </NuxtLink>
          </div>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              風險 {{ formatRiskLevelLabel(safety.risk_level) }}
            </span>
            <span class="resource-shell__meta-chip">
              審核 {{ formatReviewStatusLabel(safety.review_status) }}
            </span>
            <span class="resource-shell__meta-chip">
              僅限官方渠道 {{ safety.official_channel_only ? '是' : '否' }}
            </span>
          </div>

          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">來源標示</span>
              <span class="resource-key-value__value">{{ safety.source_label }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">分發渠道</span>
              <span class="resource-key-value__value">
                {{ formatDistributionChannelLabel(safety.distribution_channel) }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">來源網址</span>
              <a
                v-if="safety.source_url"
                class="resource-key-value__value"
                :href="safety.source_url"
                target="_blank"
                rel="noreferrer"
              >
                {{ safety.source_url }}
              </a>
              <span v-else class="resource-key-value__value">
                目前沒有來源網址。
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">風險註記</span>
              <span class="resource-key-value__value">
                {{ safety.risk_note || '目前沒有額外風險註記。' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">更新時間</span>
              <span class="resource-key-value__value">{{ safety.updated_at }}</span>
            </div>
          </div>
        </div>
      </section>

      <section
        v-if="!pending && !error && campaign"
        class="resource-section"
        data-testid="campaign-eligibility-section"
      >
        <h2 class="resource-section__title">資格條件規則</h2>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="eligibility-rule-create-link"
            :to="`/campaigns/${campaignId}/eligibility-rules/new`"
          >
            建立資格條件規則
          </NuxtLink>
        </div>

        <div
          v-if="eligibilityPending"
          class="resource-state"
          data-testid="campaign-eligibility-loading"
        >
          <h3 class="resource-state__title">載入資格條件規則中</h3>
          <p class="resource-state__description">
            正在載入這個活動的最小資格條件規則。
          </p>
        </div>

        <div
          v-else-if="eligibilityError"
          class="resource-state"
          data-testid="campaign-eligibility-error"
        >
          <h3 class="resource-state__title">無法載入資格條件規則</h3>
          <p class="resource-state__description">
            {{ eligibilityError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshEligibility()">
              重試
            </button>
          </div>
        </div>

        <div
          v-else-if="eligibilityRules.length === 0"
          class="resource-state"
          data-testid="campaign-eligibility-empty"
        >
          <h3 class="resource-state__title">目前還沒有資格條件規則</h3>
          <p class="resource-state__description">
            目前這個活動尚未建立任何資格條件規則，後續可在後端建立後由此區塊直接承接。
          </p>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              data-testid="eligibility-rule-empty-create-link"
              :to="`/campaigns/${campaignId}/eligibility-rules/new`"
            >
              建立第一筆資格條件規則
            </NuxtLink>
          </div>
        </div>

        <div
          v-else
          class="resource-section__body"
          data-testid="campaign-eligibility-list"
        >
          <NuxtLink
            v-for="eligibilityRule in eligibilityRules"
            :key="eligibilityRule.id"
            class="resource-card"
            :data-testid="`eligibility-rule-card-${eligibilityRule.id}`"
            :to="`/campaigns/${campaign.id}/eligibility-rules/${eligibilityRule.id}`"
          >
            <span class="resource-shell__breadcrumb">資格條件規則</span>
            <h3 class="resource-card__title">
              {{ formatPlatformLabel(eligibilityRule.platform) }}
            </h3>
            <p class="resource-card__description">
              {{
                eligibilityRule.os_name
                  ? `作業系統 ${eligibilityRule.os_name}`
                  : '目前尚未限制作業系統。'
              }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">
                啟用中 {{ eligibilityRule.is_active ? '是' : '否' }}
              </span>
              <span class="resource-card__chip">
                {{
                  eligibilityRule.install_channel
                    ? `渠道 ${eligibilityRule.install_channel}`
                    : '目前尚未限制安裝渠道'
                }}
              </span>
            </div>
          </NuxtLink>
        </div>
      </section>

      <section
        v-if="!pending && !error && campaign"
        class="resource-section"
        data-testid="campaign-tasks-section"
      >
        <h2 class="resource-section__title">任務</h2>

        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="campaign-task-create-link"
            :to="`/campaigns/${campaign.id}/tasks/new`"
          >
            為此活動建立任務
          </NuxtLink>
          <NuxtLink
            class="resource-action"
            data-testid="campaign-tasks-link"
            :to="`/tasks?campaign_id=${campaign.id}`"
          >
            查看此活動的所有任務
          </NuxtLink>
        </div>

        <div
          v-if="tasksPending"
          class="resource-state"
          data-testid="campaign-tasks-loading"
        >
          <h3 class="resource-state__title">載入任務中</h3>
          <p class="resource-state__description">
            正在載入這個活動底下的任務列表。
          </p>
        </div>

        <div
          v-else-if="tasksError"
          class="resource-state"
          data-testid="campaign-tasks-error"
        >
          <h3 class="resource-state__title">無法載入任務</h3>
          <p class="resource-state__description">
            {{ tasksError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshTasks()">
              重試
            </button>
          </div>
        </div>

        <div
          v-else-if="tasks.length === 0"
          class="resource-state"
          data-testid="campaign-tasks-empty"
        >
          <h3 class="resource-state__title">目前還沒有任務</h3>
          <p class="resource-state__description">
            目前這個活動尚未建立任何任務，後續可在後端建立後由此區塊直接承接。
          </p>
        </div>

        <div
          v-else
          class="resource-section__body"
          data-testid="campaign-tasks-list"
        >
          <NuxtLink
            v-for="task in tasks"
            :key="task.id"
            class="resource-card"
            :data-testid="`campaign-task-card-${task.id}`"
            :to="`/tasks/${task.id}`"
          >
            <span class="resource-shell__breadcrumb">任務</span>
            <h3 class="resource-card__title">{{ task.title }}</h3>
            <p class="resource-card__description">
              {{
                task.device_profile_id
                  ? `已指派給 ${task.device_profile_id}`
                  : '目前尚未指派裝置設定檔。'
              }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">狀態 {{ formatTaskStatusLabel(task.status) }}</span>
              <span class="resource-card__chip">更新於 {{ task.updated_at }}</span>
            </div>
          </NuxtLink>
        </div>
      </section>

      <NuxtPage />
    </section>
  </main>
</template>
