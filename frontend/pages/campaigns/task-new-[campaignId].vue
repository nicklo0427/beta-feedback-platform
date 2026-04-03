<script setup lang="ts">
definePageMeta({
  path: '/campaigns/:campaignId/tasks/new'
})

import { computed, ref } from 'vue'

import { fetchCampaignDetail } from '~/features/campaigns/api'
import { fetchDeviceProfiles } from '~/features/device-profiles/api'
import TaskForm from '~/features/tasks/TaskForm.vue'
import { createTask } from '~/features/tasks/api'
import { buildTaskCreatePayload, createEmptyTaskFormValues } from '~/features/tasks/form'
import type { TaskFormValues } from '~/features/tasks/types'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
const campaignId = computed(() => String(route.params.campaignId))
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = createEmptyTaskFormValues()

const {
  data: campaign,
  pending: campaignPending,
  error: campaignError,
  refresh: refreshCampaign
} = useAsyncData(
  () => `task-create-campaign-${campaignId.value}`,
  () => fetchCampaignDetail(campaignId.value),
  {
    server: false,
    watch: [campaignId],
    default: () => null
  }
)

const {
  data: deviceProfileResponse,
  pending: deviceProfilesPending,
  error: deviceProfilesError,
  refresh: refreshDeviceProfiles
} = useAsyncData(
  'task-create-device-profiles',
  () => fetchDeviceProfiles(),
  {
    server: false,
    default: () => ({
      items: [],
      total: 0
    })
  }
)

async function handleSubmit(values: TaskFormValues): Promise<void> {
  submitError.value = null
  submitting.value = true

  try {
    const createdTask = await createTask(campaignId.value, buildTaskCreatePayload(values))
    await router.push(`/tasks/${createdTask.id}`)
  } catch (error) {
    submitError.value =
      error instanceof ApiClientError
        ? error.message
        : 'Unable to save the task right now.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" :to="`/campaigns/${campaignId}`">
          Campaign Detail
        </NuxtLink>
        <h1 class="resource-shell__title">Create Task</h1>
        <p class="resource-shell__description">
          在目前的 Campaign 底下建立最小 Task，並決定要不要先指派到某個 device profile。
        </p>
        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            {{
              campaign
                ? `Campaign ${campaign.name}`
                : `Campaign ${campaignId}`
            }}
          </span>
        </div>
      </header>

      <section
        v-if="campaignPending || deviceProfilesPending"
        class="resource-state"
        data-testid="task-create-loading"
      >
        <h2 class="resource-state__title">Loading task create form</h2>
        <p class="resource-state__description">
          正在載入 campaign context 與可選 device profiles。
        </p>
      </section>

      <section
        v-else-if="campaignError || !campaign || deviceProfilesError"
        class="resource-state"
        data-testid="task-create-error"
      >
        <h2 class="resource-state__title">Task create unavailable</h2>
        <p class="resource-state__description">
          {{
            campaignError?.message
              || deviceProfilesError?.message
              || 'The task create form could not be loaded.'
          }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshCampaign()">
            Retry campaign
          </button>
          <button class="resource-action" type="button" @click="refreshDeviceProfiles()">
            Retry device profiles
          </button>
          <NuxtLink class="resource-action" :to="`/campaigns/${campaignId}`">
            Back to campaign
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="task-create-panel"
      >
        <h2 class="resource-section__title">New Task</h2>
        <TaskForm
          :initial-values="initialValues"
          :device-profiles="deviceProfileResponse.items"
          :pending="submitting"
          :error-message="submitError"
          submit-label="Create task"
          :cancel-to="`/campaigns/${campaignId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
