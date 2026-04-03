<script setup lang="ts">
import { computed } from 'vue'

import { fetchCampaignDetail } from '~/features/campaigns/api'
import { fetchCampaignEligibilityRules } from '~/features/eligibility/api'
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
            {{ platform }}
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
        data-testid="campaign-eligibility-section"
      >
        <h2 class="resource-section__title">Eligibility Rules</h2>

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
            <h3 class="resource-card__title">{{ eligibilityRule.platform }}</h3>
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
