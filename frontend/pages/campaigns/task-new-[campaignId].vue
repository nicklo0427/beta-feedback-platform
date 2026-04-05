<script setup lang="ts">
definePageMeta({
  path: '/campaigns/:campaignId/tasks/new'
})

import { computed, ref } from 'vue'

import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { fetchCampaignDetail } from '~/features/campaigns/api'
import { fetchDeviceProfiles } from '~/features/device-profiles/api'
import TaskForm from '~/features/tasks/TaskForm.vue'
import { createTask } from '~/features/tasks/api'
import { buildTaskCreatePayload, createEmptyTaskFormValues } from '~/features/tasks/form'
import type { TaskFormValues } from '~/features/tasks/types'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
useCurrentActorPersistence()

const campaignId = computed(() => String(route.params.campaignId))
const currentActorId = useCurrentActorId()
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
  if (!currentActorId.value) {
    submitError.value = '建立任務前，請先選擇目前操作帳號。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const createdTask = await createTask(
      campaignId.value,
      buildTaskCreatePayload(values),
      currentActorId.value
    )
    await router.push(`/tasks/${createdTask.id}`)
  } catch (submitFailure) {
    submitError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      '目前無法儲存任務。'
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
        <NuxtLink class="resource-shell__breadcrumb" :to="`/campaigns/${campaignId}`">
          活動詳情
        </NuxtLink>
        <h1 class="resource-shell__title">建立任務</h1>
        <p class="resource-shell__description">
          在目前的活動底下建立最小任務，並決定要不要先指派到某個裝置設定檔。
        </p>
        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            {{
              campaign
                ? `活動 ${campaign.name}`
                : `活動 ${campaignId}`
            }}
          </span>
        </div>
      </header>

      <CurrentActorSelector
        title="任務操作帳號"
        description="選擇目前正在操作的開發者帳號。建立任務時，系統會驗證這個活動是否屬於你。"
      />

      <section
        v-if="campaignPending || deviceProfilesPending"
        class="resource-state"
        data-testid="task-create-loading"
      >
        <h2 class="resource-state__title">載入任務建立表單中</h2>
        <p class="resource-state__description">
          正在載入活動情境與可選的裝置設定檔。
        </p>
      </section>

      <section
        v-else-if="campaignError || !campaign || deviceProfilesError"
        class="resource-state"
        data-testid="task-create-error"
      >
        <h2 class="resource-state__title">無法載入任務建立表單</h2>
        <p class="resource-state__description">
          {{
            campaignError?.message
              || deviceProfilesError?.message
              || '目前無法載入任務建立表單。'
          }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshCampaign()">
            重試活動資料
          </button>
          <button class="resource-action" type="button" @click="refreshDeviceProfiles()">
            重試裝置設定檔
          </button>
          <NuxtLink class="resource-action" :to="`/campaigns/${campaignId}`">
            返回活動
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="task-create-panel"
      >
        <h2 class="resource-section__title">新增任務</h2>
        <TaskForm
          :initial-values="initialValues"
          :device-profiles="deviceProfileResponse.items"
          :pending="submitting"
          :error-message="submitError"
          submit-label="建立任務"
          :cancel-to="`/campaigns/${campaignId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
