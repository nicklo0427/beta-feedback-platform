<script setup lang="ts">
import { computed, ref } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  getActorAwareReadErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import { fetchFeedbackQueue } from '~/features/feedback/api'
import {
  FEEDBACK_REVIEW_STATUS_OPTIONS,
  formatFeedbackCategoryLabel,
  formatFeedbackReviewStatusLabel,
  formatFeedbackSeverityLabel,
  type FeedbackReviewStatus
} from '~/features/feedback/types'

useCurrentActorPersistence()

const currentActorId = useCurrentActorId()
const activeReviewStatus = ref<FeedbackReviewStatus>('submitted')

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('review-feedback-accounts', () => fetchAccounts(), {
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
  data: feedbackResponse,
  pending: queuePending,
  error: queueError,
  refresh: refreshQueue
} = useAsyncData(
  () =>
    `review-feedback-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}-${activeReviewStatus.value}`,
  async () => {
    if (!currentActorId.value || !isDeveloperActor.value) {
      return {
        items: [],
        total: 0
      }
    }

    return fetchFeedbackQueue({
      mine: true,
      actorId: currentActorId.value,
      reviewStatus: activeReviewStatus.value
    })
  },
  {
    server: false,
    watch: [currentActorId, currentActor, activeReviewStatus],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const feedbackItems = computed(() => feedbackResponse.value.items)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/">首頁</NuxtLink>
        <h1 class="resource-shell__title">回饋審閱佇列</h1>
        <p class="resource-shell__description">
          這個頁面提供開發者端的最小回饋審閱佇列，讓你可以依審閱狀態篩選屬於自己專案 / 活動的回饋，並快速進入詳情進行審閱。
        </p>
      </header>

      <CurrentActorSelector
        title="開發者情境"
        description="選擇目前正在操作的開發者帳號，佇列會依它擁有的 projects / campaigns 推導可審閱的回饋。"
      />

      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="feedback-review-actor-error"
      >
        <h2 class="resource-state__title">無法取得操作情境</h2>
        <p class="resource-state__description">
          {{ accountsError.message }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshAccounts()">
            重試
          </button>
        </div>
      </section>

      <section
        v-else-if="accountsPending"
        class="resource-state"
        data-testid="feedback-review-actor-loading"
      >
        <h2 class="resource-state__title">載入開發者情境中</h2>
        <p class="resource-state__description">
          正在確認目前操作帳號與可用的開發者情境。
        </p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="feedback-review-select-actor"
      >
        <h2 class="resource-state__title">請選擇開發者帳號</h2>
        <p class="resource-state__description">
          先選擇目前操作帳號，系統才知道要推導哪一位開發者的回饋審閱佇列。
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="feedback-review-actor-missing"
      >
        <h2 class="resource-state__title">找不到已選擇的帳號</h2>
        <p class="resource-state__description">
          目前找不到你選擇的帳號，請重新選擇一筆可用的開發者帳號。
        </p>
      </section>

      <section
        v-else-if="!isDeveloperActor"
        class="resource-state"
        data-testid="feedback-review-role-mismatch"
      >
        <h2 class="resource-state__title">回饋審閱需要開發者帳號</h2>
        <p class="resource-state__description">
          目前選到的是{{ formatAccountRoleLabel(currentActor.role) }}帳號。請切換到開發者帳號，再查看回饋審閱佇列。
        </p>
      </section>

      <template v-else>
        <section class="resource-section" data-testid="feedback-review-filters">
          <h2 class="resource-section__title">審閱狀態篩選</h2>
          <div class="resource-state__actions">
            <button
              v-for="statusOption in FEEDBACK_REVIEW_STATUS_OPTIONS"
              :key="statusOption"
              class="resource-action"
              :data-testid="`feedback-review-filter-${statusOption}`"
              type="button"
              @click="activeReviewStatus = statusOption"
            >
              {{ formatFeedbackReviewStatusLabel(statusOption) }}
            </button>
          </div>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              目前帳號 {{ currentActor.display_name }}
            </span>
            <span class="resource-shell__meta-chip">
              審閱 {{ formatFeedbackReviewStatusLabel(activeReviewStatus) }}
            </span>
          </div>
        </section>

        <section
          v-if="queuePending"
          class="resource-state"
          data-testid="feedback-review-loading"
        >
          <h2 class="resource-state__title">載入審閱佇列中</h2>
          <p class="resource-state__description">
            正在根據目前操作帳號與其擁有的專案 / 活動推導回饋審閱佇列。
          </p>
        </section>

        <section
          v-else-if="queueError"
          class="resource-state"
          data-testid="feedback-review-error"
        >
          <h2 class="resource-state__title">無法載入回饋審閱佇列</h2>
          <p class="resource-state__description">
            {{
              getActorAwareReadErrorMessage(
                queueError,
                '目前無法載入回饋審閱佇列。'
              )
            }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshQueue()">
              重試
            </button>
          </div>
        </section>

        <section
          v-else-if="feedbackItems.length === 0"
          class="resource-state"
          data-testid="feedback-review-empty"
        >
          <h2 class="resource-state__title">這個審閱狀態下沒有回饋</h2>
          <p class="resource-state__description">
            目前這位開發者在 {{ formatFeedbackReviewStatusLabel(activeReviewStatus) }} 狀態下沒有任何回饋。
          </p>
        </section>

        <section
          v-else
          class="resource-section__body"
          data-testid="feedback-review-list"
        >
          <article
            v-for="feedback in feedbackItems"
            :key="feedback.id"
            class="resource-card"
            :data-testid="`review-feedback-card-${feedback.id}`"
          >
            <span class="resource-shell__breadcrumb">回饋審閱</span>
            <h2 class="resource-card__title">{{ feedback.summary }}</h2>
            <p class="resource-card__description">
              任務 {{ feedback.task_id }} · 活動 {{ feedback.campaign_id }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">
                審閱 {{ formatFeedbackReviewStatusLabel(feedback.review_status) }}
              </span>
              <span class="resource-card__chip">嚴重程度 {{ formatFeedbackSeverityLabel(feedback.severity) }}</span>
              <span class="resource-card__chip">分類 {{ formatFeedbackCategoryLabel(feedback.category) }}</span>
              <span class="resource-card__chip">提交於 {{ feedback.submitted_at }}</span>
            </div>
            <div class="resource-state__actions">
              <NuxtLink
                class="resource-action"
                :data-testid="`review-feedback-link-${feedback.id}`"
                :to="`/tasks/${feedback.task_id}/feedback/${feedback.id}`"
              >
                開啟回饋詳情
              </NuxtLink>
            </div>
          </article>
        </section>
      </template>
    </section>
  </main>
</template>
