<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { fetchFeedbackDetail, updateFeedback } from '~/features/feedback/api'
import {
  FEEDBACK_REVIEW_STATUS_OPTIONS,
  formatFeedbackReviewStatusLabel,
  type FeedbackReviewStatus
} from '~/features/feedback/types'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const taskId = computed(() => String(route.params.taskId))
const feedbackId = computed(() => String(route.params.feedbackId))

const {
  data: feedback,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `feedback-detail-${feedbackId.value}`,
  () => fetchFeedbackDetail(feedbackId.value),
  {
    server: false,
    watch: [feedbackId],
    default: () => null
  }
)

const reviewStatus = ref<FeedbackReviewStatus>('submitted')
const developerNote = ref('')
const reviewPending = ref(false)
const reviewError = ref<string | null>(null)
const reviewSuccess = ref<string | null>(null)

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
    reviewError.value = 'Feedback detail is unavailable.'
    reviewSuccess.value = null
    return
  }

  const normalizedDeveloperNote = developerNote.value.trim() || null
  const currentDeveloperNote = feedback.value.developer_note ?? null

  if (
    reviewStatus.value === feedback.value.review_status &&
    normalizedDeveloperNote === currentDeveloperNote
  ) {
    reviewError.value = 'No review changes to save yet.'
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
    })

    feedback.value = updatedFeedback
    reviewStatus.value = updatedFeedback.review_status
    developerNote.value = updatedFeedback.developer_note ?? ''
    reviewSuccess.value = 'Review changes saved.'
  } catch (submitFailure) {
    reviewError.value =
      submitFailure instanceof ApiClientError
        ? submitFailure.message
        : 'Unable to update feedback review right now.'
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
          Task Detail
        </NuxtLink>
        <h1 class="resource-shell__title">Feedback Detail Shell</h1>
        <p class="resource-shell__description">
          這個頁面先承接單一 feedback 的核心欄位，提供後續 triage 與回饋整理流程可依附的最小 detail shell。
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
            Edit feedback
          </NuxtLink>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="feedback-detail-loading"
      >
        <h2 class="resource-state__title">Loading feedback detail</h2>
        <p class="resource-state__description">
          正在從 API 載入 feedback detail。
        </p>
      </section>

      <section
        v-else-if="error || !feedback"
        class="resource-state"
        data-testid="feedback-detail-error"
      >
        <h2 class="resource-state__title">Feedback detail unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The requested feedback could not be loaded.' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            Retry
          </button>
          <NuxtLink class="resource-action" :to="`/tasks/${taskId}`">
            Back to task
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="feedback-detail-panel"
      >
        <h2 class="resource-section__title">{{ feedback.summary }}</h2>

        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">Severity {{ feedback.severity }}</span>
          <span class="resource-shell__meta-chip">Category {{ feedback.category }}</span>
          <span class="resource-shell__meta-chip">
            Review {{ formatFeedbackReviewStatusLabel(feedback.review_status) }}
          </span>
          <span class="resource-shell__meta-chip">Task {{ feedback.task_id }}</span>
        </div>

        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Feedback ID</span>
            <span class="resource-key-value__value">{{ feedback.id }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Campaign ID</span>
            <NuxtLink
              class="resource-key-value__value"
              :to="`/campaigns/${feedback.campaign_id}`"
            >
              {{ feedback.campaign_id }}
            </NuxtLink>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Device Profile ID</span>
            <NuxtLink
              v-if="feedback.device_profile_id"
              class="resource-key-value__value"
              :to="`/device-profiles/${feedback.device_profile_id}`"
            >
              {{ feedback.device_profile_id }}
            </NuxtLink>
            <span v-else class="resource-key-value__value">
              Not derived yet.
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Rating</span>
            <span class="resource-key-value__value">
              {{ feedback.rating ?? 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Reproduction Steps</span>
            <span class="resource-key-value__value">
              {{ feedback.reproduction_steps || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Expected Result</span>
            <span class="resource-key-value__value">
              {{ feedback.expected_result || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Actual Result</span>
            <span class="resource-key-value__value">
              {{ feedback.actual_result || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Note</span>
            <span class="resource-key-value__value">
              {{ feedback.note || 'No note provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Review Status</span>
            <span class="resource-key-value__value">
              {{ formatFeedbackReviewStatusLabel(feedback.review_status) }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Developer Note</span>
            <span class="resource-key-value__value">
              {{ feedback.developer_note || 'No developer note yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Submitted At</span>
            <span class="resource-key-value__value">{{ feedback.submitted_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Updated At</span>
            <span class="resource-key-value__value">{{ feedback.updated_at }}</span>
          </div>
        </div>
      </section>

      <section class="resource-section" data-testid="feedback-review-panel">
        <h2 class="resource-section__title">Review Workflow</h2>
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

          <div class="resource-form__grid">
            <label class="resource-field">
              <span class="resource-field__label">Review Status</span>
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
            <span class="resource-field__label">Developer Note</span>
            <textarea
              v-model="developerNote"
              class="resource-textarea"
              data-testid="feedback-developer-note-field"
              rows="4"
              :disabled="reviewPending"
            />
          </label>

          <div class="resource-form__actions">
            <button
              class="resource-action"
              data-testid="feedback-review-submit"
              type="button"
              :disabled="reviewPending"
              @click="handleReviewSubmit"
            >
              {{ reviewPending ? 'Saving...' : 'Save review changes' }}
            </button>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>
