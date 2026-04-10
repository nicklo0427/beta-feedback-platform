<script setup lang="ts">
definePageMeta({
  path: '/tasks/:taskId/feedback/:feedbackId/edit'
})

import { computed, ref, watch } from 'vue'

import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  getActorAwareReadErrorMessage,
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import FeedbackForm from '~/features/feedback/FeedbackForm.vue'
import { fetchFeedbackDetail, updateFeedback } from '~/features/feedback/api'
import {
  buildFeedbackUpdatePayload,
  createEmptyFeedbackFormValues,
  toFeedbackFormValues
} from '~/features/feedback/form'
import type { FeedbackFormValues } from '~/features/feedback/types'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
useCurrentActorPersistence()

const taskId = computed(() => String(route.params.taskId))
const feedbackId = computed(() => String(route.params.feedbackId))
const currentActorId = useCurrentActorId()
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = ref(createEmptyFeedbackFormValues())
const isResubmission = computed(
  () => feedback.value?.review_status === 'needs_more_info'
)

const {
  data: feedback,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `feedback-edit-${feedbackId.value}-${currentActorId.value ?? 'none'}`,
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

watch(
  feedback,
  (nextFeedback) => {
    if (!nextFeedback) {
      return
    }

    initialValues.value = toFeedbackFormValues(nextFeedback)
    submitError.value = null
  },
  {
    immediate: true
  }
)

async function handleSubmit(values: FeedbackFormValues): Promise<void> {
  if (!feedback.value) {
    submitError.value = '目前無法取得回饋內容。'
    return
  }

  if (!currentActorId.value) {
    submitError.value = '更新回饋前，請先選擇目前操作帳號。'
    return
  }

  const payload = buildFeedbackUpdatePayload(values, initialValues.value)

  if (!payload) {
    submitError.value = '目前沒有可儲存的變更。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const updatedFeedback = await updateFeedback(
      feedbackId.value,
      payload,
      currentActorId.value
    )
    await router.push(`/tasks/${taskId.value}/feedback/${updatedFeedback.id}`)
  } catch (submitFailure) {
    submitError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      '目前無法更新回饋。'
    )
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" :to="`/tasks/${taskId}/feedback/${feedbackId}`">
          回饋詳情
        </NuxtLink>
        <h1 class="resource-shell__title">編輯回饋</h1>
        <p class="resource-shell__description">
          更新既有回饋的最小結構化欄位，保持任務情境與既有回饋內容一致。
        </p>
      </header>

      <CurrentActorSelector
        title="回饋操作帳號"
        description="選擇目前正在操作的測試者帳號。更新回饋與重新提交時，系統會驗證這筆回饋是否屬於你的任務指派。"
      />

      <section
        v-if="!currentActorId"
        class="resource-state"
        data-testid="feedback-edit-select-actor"
      >
        <h2 class="resource-state__title">請先選擇目前操作帳號</h2>
        <p class="resource-state__description">
          回饋編輯頁現在需要 actor-aware read context，請先選擇目前操作帳號。
        </p>
      </section>

      <section
        v-else-if="pending"
        class="resource-state"
        data-testid="feedback-edit-loading"
      >
        <h2 class="resource-state__title">載入回饋編輯表單中</h2>
        <p class="resource-state__description">
          正在載入既有回饋內容。
        </p>
      </section>

      <section
        v-else-if="error || !feedback"
        class="resource-state"
        data-testid="feedback-edit-error"
      >
        <h2 class="resource-state__title">無法載入回饋編輯表單</h2>
        <p class="resource-state__description">
          {{ getActorAwareReadErrorMessage(error, '目前無法載入回饋編輯表單。') }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試回饋資料
          </button>
          <NuxtLink class="resource-action" :to="`/tasks/${taskId}`">
            返回任務
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="feedback-edit-panel"
      >
        <h2 class="resource-section__title">編輯 {{ feedback.summary }}</h2>
        <div
          v-if="isResubmission"
          class="resource-state"
          data-testid="feedback-resubmission-context"
        >
          <h3 class="resource-state__title">需要重新提交</h3>
          <p class="resource-state__description">
            這筆回饋目前為「需補充資訊」。更新內容並送出後，系統會自動將審閱狀態改回「已提交」。
          </p>
          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">開發者註記</span>
              <span class="resource-key-value__value">
                {{ feedback.developer_note || '目前沒有補充說明。' }}
              </span>
            </div>
          </div>
        </div>
        <FeedbackForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          :submit-label="isResubmission ? '重新提交回饋' : '更新回饋'"
          :cancel-to="`/tasks/${taskId}/feedback/${feedbackId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
