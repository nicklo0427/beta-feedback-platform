<script setup lang="ts">
definePageMeta({
  path: '/tasks/:taskId/feedback/new'
})

import { computed, ref } from 'vue'

import FeedbackForm from '~/features/feedback/FeedbackForm.vue'
import { createFeedback } from '~/features/feedback/api'
import {
  buildFeedbackCreatePayload,
  createEmptyFeedbackFormValues
} from '~/features/feedback/form'
import type { FeedbackFormValues } from '~/features/feedback/types'
import { fetchTaskDetail } from '~/features/tasks/api'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
const taskId = computed(() => String(route.params.taskId))
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = createEmptyFeedbackFormValues()

const {
  data: task,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `feedback-create-task-${taskId.value}`,
  () => fetchTaskDetail(taskId.value),
  {
    server: false,
    watch: [taskId],
    default: () => null
  }
)

async function handleSubmit(values: FeedbackFormValues): Promise<void> {
  submitError.value = null
  submitting.value = true

  try {
    const createdFeedback = await createFeedback(
      taskId.value,
      buildFeedbackCreatePayload(values)
    )
    await router.push(`/tasks/${taskId.value}/feedback/${createdFeedback.id}`)
  } catch (submitErr) {
    submitError.value =
      submitErr instanceof ApiClientError
        ? submitErr.message
        : 'Unable to submit feedback right now.'
  } finally {
    submitting.value = false
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
        <h1 class="resource-shell__title">Submit Feedback</h1>
        <p class="resource-shell__description">
          在目前的 task context 下提交最小結構化 feedback，先聚焦可執行問題描述與結果差異。
        </p>
        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            {{ task ? `Task ${task.title}` : `Task ${taskId}` }}
          </span>
          <span
            v-if="task"
            class="resource-shell__meta-chip"
          >
            Status {{ task.status }}
          </span>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="feedback-create-loading"
      >
        <h2 class="resource-state__title">Loading feedback submit form</h2>
        <p class="resource-state__description">
          正在載入 task context，準備 feedback submit flow。
        </p>
      </section>

      <section
        v-else-if="error || !task"
        class="resource-state"
        data-testid="feedback-create-error"
      >
        <h2 class="resource-state__title">Feedback submit unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The feedback submit form could not be loaded.' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            Retry task
          </button>
          <NuxtLink class="resource-action" :to="`/tasks/${taskId}`">
            Back to task
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="feedback-create-panel"
      >
        <h2 class="resource-section__title">New Feedback</h2>
        <FeedbackForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="Submit feedback"
          :cancel-to="`/tasks/${taskId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
