<script setup lang="ts">
definePageMeta({
  path: '/tasks/:taskId/feedback/new'
})

import { computed, ref } from 'vue'

import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import FeedbackForm from '~/features/feedback/FeedbackForm.vue'
import { createFeedback } from '~/features/feedback/api'
import {
  buildFeedbackCreatePayload,
  createEmptyFeedbackFormValues
} from '~/features/feedback/form'
import type { FeedbackFormValues } from '~/features/feedback/types'
import { fetchTaskDetail } from '~/features/tasks/api'
import { formatTaskStatusLabel } from '~/features/tasks/types'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
useCurrentActorPersistence()

const taskId = computed(() => String(route.params.taskId))
const currentActorId = useCurrentActorId()
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
  if (!currentActorId.value) {
    submitError.value = '提交回饋前，請先選擇目前操作帳號。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const createdFeedback = await createFeedback(
      taskId.value,
      buildFeedbackCreatePayload(values),
      currentActorId.value
    )
    await router.push(`/tasks/${taskId.value}/feedback/${createdFeedback.id}`)
  } catch (submitFailure) {
    submitError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      '目前無法提交回饋。'
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
        <NuxtLink class="resource-shell__breadcrumb" :to="`/tasks/${taskId}`">
          任務詳情
        </NuxtLink>
        <h1 class="resource-shell__title">提交回饋</h1>
        <p class="resource-shell__description">
          在目前的任務情境下提交最小結構化回饋，先聚焦可執行的問題描述與結果差異。
        </p>
        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            {{ task ? `任務 ${task.title}` : `任務 ${taskId}` }}
          </span>
          <span
            v-if="task"
            class="resource-shell__meta-chip"
          >
            狀態 {{ formatTaskStatusLabel(task.status) }}
          </span>
        </div>
      </header>

      <CurrentActorSelector
        title="回饋提交帳號"
        description="選擇目前正在操作的測試者帳號。提交回饋時，系統會驗證這個任務是否真的指派給你。"
      />

      <section
        v-if="pending"
        class="resource-state"
        data-testid="feedback-create-loading"
      >
        <h2 class="resource-state__title">載入回饋提交表單中</h2>
        <p class="resource-state__description">
          正在載入任務情境，準備回饋提交流程。
        </p>
      </section>

      <section
        v-else-if="error || !task"
        class="resource-state"
        data-testid="feedback-create-error"
      >
        <h2 class="resource-state__title">無法載入回饋提交表單</h2>
        <p class="resource-state__description">
          {{ error?.message || '目前無法載入回饋提交表單。' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試任務資料
          </button>
          <NuxtLink class="resource-action" :to="`/tasks/${taskId}`">
            返回任務
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="feedback-create-panel"
      >
        <h2 class="resource-section__title">新增回饋</h2>
        <FeedbackForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="提交回饋"
          :cancel-to="`/tasks/${taskId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
