<script setup lang="ts">
import { computed, ref } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
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
import { useAppI18n } from '~/features/i18n/use-app-i18n'

useCurrentActorPersistence()

const { locale, t } = useAppI18n()
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
      <header class="resource-shell__header app-page-header">
        <NuxtLink class="resource-shell__breadcrumb" to="/dashboard">Dashboard</NuxtLink>
        <h1 class="resource-shell__title">{{ t('reviewFeedback.title') }}</h1>
        <p class="resource-shell__description">
          {{ t('reviewFeedback.description') }}
        </p>
      </header>
      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="feedback-review-actor-error"
      >
        <h2 class="resource-state__title">{{ t('reviewFeedback.actorErrorTitle') }}</h2>
        <p class="resource-state__description">
          {{ accountsError.message }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshAccounts()">
            {{ t('common.retry') }}
          </button>
        </div>
      </section>

      <section
        v-else-if="accountsPending"
        class="resource-state"
        data-testid="feedback-review-actor-loading"
      >
        <h2 class="resource-state__title">{{ t('reviewFeedback.actorLoadingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('reviewFeedback.actorLoadingDescription') }}
        </p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="feedback-review-select-actor"
      >
        <h2 class="resource-state__title">{{ t('reviewFeedback.selectActorTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('reviewFeedback.selectActorDescription') }}
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="feedback-review-actor-missing"
      >
        <h2 class="resource-state__title">{{ t('reviewFeedback.actorMissingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('reviewFeedback.actorMissingDescription') }}
        </p>
      </section>

      <section
        v-else-if="!isDeveloperActor"
        class="resource-state"
        data-testid="feedback-review-role-mismatch"
      >
        <h2 class="resource-state__title">{{ t('reviewFeedback.roleMismatchTitle') }}</h2>
        <p class="resource-state__description">
          {{
            t('reviewFeedback.roleMismatchDescription', {
              role: formatAccountRoleLabel(currentActor.role, locale)
            })
          }}
        </p>
      </section>

      <template v-else>
        <section class="resource-section" data-testid="feedback-review-filters">
          <h2 class="resource-section__title">{{ t('reviewFeedback.filtersTitle') }}</h2>
          <div class="resource-state__actions app-page-actions">
            <button
              v-for="statusOption in FEEDBACK_REVIEW_STATUS_OPTIONS"
              :key="statusOption"
              class="resource-action"
              :data-testid="`feedback-review-filter-${statusOption}`"
              type="button"
              @click="activeReviewStatus = statusOption"
            >
              {{ formatFeedbackReviewStatusLabel(statusOption, locale) }}
            </button>
          </div>
          <div class="app-page-summary-grid">
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">{{ t('reviewFeedback.currentAccount') }}</span>
              <strong class="app-page-summary-card__value">{{ currentActor.display_name }}</strong>
              <span class="app-page-summary-card__description">{{ t('reviewFeedback.currentAccountDescription') }}</span>
            </article>
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">{{ t('reviewFeedback.reviewLabel') }}</span>
              <strong class="app-page-summary-card__value">{{ formatFeedbackReviewStatusLabel(activeReviewStatus, locale) }}</strong>
              <span class="app-page-summary-card__description">{{ t('reviewFeedback.reviewDescription') }}</span>
            </article>
          </div>
        </section>

        <section
          v-if="queuePending"
          class="resource-state"
          data-testid="feedback-review-loading"
        >
          <h2 class="resource-state__title">{{ t('reviewFeedback.loadingTitle') }}</h2>
          <p class="resource-state__description">
            {{ t('reviewFeedback.loadingDescription') }}
          </p>
        </section>

        <section
          v-else-if="queueError"
          class="resource-state"
          data-testid="feedback-review-error"
        >
          <h2 class="resource-state__title">{{ t('reviewFeedback.errorTitle') }}</h2>
          <p class="resource-state__description">
            {{
              getActorAwareReadErrorMessage(
                queueError,
                t('reviewFeedback.errorTitle')
              )
            }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshQueue()">
              {{ t('common.retry') }}
            </button>
          </div>
        </section>

        <section
          v-else-if="feedbackItems.length === 0"
          class="resource-state"
          data-testid="feedback-review-empty"
        >
          <h2 class="resource-state__title">{{ t('reviewFeedback.emptyTitle') }}</h2>
          <p class="resource-state__description">
            {{ t('reviewFeedback.emptyDescription', { status: formatFeedbackReviewStatusLabel(activeReviewStatus, locale) }) }}
          </p>
        </section>

        <section
          v-else
          class="resource-section__body app-page-card-grid"
          data-testid="feedback-review-list"
        >
          <article
            v-for="feedback in feedbackItems"
            :key="feedback.id"
            class="resource-card"
            :data-testid="`review-feedback-card-${feedback.id}`"
          >
            <span class="resource-shell__breadcrumb">{{ t('reviewFeedback.breadcrumb') }}</span>
            <h2 class="resource-card__title">{{ feedback.summary }}</h2>
            <p class="resource-card__description">
              {{ t('reviewFeedback.taskCampaignSummary', { taskId: feedback.task_id, campaignId: feedback.campaign_id }) }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">
                {{ t('reviewFeedback.reviewLabel') }} {{ formatFeedbackReviewStatusLabel(feedback.review_status, locale) }}
              </span>
              <span class="resource-card__chip">{{ t('reviewFeedback.severityLabel') }} {{ formatFeedbackSeverityLabel(feedback.severity, locale) }}</span>
              <span class="resource-card__chip">{{ t('reviewFeedback.categoryLabel') }} {{ formatFeedbackCategoryLabel(feedback.category, locale) }}</span>
              <span class="resource-card__chip">{{ t('reviewFeedback.submittedAtLabel') }} {{ feedback.submitted_at }}</span>
            </div>
            <div class="resource-state__actions">
              <NuxtLink
                class="resource-action"
                :data-testid="`review-feedback-link-${feedback.id}`"
                :to="`/tasks/${feedback.task_id}/feedback/${feedback.id}`"
              >
                {{ t('reviewFeedback.openFeedbackDetail') }}
              </NuxtLink>
            </div>
          </article>
        </section>
      </template>
    </section>
  </main>
</template>
