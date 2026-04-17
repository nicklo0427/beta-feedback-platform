<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import ActivityTimelinePanel from '~/features/activity-events/ActivityTimelinePanel.vue'
import { fetchFeedbackTimeline } from '~/features/activity-events/api'
import {
  getActorAwareReadErrorMessage,
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { fetchFeedbackDetail, updateFeedback } from '~/features/feedback/api'
import {
  FEEDBACK_REVIEW_STATUS_OPTIONS,
  formatFeedbackCategoryLabel,
  formatFeedbackReviewStatusLabel,
  formatFeedbackSeverityLabel,
  type FeedbackReviewStatus
} from '~/features/feedback/types'
import { useAppI18n } from '~/features/i18n/use-app-i18n'

const route = useRoute()
useCurrentActorPersistence()
const { locale, t } = useAppI18n()

const taskId = computed(() => String(route.params.taskId))
const feedbackId = computed(() => String(route.params.feedbackId))
const currentActorId = useCurrentActorId()

const {
  data: feedback,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `feedback-detail-${feedbackId.value}-${currentActorId.value ?? 'none'}`,
  async () => {
    if (!currentActorId.value) {
      return null
    }

    return fetchFeedbackDetail(feedbackId.value, currentActorId.value)
  },
  {
    server: false,
    watch: [feedbackId, currentActorId],
    default: () => null
  }
)

const reviewStatus = ref<FeedbackReviewStatus>('submitted')
const developerNote = ref('')
const reviewPending = ref(false)
const reviewError = ref<string | null>(null)
const reviewSuccess = ref<string | null>(null)
const needsMoreInfo = computed(
  () => feedback.value?.review_status === 'needs_more_info'
)
const {
  data: timelineResponse,
  pending: timelinePending,
  error: timelineError
} = useAsyncData(
  () => `feedback-timeline-${feedbackId.value}-${currentActorId.value ?? 'none'}`,
  async () => {
    if (!currentActorId.value) {
      return {
        items: [],
        total: 0
      }
    }

    return fetchFeedbackTimeline(feedbackId.value, currentActorId.value)
  },
  {
    server: false,
    watch: [feedbackId, currentActorId],
    default: () => ({
      items: [],
      total: 0
    })
  }
)
const timelineEvents = computed(() => timelineResponse.value.items)
const timelineErrorMessage = computed(() =>
  timelineError.value
    ? getActorAwareReadErrorMessage(timelineError.value, t('feedbackDetail.timelineTitle'))
    : null
)

watch(
  feedback,
  (nextFeedback) => {
    if (!nextFeedback) {
      return
    }

    reviewStatus.value = nextFeedback.review_status
    developerNote.value = nextFeedback.developer_note ?? ''
    reviewError.value = null
  },
  {
    immediate: true
  }
)

async function handleReviewSubmit(): Promise<void> {
  if (!feedback.value) {
    reviewError.value = t('feedbackDetail.reviewNoFeedback')
    reviewSuccess.value = null
    return
  }

  if (!currentActorId.value) {
    reviewError.value = t('feedbackDetail.reviewNoActor')
    reviewSuccess.value = null
    return
  }

  const normalizedDeveloperNote = developerNote.value.trim() || null
  const currentDeveloperNote = feedback.value.developer_note ?? null

  if (
    reviewStatus.value === feedback.value.review_status &&
    normalizedDeveloperNote === currentDeveloperNote
  ) {
    reviewError.value = t('feedbackDetail.reviewNoChanges')
    reviewSuccess.value = null
    return
  }

  reviewPending.value = true
  reviewError.value = null
  reviewSuccess.value = null

  try {
    const updatedFeedback = await updateFeedback(feedbackId.value, {
      review_status: reviewStatus.value,
      developer_note: normalizedDeveloperNote
    }, currentActorId.value)

    feedback.value = updatedFeedback
    reviewStatus.value = updatedFeedback.review_status
    developerNote.value = updatedFeedback.developer_note ?? ''
    reviewSuccess.value = t('feedbackDetail.reviewSuccess')
  } catch (submitFailure) {
    reviewError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      t('feedbackDetail.reviewFallback')
    )
  } finally {
    reviewPending.value = false
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" :to="`/tasks/${taskId}`">
          {{ t('feedbackDetail.breadcrumb') }}
        </NuxtLink>
        <h1 class="resource-shell__title">{{ t('feedbackDetail.title') }}</h1>
        <p class="resource-shell__description">
          {{ t('feedbackDetail.description') }}
        </p>
        <div
          v-if="feedback"
          class="resource-state__actions"
        >
          <NuxtLink
            class="resource-action"
            data-testid="feedback-edit-link"
            :to="`/tasks/${taskId}/feedback/${feedback.id}/edit`"
          >
            {{ needsMoreInfo ? t('feedbackDetail.respondSupplement') : t('feedbackDetail.editFeedback') }}
          </NuxtLink>
          <NuxtLink
            v-if="needsMoreInfo"
            class="resource-action"
            data-testid="feedback-resubmit-link"
            :to="`/tasks/${taskId}/feedback/${feedback.id}/edit`"
          >
            {{ t('feedbackDetail.resubmitFeedback') }}
          </NuxtLink>
        </div>
      </header>

      <section
        v-if="!currentActorId"
        class="resource-state"
        data-testid="feedback-detail-select-actor"
      >
        <h2 class="resource-state__title">{{ t('feedbackDetail.selectActorTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('feedbackDetail.selectActorDescription') }}
        </p>
      </section>

      <section
        v-else-if="pending"
        class="resource-state"
        data-testid="feedback-detail-loading"
      >
        <h2 class="resource-state__title">{{ t('feedbackDetail.loadingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('feedbackDetail.loadingDescription') }}
        </p>
      </section>

      <section
        v-else-if="error || !feedback"
        class="resource-state"
        data-testid="feedback-detail-error"
      >
        <h2 class="resource-state__title">{{ t('feedbackDetail.errorTitle') }}</h2>
        <p class="resource-state__description">
          {{ getActorAwareReadErrorMessage(error, t('feedbackDetail.errorFallback')) }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            {{ t('common.retry') }}
          </button>
          <NuxtLink class="resource-action" :to="`/tasks/${taskId}`">
            {{ t('feedbackDetail.backToTask') }}
          </NuxtLink>
        </div>
      </section>

      <section
        v-if="feedback && needsMoreInfo"
        class="resource-state"
        data-testid="feedback-supplement-banner"
      >
        <h2 class="resource-state__title">{{ t('feedbackDetail.supplementTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('feedbackDetail.supplementDescription') }}
        </p>
        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">{{ t('feedbackDetail.developerNoteLabel') }}</span>
            <span class="resource-key-value__value">
              {{ feedback.developer_note || t('feedbackDetail.developerNoteEmpty') }}
            </span>
          </div>
        </div>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="feedback-supplement-edit-link"
            :to="`/tasks/${taskId}/feedback/${feedback.id}/edit`"
          >
            {{ t('feedbackDetail.openResubmitForm') }}
          </NuxtLink>
        </div>
      </section>

      <section
        v-if="feedback"
        class="detail-layout"
        data-testid="feedback-detail-layout"
      >
        <div class="detail-layout__main">
          <section
            class="resource-section"
            data-testid="feedback-detail-panel"
          >
            <span class="resource-section__eyebrow">Feedback Detail</span>
            <h2 class="resource-section__title">{{ feedback.summary }}</h2>

            <div class="resource-shell__meta">
              <span class="resource-shell__meta-chip">嚴重程度 {{ formatFeedbackSeverityLabel(feedback.severity) }}</span>
              <span class="resource-shell__meta-chip">分類 {{ formatFeedbackCategoryLabel(feedback.category) }}</span>
              <span class="resource-shell__meta-chip">
                審閱 {{ formatFeedbackReviewStatusLabel(feedback.review_status) }}
              </span>
              <span class="resource-shell__meta-chip">任務 {{ feedback.task_id }}</span>
            </div>

            <div class="resource-key-value">
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">回饋 ID</span>
                <span class="resource-key-value__value">{{ feedback.id }}</span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">活動 ID</span>
                <NuxtLink
                  class="resource-key-value__value"
                  :to="`/campaigns/${feedback.campaign_id}`"
                >
                  {{ feedback.campaign_id }}
                </NuxtLink>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">裝置設定檔 ID</span>
                <NuxtLink
                  v-if="feedback.device_profile_id"
                  class="resource-key-value__value"
                  :to="`/device-profiles/${feedback.device_profile_id}`"
                >
                  {{ feedback.device_profile_id }}
                </NuxtLink>
                <span v-else class="resource-key-value__value">
                  尚未推導。
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">評分</span>
                <span class="resource-key-value__value">
                  {{ feedback.rating ?? '尚未提供。' }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">重現步驟</span>
                <span class="resource-key-value__value">
                  {{ feedback.reproduction_steps || '尚未提供。' }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">預期結果</span>
                <span class="resource-key-value__value">
                  {{ feedback.expected_result || '尚未提供。' }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">實際結果</span>
                <span class="resource-key-value__value">
                  {{ feedback.actual_result || '尚未提供。' }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">備註</span>
                <span class="resource-key-value__value">
                  {{ feedback.note || '目前沒有備註。' }}
                </span>
              </div>
            </div>
          </section>

          <section
            class="resource-section"
            data-testid="feedback-review-panel"
          >
            <span class="resource-section__eyebrow">Review Workflow</span>
            <h2 class="resource-section__title">審閱流程</h2>
            <div class="resource-section__body">
              <p class="resource-card__description">
                開發者可在這裡標記回饋狀態，並留下最小補充要求或處理註記。
              </p>

              <div
                v-if="reviewError || reviewSuccess"
                class="resource-form__error"
                :data-testid="reviewError ? 'feedback-review-error' : 'feedback-review-success'"
              >
                {{ reviewError || reviewSuccess }}
              </div>

              <section class="resource-form__section">
                <div>
                  <h3 class="resource-form__section-title">審閱設定</h3>
                  <p class="resource-form__section-description">
                    更新回饋狀態與開發者註記後，這些內容會立即反映到 review queue 與補件流程。
                  </p>
                </div>

                <div class="resource-form__section-grid">
                  <label class="resource-field">
                    <span class="resource-field__label">審閱狀態</span>
                    <select
                      v-model="reviewStatus"
                      class="resource-select"
                      data-testid="feedback-review-status-field"
                      :disabled="reviewPending"
                    >
                      <option
                        v-for="statusOption in FEEDBACK_REVIEW_STATUS_OPTIONS"
                        :key="statusOption"
                        :value="statusOption"
                      >
                        {{ formatFeedbackReviewStatusLabel(statusOption) }}
                      </option>
                    </select>
                  </label>
                </div>

                <label class="resource-field">
                  <span class="resource-field__label">開發者註記</span>
                  <textarea
                    v-model="developerNote"
                    class="resource-textarea"
                    data-testid="feedback-developer-note-field"
                    rows="4"
                    :disabled="reviewPending"
                  />
                </label>
              </section>

              <div class="resource-form__sticky-actions">
                <button
                  class="resource-action"
                  data-testid="feedback-review-submit"
                  type="button"
                  :disabled="reviewPending"
                  @click="handleReviewSubmit"
                >
                  {{ reviewPending ? '儲存中...' : '儲存審閱變更' }}
                </button>
              </div>
            </div>
          </section>
        </div>

        <aside class="detail-layout__rail">
          <section
            class="resource-section"
            data-testid="feedback-review-context-panel"
          >
            <span class="resource-section__eyebrow">Review Context</span>
            <h2 class="resource-section__title">審閱上下文</h2>

            <div class="resource-key-value">
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">審閱狀態</span>
                <span class="resource-key-value__value">
                  {{ formatFeedbackReviewStatusLabel(feedback.review_status) }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">開發者註記</span>
                <span class="resource-key-value__value">
                  {{ feedback.developer_note || '目前沒有開發者註記。' }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">提交時間</span>
                <span class="resource-key-value__value">{{ feedback.submitted_at }}</span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">重新提交時間</span>
                <span class="resource-key-value__value">
                  {{ feedback.resubmitted_at || '尚未重新提交。' }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">更新時間</span>
                <span class="resource-key-value__value">{{ feedback.updated_at }}</span>
              </div>
            </div>
          </section>

          <ActivityTimelinePanel
            title="回饋時間線"
            description="這裡會整理回饋提交、補件要求、重新提交與審閱完成等關鍵事件。"
            :pending="timelinePending"
            :error-message="timelineErrorMessage"
            :events="timelineEvents"
            empty-message="這筆回饋目前還沒有可顯示的關鍵事件。"
            test-id-prefix="feedback-timeline"
          />
        </aside>
      </section>
    </section>
  </main>
</template>
