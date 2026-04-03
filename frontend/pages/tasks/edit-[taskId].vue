<script setup lang="ts">
definePageMeta({
  path: '/tasks/:taskId/edit'
})

import { computed, ref, watch } from 'vue'

import { fetchDeviceProfiles } from '~/features/device-profiles/api'
import TaskForm from '~/features/tasks/TaskForm.vue'
import { fetchTaskDetail, updateTask } from '~/features/tasks/api'
import { buildTaskUpdatePayload, createEmptyTaskFormValues, toTaskFormValues } from '~/features/tasks/form'
import type { TaskFormValues } from '~/features/tasks/types'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
const taskId = computed(() => String(route.params.taskId))
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
    submitError.value = 'Task detail is unavailable.'
    return
  }

  const payload = buildTaskUpdatePayload(values, initialValues.value)

  if (!payload) {
    submitError.value = 'No changes to save yet.'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const updatedTask = await updateTask(taskId.value, payload)
    await router.push(`/tasks/${updatedTask.id}`)
  } catch (error) {
    submitError.value =
      error instanceof ApiClientError
        ? error.message
        : 'Unable to update the task right now.'
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
        <h1 class="resource-shell__title">Edit Task</h1>
        <p class="resource-shell__description">
          更新單一 Task 的最小欄位、assignment target 與 status，並讓 backend 驗證狀態流轉是否合法。
        </p>
      </header>

      <section
        v-if="taskPending || deviceProfilesPending"
        class="resource-state"
        data-testid="task-edit-loading"
      >
        <h2 class="resource-state__title">Loading task edit form</h2>
        <p class="resource-state__description">
          正在載入既有 Task 與可選 device profiles。
        </p>
      </section>

      <section
        v-else-if="taskError || !task || deviceProfilesError"
        class="resource-state"
        data-testid="task-edit-error"
      >
        <h2 class="resource-state__title">Task edit unavailable</h2>
        <p class="resource-state__description">
          {{
            taskError?.message
              || deviceProfilesError?.message
              || 'The task edit form could not be loaded.'
          }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshTask()">
            Retry task
          </button>
          <button class="resource-action" type="button" @click="refreshDeviceProfiles()">
            Retry device profiles
          </button>
          <NuxtLink class="resource-action" to="/tasks">
            Back to tasks
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="task-edit-panel"
      >
        <h2 class="resource-section__title">Edit {{ task.title }}</h2>
        <TaskForm
          :initial-values="initialValues"
          :device-profiles="deviceProfileResponse.items"
          :pending="submitting"
          :error-message="submitError"
          submit-label="Update task"
          :cancel-to="`/tasks/${taskId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
