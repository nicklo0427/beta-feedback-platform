<script setup lang="ts">
definePageMeta({
  path: '/tasks/:taskId/feedback/:feedbackId/edit'
})

import { computed, ref, watch } from 'vue'

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
const taskId = computed(() => String(route.params.taskId))
const feedbackId = computed(() => String(route.params.feedbackId))
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = ref(createEmptyFeedbackFormValues())

const {
  data: feedback,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `feedback-edit-${feedbackId.value}`,
  () => fetchFeedbackDetail(feedbackId.value),
  {
    server: false,
    watch: [feedbackId],
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
    submitError.value = 'Feedback detail is unavailable.'
    return
  }

  const payload = buildFeedbackUpdatePayload(values, initialValues.value)

  if (!payload) {
    submitError.value = 'No changes to save yet.'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const updatedFeedback = await updateFeedback(feedbackId.value, payload)
    await router.push(`/tasks/${taskId.value}/feedback/${updatedFeedback.id}`)
  } catch (submitErr) {
    submitError.value =
      submitErr instanceof ApiClientError
        ? submitErr.message
        : 'Unable to update feedback right now.'
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
          Feedback Detail
        </NuxtLink>
        <h1 class="resource-shell__title">Edit Feedback</h1>
        <p class="resource-shell__description">
          更新既有 feedback 的最小結構化欄位，保持 task context 與既有回饋內容一致。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="feedback-edit-loading"
      >
        <h2 class="resource-state__title">Loading feedback edit form</h2>
        <p class="resource-state__description">
          正在載入既有 feedback 內容。
        </p>
      </section>

      <section
        v-else-if="error || !feedback"
        class="resource-state"
        data-testid="feedback-edit-error"
      >
        <h2 class="resource-state__title">Feedback edit unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The feedback edit form could not be loaded.' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            Retry feedback
          </button>
          <NuxtLink class="resource-action" :to="`/tasks/${taskId}`">
            Back to task
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="feedback-edit-panel"
      >
        <h2 class="resource-section__title">Edit {{ feedback.summary }}</h2>
        <FeedbackForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="Update feedback"
          :cancel-to="`/tasks/${taskId}/feedback/${feedbackId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
