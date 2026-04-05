<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
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
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
useCurrentActorPersistence()

const taskId = computed(() => String(route.params.taskId))
const feedbackId = computed(() => String(route.params.feedbackId))
const currentActorId = useCurrentActorId()

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
const needsMoreInfo = computed(
  () => feedback.value?.review_status === 'needs_more_info'
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
    reviewError.value = '目前無法取得回饋內容。'
    reviewSuccess.value = null
    return
  }

  if (!currentActorId.value) {
    reviewError.value = '儲存審閱變更前，請先選擇目前操作帳號。'
    reviewSuccess.value = null
    return
  }

  const normalizedDeveloperNote = developerNote.value.trim() || null
  const currentDeveloperNote = feedback.value.developer_note ?? null

  if (
    reviewStatus.value === feedback.value.review_status &&
    normalizedDeveloperNote === currentDeveloperNote
  ) {
    reviewError.value = '目前沒有可儲存的審閱變更。'
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
    reviewSuccess.value = '審閱變更已儲存。'
  } catch (submitFailure) {
    reviewError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      '目前無法更新回饋審閱資訊。'
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
          任務詳情
        </NuxtLink>
        <h1 class="resource-shell__title">回饋詳情</h1>
        <p class="resource-shell__description">
          這個頁面先承接單一回饋的核心欄位，提供後續整理與審閱流程可依附的最小詳情頁骨架。
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
            {{ needsMoreInfo ? '回應補件要求' : '編輯回饋' }}
          </NuxtLink>
          <NuxtLink
            v-if="needsMoreInfo"
            class="resource-action"
            data-testid="feedback-resubmit-link"
            :to="`/tasks/${taskId}/feedback/${feedback.id}/edit`"
          >
            重新提交回饋
          </NuxtLink>
        </div>
      </header>

      <CurrentActorSelector
        title="回饋操作帳號"
        description="選擇目前操作的帳號。測試者可更新自己的回饋內容，開發者可審閱屬於自己活動的回饋。"
      />

      <section
        v-if="pending"
        class="resource-state"
        data-testid="feedback-detail-loading"
      >
        <h2 class="resource-state__title">載入回饋詳情中</h2>
        <p class="resource-state__description">
          正在從 API 載入回饋詳情。
        </p>
      </section>

      <section
        v-else-if="error || !feedback"
        class="resource-state"
        data-testid="feedback-detail-error"
      >
        <h2 class="resource-state__title">無法載入回饋詳情</h2>
        <p class="resource-state__description">
          {{ error?.message || '找不到指定的回饋。' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試
          </button>
          <NuxtLink class="resource-action" :to="`/tasks/${taskId}`">
            返回任務
          </NuxtLink>
        </div>
      </section>

      <section
        v-if="feedback && needsMoreInfo"
        class="resource-state"
        data-testid="feedback-supplement-banner"
      >
        <h2 class="resource-state__title">需要補充資訊</h2>
        <p class="resource-state__description">
          開發者已要求補充資訊。更新回饋後再次送出，審閱狀態會自動回到「已提交」。
        </p>
        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">開發者註記</span>
            <span class="resource-key-value__value">
              {{ feedback.developer_note || '目前沒有補充說明。' }}
            </span>
          </div>
        </div>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="feedback-supplement-edit-link"
            :to="`/tasks/${taskId}/feedback/${feedback.id}/edit`"
          >
            開啟重新提交表單
          </NuxtLink>
        </div>
      </section>

      <section
        v-if="feedback"
        class="resource-section"
        data-testid="feedback-detail-panel"
      >
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

      <section
        v-if="feedback"
        class="resource-section"
        data-testid="feedback-review-panel"
      >
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

          <div class="resource-form__grid">
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

          <div class="resource-form__actions">
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
    </section>
  </main>
</template>
