<script setup lang="ts">
import { computed } from 'vue'

import { fetchCampaignDetail } from '~/features/campaigns/api'
import { fetchCampaignEligibilityRules } from '~/features/eligibility/api'
import { formatPlatformLabel } from '~/features/platform-display'
import { fetchCampaignReputation } from '~/features/reputation/api'
import { fetchCampaignSafety } from '~/features/safety/api'
import { fetchTasks } from '~/features/tasks/api'

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
        <NuxtLink class="resource-shell__breadcrumb" to="/campaigns">Campaigns</NuxtLink>
        <h1 class="resource-shell__title">Campaign Detail Shell</h1>
        <p class="resource-shell__description">
          這個頁面先承接單一 Campaign 的核心欄位，包含所屬 Project、版本、平台與活動狀態。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="campaign-detail-loading"
      >
        <h2 class="resource-state__title">Loading campaign detail</h2>
        <p class="resource-state__description">
          正在從 API 載入 Campaign detail。
        </p>
      </section>

      <section
        v-else-if="error || !campaign"
        class="resource-state"
        data-testid="campaign-detail-error"
      >
        <h2 class="resource-state__title">Campaign detail unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The requested campaign could not be loaded.' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            Retry
          </button>
          <NuxtLink class="resource-action" to="/campaigns">
            Back to campaigns
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="campaign-detail-panel"
      >
        <h2 class="resource-section__title">{{ campaign.name }}</h2>

        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">Status {{ campaign.status }}</span>
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
            <span class="resource-key-value__label">Campaign ID</span>
            <span class="resource-key-value__value">{{ campaign.id }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Project ID</span>
            <NuxtLink
              class="resource-key-value__value"
              :to="`/projects/${campaign.project_id}`"
            >
              {{ campaign.project_id }}
            </NuxtLink>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Version Label</span>
            <span class="resource-key-value__value">
              {{ campaign.version_label || 'No version label yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Updated At</span>
            <span class="resource-key-value__value">{{ campaign.updated_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Created At</span>
            <span class="resource-key-value__value">{{ campaign.created_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Description</span>
            <span class="resource-key-value__value">
              {{ campaign.description || 'No campaign description provided yet.' }}
            </span>
          </div>
        </div>
      </section>

      <section
        v-if="!pending && !error && campaign"
        class="resource-section"
        data-testid="campaign-reputation-section"
      >
        <h2 class="resource-section__title">Collaboration Summary</h2>

        <div
          v-if="reputationPending"
          class="resource-state"
          data-testid="campaign-reputation-loading"
        >
          <h3 class="resource-state__title">Loading collaboration summary</h3>
          <p class="resource-state__description">
            正在根據 tasks 與 feedback 推導這個 campaign 的最小 collaboration summary。
          </p>
        </div>

        <div
          v-else-if="reputationError"
          class="resource-state"
          data-testid="campaign-reputation-error"
        >
          <h3 class="resource-state__title">Collaboration summary unavailable</h3>
          <p class="resource-state__description">
            {{ reputationError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshReputation()">
              Retry
            </button>
          </div>
        </div>

        <div
          v-else-if="reputation && !hasReputationSignals"
          class="resource-state"
          data-testid="campaign-reputation-zero"
        >
          <h3 class="resource-state__title">No collaboration signals yet</h3>
          <p class="resource-state__description">
            這個 campaign 還沒有累積 task completion 或 feedback 紀錄，目前 summary 維持在 zero state。
          </p>
        </div>

        <div
          v-else-if="reputation"
          class="resource-section"
          data-testid="campaign-reputation-panel"
        >
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              Closure rate {{ reputation.closure_rate.toFixed(2) }}
            </span>
            <span class="resource-shell__meta-chip">
              Feedback {{ reputation.feedback_received_count }}
            </span>
          </div>

          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Tasks Total</span>
              <span class="resource-key-value__value">
                {{ reputation.tasks_total_count }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Tasks Closed</span>
              <span class="resource-key-value__value">
                {{ reputation.tasks_closed_count }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Feedback Received</span>
              <span class="resource-key-value__value">
                {{ reputation.feedback_received_count }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Last Feedback At</span>
              <span class="resource-key-value__value">
                {{ reputation.last_feedback_at || 'No feedback received yet.' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Updated At</span>
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
        <h2 class="resource-section__title">Safety and Source</h2>

        <div
          v-if="safetyPending"
          class="resource-state"
          data-testid="campaign-safety-loading"
        >
          <h3 class="resource-state__title">Loading campaign safety</h3>
          <p class="resource-state__description">
            正在載入這個 Campaign 的來源標示與風險資訊。
          </p>
        </div>

        <div
          v-else-if="safetyError"
          class="resource-state"
          data-testid="campaign-safety-error"
        >
          <h3 class="resource-state__title">Campaign safety unavailable</h3>
          <p class="resource-state__description">
            {{ safetyError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshSafety()">
              Retry
            </button>
          </div>
        </div>

        <div
          v-else-if="!safety"
          class="resource-state"
          data-testid="campaign-safety-empty"
        >
          <h3 class="resource-state__title">No safety profile yet</h3>
          <p class="resource-state__description">
            目前這個 Campaign 尚未設定來源標示與風險資訊。後續建立 safety profile 後，這個區塊會直接承接顯示。
          </p>
        </div>

        <div
          v-else
          class="resource-section"
          data-testid="campaign-safety-panel"
        >
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              Risk {{ safety.risk_level }}
            </span>
            <span class="resource-shell__meta-chip">
              Review {{ safety.review_status }}
            </span>
            <span class="resource-shell__meta-chip">
              Official channel only {{ safety.official_channel_only ? 'yes' : 'no' }}
            </span>
          </div>

          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Source Label</span>
              <span class="resource-key-value__value">{{ safety.source_label }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Distribution Channel</span>
              <span class="resource-key-value__value">{{ safety.distribution_channel }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Source URL</span>
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
                No source URL provided.
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Risk Note</span>
              <span class="resource-key-value__value">
                {{ safety.risk_note || 'No additional risk note.' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Updated At</span>
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
        <h2 class="resource-section__title">Eligibility Rules</h2>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="eligibility-rule-create-link"
            :to="`/campaigns/${campaignId}/eligibility-rules/new`"
          >
            Create eligibility rule
          </NuxtLink>
        </div>

        <div
          v-if="eligibilityPending"
          class="resource-state"
          data-testid="campaign-eligibility-loading"
        >
          <h3 class="resource-state__title">Loading eligibility rules</h3>
          <p class="resource-state__description">
            正在載入這個 Campaign 的最小資格條件規則。
          </p>
        </div>

        <div
          v-else-if="eligibilityError"
          class="resource-state"
          data-testid="campaign-eligibility-error"
        >
          <h3 class="resource-state__title">Eligibility rules unavailable</h3>
          <p class="resource-state__description">
            {{ eligibilityError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshEligibility()">
              Retry
            </button>
          </div>
        </div>

        <div
          v-else-if="eligibilityRules.length === 0"
          class="resource-state"
          data-testid="campaign-eligibility-empty"
        >
          <h3 class="resource-state__title">No eligibility rules yet</h3>
          <p class="resource-state__description">
            目前這個 Campaign 尚未建立任何 eligibility rules，後續可在 backend 建立後由此區塊直接承接。
          </p>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              data-testid="eligibility-rule-empty-create-link"
              :to="`/campaigns/${campaignId}/eligibility-rules/new`"
            >
              Create the first eligibility rule
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
            <span class="resource-shell__breadcrumb">Eligibility Rule</span>
            <h3 class="resource-card__title">
              {{ formatPlatformLabel(eligibilityRule.platform) }}
            </h3>
            <p class="resource-card__description">
              {{
                eligibilityRule.os_name
                  ? `OS ${eligibilityRule.os_name}`
                  : 'No OS restriction yet.'
              }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">
                Active {{ eligibilityRule.is_active ? 'yes' : 'no' }}
              </span>
              <span class="resource-card__chip">
                {{
                  eligibilityRule.install_channel
                    ? `Channel ${eligibilityRule.install_channel}`
                    : 'No install channel restriction'
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
        <h2 class="resource-section__title">Tasks</h2>

        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="campaign-task-create-link"
            :to="`/campaigns/${campaign.id}/tasks/new`"
          >
            Create task for this campaign
          </NuxtLink>
          <NuxtLink
            class="resource-action"
            data-testid="campaign-tasks-link"
            :to="`/tasks?campaign_id=${campaign.id}`"
          >
            View all tasks for this campaign
          </NuxtLink>
        </div>

        <div
          v-if="tasksPending"
          class="resource-state"
          data-testid="campaign-tasks-loading"
        >
          <h3 class="resource-state__title">Loading tasks</h3>
          <p class="resource-state__description">
            正在載入這個 Campaign 底下的 Task list。
          </p>
        </div>

        <div
          v-else-if="tasksError"
          class="resource-state"
          data-testid="campaign-tasks-error"
        >
          <h3 class="resource-state__title">Tasks unavailable</h3>
          <p class="resource-state__description">
            {{ tasksError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshTasks()">
              Retry
            </button>
          </div>
        </div>

        <div
          v-else-if="tasks.length === 0"
          class="resource-state"
          data-testid="campaign-tasks-empty"
        >
          <h3 class="resource-state__title">No tasks yet</h3>
          <p class="resource-state__description">
            目前這個 Campaign 尚未建立任何 Task，後續可在 backend 建立後由此區塊直接承接。
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
            <span class="resource-shell__breadcrumb">Task</span>
            <h3 class="resource-card__title">{{ task.title }}</h3>
            <p class="resource-card__description">
              {{
                task.device_profile_id
                  ? `Assigned to ${task.device_profile_id}`
                  : 'No device profile assigned yet.'
              }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">Status {{ task.status }}</span>
              <span class="resource-card__chip">Updated {{ task.updated_at }}</span>
            </div>
          </NuxtLink>
        </div>
      </section>

      <NuxtPage />
    </section>
  </main>
</template>
