<script setup lang="ts">
import { computed } from 'vue'

import { fetchAccountDetail, fetchAccountSummary } from '~/features/accounts/api'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import { formatCampaignStatusLabel } from '~/features/campaigns/types'
import { formatFeedbackReviewStatusLabel } from '~/features/feedback/types'
import { formatPlatformLabel } from '~/features/platform-display'
import { formatTaskStatusLabel } from '~/features/tasks/types'

const route = useRoute()
const accountId = computed(() => String(route.params.accountId))

const {
  data: account,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `account-detail-${accountId.value}`,
  () => fetchAccountDetail(accountId.value),
  {
    server: false,
    watch: [accountId],
    default: () => null
  }
)

const {
  data: accountSummary,
  pending: summaryPending,
  error: summaryError,
  refresh: refreshSummary
} = useAsyncData(
  () => `account-summary-${accountId.value}`,
  () => fetchAccountSummary(accountId.value),
  {
    server: false,
    watch: [accountId],
    default: () => null
  }
)

const developerSummary = computed(() => accountSummary.value?.developer_summary ?? null)
const testerSummary = computed(() => accountSummary.value?.tester_summary ?? null)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/accounts">帳號列表</NuxtLink>
        <h1 class="resource-shell__title">帳號詳情</h1>
        <p class="resource-shell__description">
          這個頁面顯示單一帳號的最小資料，用來支撐下一階段的擁有權、目前操作帳號與依角色協作流程。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="account-detail-loading"
      >
        <h2 class="resource-state__title">正在載入帳號詳情</h2>
        <p class="resource-state__description">
          正在從 API 載入帳號詳情。
        </p>
      </section>

      <section
        v-else-if="error || !account"
        class="resource-state"
        data-testid="account-detail-error"
      >
        <h2 class="resource-state__title">帳號詳情暫時無法使用</h2>
        <p class="resource-state__description">
          {{ error?.message || '無法載入指定的帳號。' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試
          </button>
          <NuxtLink class="resource-action" to="/accounts">
            返回帳號列表
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="account-detail-panel"
      >
        <h2 class="resource-section__title">{{ account.display_name }}</h2>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="account-edit-link"
            :to="`/accounts/${account.id}/edit`"
          >
            編輯帳號
          </NuxtLink>
        </div>
        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            {{ formatAccountRoleLabel(account.role) }}
          </span>
        </div>
        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">帳號 ID</span>
            <span class="resource-key-value__value">{{ account.id }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">更新時間</span>
            <span class="resource-key-value__value">{{ account.updated_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">建立時間</span>
            <span class="resource-key-value__value">{{ account.created_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">語系</span>
            <span class="resource-key-value__value">
              {{ account.locale || '尚未提供。' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">簡介</span>
            <span class="resource-key-value__value">
              {{ account.bio || '尚未提供。' }}
            </span>
          </div>
        </div>
      </section>

      <section
        v-if="summaryPending"
        class="resource-state"
        data-testid="account-summary-loading"
      >
        <h2 class="resource-state__title">正在載入協作摘要</h2>
        <p class="resource-state__description">
          正在彙整這個帳號的 owned resources 與 collaboration footprint。
        </p>
      </section>

      <section
        v-else-if="summaryError || !accountSummary"
        class="resource-state"
        data-testid="account-summary-error"
      >
        <h2 class="resource-state__title">協作摘要暫時無法使用</h2>
        <p class="resource-state__description">
          {{ summaryError?.message || '目前無法載入帳號協作摘要。' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshSummary()">
            重試
          </button>
        </div>
      </section>

      <section
        v-else-if="developerSummary"
        class="resource-section"
        data-testid="account-summary-developer-panel"
      >
        <h2 class="resource-section__title">開發者協作摘要</h2>
        <div class="resource-state__actions">
          <NuxtLink class="resource-action" to="/my/projects">
            查看我的專案
          </NuxtLink>
          <NuxtLink class="resource-action" to="/my/campaigns">
            查看我的活動
          </NuxtLink>
        </div>
        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">擁有專案數</span>
            <span class="resource-key-value__value">
              {{ developerSummary.owned_projects_count }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">擁有活動數</span>
            <span class="resource-key-value__value">
              {{ developerSummary.owned_campaigns_count }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">待審閱回饋數</span>
            <span class="resource-key-value__value">
              {{ developerSummary.feedback_to_review_count }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">摘要更新時間</span>
            <span class="resource-key-value__value">
              {{ accountSummary.updated_at }}
            </span>
          </div>
        </div>

        <section
          v-if="
            developerSummary.recent_projects.length === 0 &&
            developerSummary.recent_campaigns.length === 0
          "
          class="resource-state"
          data-testid="account-summary-developer-empty"
        >
          <h3 class="resource-state__title">尚無 owned resources</h3>
          <p class="resource-state__description">
            這個開發者帳號目前還沒有擁有任何專案或活動。
          </p>
        </section>

        <template v-else>
          <div
            v-if="developerSummary.recent_projects.length > 0"
            class="resource-shell__grid"
            data-testid="account-recent-projects"
          >
            <NuxtLink
              v-for="project in developerSummary.recent_projects"
              :key="project.id"
              class="resource-card"
              :data-testid="`account-summary-project-${project.id}`"
              :to="`/projects/${project.id}`"
            >
              <span class="resource-shell__breadcrumb">最近專案</span>
              <h3 class="resource-card__title">{{ project.name }}</h3>
              <div class="resource-card__meta">
                <span class="resource-card__chip">Project {{ project.id }}</span>
              </div>
              <p class="resource-card__description">
                更新時間 {{ project.updated_at }}
              </p>
            </NuxtLink>
          </div>

          <div
            v-if="developerSummary.recent_campaigns.length > 0"
            class="resource-shell__grid"
            data-testid="account-recent-campaigns"
          >
            <NuxtLink
              v-for="campaign in developerSummary.recent_campaigns"
              :key="campaign.id"
              class="resource-card"
              :data-testid="`account-summary-campaign-${campaign.id}`"
                :to="`/campaigns/${campaign.id}`"
            >
              <span class="resource-shell__breadcrumb">最近活動</span>
              <h3 class="resource-card__title">{{ campaign.name }}</h3>
              <div class="resource-card__meta">
                <span class="resource-card__chip">
                  {{ formatCampaignStatusLabel(campaign.status) }}
                </span>
                <span class="resource-card__chip">Project {{ campaign.project_id }}</span>
              </div>
              <p class="resource-card__description">
                更新時間 {{ campaign.updated_at }}
              </p>
            </NuxtLink>
          </div>
        </template>
      </section>

      <section
        v-else-if="testerSummary"
        class="resource-section"
        data-testid="account-summary-tester-panel"
      >
        <h2 class="resource-section__title">測試者協作摘要</h2>
        <div class="resource-state__actions">
          <NuxtLink class="resource-action" to="/device-profiles">
            查看測試裝置
          </NuxtLink>
          <NuxtLink class="resource-action" to="/my/tasks">
            查看我的任務
          </NuxtLink>
        </div>
        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">擁有裝置數</span>
            <span class="resource-key-value__value">
              {{ testerSummary.owned_device_profiles_count }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">指派任務數</span>
            <span class="resource-key-value__value">
              {{ testerSummary.assigned_tasks_count }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">已提交回饋數</span>
            <span class="resource-key-value__value">
              {{ testerSummary.submitted_feedback_count }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">摘要更新時間</span>
            <span class="resource-key-value__value">
              {{ accountSummary.updated_at }}
            </span>
          </div>
        </div>

        <section
          v-if="
            testerSummary.recent_device_profiles.length === 0 &&
            testerSummary.recent_tasks.length === 0 &&
            testerSummary.recent_feedback.length === 0
          "
          class="resource-state"
          data-testid="account-summary-tester-empty"
        >
          <h3 class="resource-state__title">尚無 collaboration footprint</h3>
          <p class="resource-state__description">
            這個測試者帳號目前還沒有擁有任何裝置、任務或回饋。
          </p>
        </section>

        <template v-else>
          <div
            v-if="testerSummary.recent_device_profiles.length > 0"
            class="resource-shell__grid"
            data-testid="account-recent-device-profiles"
          >
            <NuxtLink
              v-for="deviceProfile in testerSummary.recent_device_profiles"
              :key="deviceProfile.id"
              class="resource-card"
              :data-testid="`account-summary-device-profile-${deviceProfile.id}`"
              :to="`/device-profiles/${deviceProfile.id}`"
            >
              <span class="resource-shell__breadcrumb">最近裝置</span>
              <h3 class="resource-card__title">{{ deviceProfile.name }}</h3>
              <div class="resource-card__meta">
                <span class="resource-card__chip">
                  {{ formatPlatformLabel(deviceProfile.platform) }}
                </span>
              </div>
              <p class="resource-card__description">
                更新時間 {{ deviceProfile.updated_at }}
              </p>
            </NuxtLink>
          </div>

          <div
            v-if="testerSummary.recent_tasks.length > 0"
            class="resource-shell__grid"
            data-testid="account-recent-tasks"
          >
            <NuxtLink
              v-for="task in testerSummary.recent_tasks"
              :key="task.id"
              class="resource-card"
              :data-testid="`account-summary-task-${task.id}`"
              :to="`/tasks/${task.id}`"
            >
              <span class="resource-shell__breadcrumb">最近任務</span>
              <h3 class="resource-card__title">{{ task.title }}</h3>
              <div class="resource-card__meta">
                <span class="resource-card__chip">
                  {{ formatTaskStatusLabel(task.status) }}
                </span>
                <span class="resource-card__chip">Campaign {{ task.campaign_id }}</span>
              </div>
              <p class="resource-card__description">
                更新時間 {{ task.updated_at }}
              </p>
            </NuxtLink>
          </div>

          <div
            v-if="testerSummary.recent_feedback.length > 0"
            class="resource-shell__grid"
            data-testid="account-recent-feedback"
          >
            <NuxtLink
              v-for="feedback in testerSummary.recent_feedback"
              :key="feedback.id"
              class="resource-card"
              :data-testid="`account-summary-feedback-${feedback.id}`"
              :to="`/tasks/${feedback.task_id}/feedback/${feedback.id}`"
            >
              <span class="resource-shell__breadcrumb">最近回饋</span>
              <h3 class="resource-card__title">{{ feedback.summary }}</h3>
              <div class="resource-card__meta">
                <span class="resource-card__chip">
                  {{ formatFeedbackReviewStatusLabel(feedback.review_status) }}
                </span>
                <span class="resource-card__chip">Task {{ feedback.task_id }}</span>
              </div>
              <p class="resource-card__description">
                提交時間 {{ feedback.submitted_at }}
              </p>
            </NuxtLink>
          </div>
        </template>
      </section>
    </section>
  </main>
</template>
