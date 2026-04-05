<script setup lang="ts">
definePageMeta({
  path: '/tasks/:taskId/edit'
})

import { computed, ref, watch } from 'vue'

import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { fetchDeviceProfiles } from '~/features/device-profiles/api'
import TaskForm from '~/features/tasks/TaskForm.vue'
import { fetchTaskDetail, updateTask } from '~/features/tasks/api'
import { buildTaskUpdatePayload, createEmptyTaskFormValues, toTaskFormValues } from '~/features/tasks/form'
import type { TaskFormValues } from '~/features/tasks/types'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
useCurrentActorPersistence()

const taskId = computed(() => String(route.params.taskId))
const currentActorId = useCurrentActorId()
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = ref(createEmptyTaskFormValues())

const {
  data: task,
  pending: taskPending,
  error: taskError,
  refresh: refreshTask
} = useAsyncData(
  () => `task-edit-${taskId.value}`,
  () => fetchTaskDetail(taskId.value),
  {
    server: false,
    watch: [taskId],
    default: () => null
  }
)

const {
  data: deviceProfileResponse,
  pending: deviceProfilesPending,
  error: deviceProfilesError,
  refresh: refreshDeviceProfiles
} = useAsyncData(
  'task-edit-device-profiles',
  () => fetchDeviceProfiles(),
  {
    server: false,
    default: () => ({
      items: [],
      total: 0
    })
  }
)

watch(
  task,
  (nextTask) => {
    if (!nextTask) {
      return
    }

    initialValues.value = toTaskFormValues(nextTask)
    submitError.value = null
  },
  {
    immediate: true
  }
)

async function handleSubmit(values: TaskFormValues): Promise<void> {
  if (!task.value) {
    submitError.value = '目前無法取得任務內容。'
    return
  }

  if (!currentActorId.value) {
    submitError.value = '更新任務前，請先選擇目前操作帳號。'
    return
  }

  const payload = buildTaskUpdatePayload(values, initialValues.value)

  if (!payload) {
    submitError.value = '目前沒有可儲存的變更。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const updatedTask = await updateTask(taskId.value, payload, currentActorId.value)
    await router.push(`/tasks/${updatedTask.id}`)
  } catch (submitFailure) {
    submitError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      '目前無法更新任務。'
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
        <h1 class="resource-shell__title">編輯任務</h1>
        <p class="resource-shell__description">
          更新單一任務的最小欄位、指派目標與狀態，並讓後端驗證狀態流轉是否合法。
        </p>
      </header>

      <CurrentActorSelector
        title="任務操作帳號"
        description="選擇目前正在操作的開發者帳號。更新任務時，系統會驗證這個任務是否屬於你。"
      />

      <section
        v-if="taskPending || deviceProfilesPending"
        class="resource-state"
        data-testid="task-edit-loading"
      >
        <h2 class="resource-state__title">載入任務編輯表單中</h2>
        <p class="resource-state__description">
          正在載入既有任務與可選的裝置設定檔。
        </p>
      </section>

      <section
        v-else-if="taskError || !task || deviceProfilesError"
        class="resource-state"
        data-testid="task-edit-error"
      >
        <h2 class="resource-state__title">無法載入任務編輯表單</h2>
        <p class="resource-state__description">
          {{
            taskError?.message
              || deviceProfilesError?.message
              || '目前無法載入任務編輯表單。'
          }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshTask()">
            重試任務資料
          </button>
          <button class="resource-action" type="button" @click="refreshDeviceProfiles()">
            重試裝置設定檔
          </button>
          <NuxtLink class="resource-action" to="/tasks">
            返回任務列表
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="task-edit-panel"
      >
        <h2 class="resource-section__title">編輯 {{ task.title }}</h2>
        <TaskForm
          :initial-values="initialValues"
          :device-profiles="deviceProfileResponse.items"
          :pending="submitting"
          :error-message="submitError"
          submit-label="更新任務"
          :cancel-to="`/tasks/${taskId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
