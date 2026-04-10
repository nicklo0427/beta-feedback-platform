<script setup lang="ts">
definePageMeta({
  path: '/review/participation-requests/:requestId/tasks/new'
})

import { computed, ref } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import {
  createTaskFromParticipationRequest,
  fetchParticipationRequestDetail
} from '~/features/participation-requests/api'
import TaskForm from '~/features/tasks/TaskForm.vue'
import { createEmptyTaskFormValues } from '~/features/tasks/form'
import type { TaskFormValues } from '~/features/tasks/types'

useCurrentActorPersistence()

const route = useRoute()
const router = useRouter()
const requestId = computed(() => String(route.params.requestId))
const currentActorId = useCurrentActorId()
const submitting = ref(false)
const submitError = ref<string | null>(null)

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('participation-request-task-create-accounts', () => fetchAccounts(), {
  server: false,
  default: () => ({
    items: [],
    total: 0
  })
})

const accounts = computed(() => accountResponse.value.items)
const currentActor = computed(
  () => accounts.value.find((account) => account.id === currentActorId.value) ?? null
)
const isDeveloperActor = computed(() => currentActor.value?.role === 'developer')

const {
  data: participationRequest,
  pending,
  error,
  refresh
} = useAsyncData(
  () =>
    `participation-request-task-create-${requestId.value}-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
  async () => {
    if (!currentActorId.value || !isDeveloperActor.value) {
      return null
    }

    return fetchParticipationRequestDetail(requestId.value, currentActorId.value)
  },
  {
    server: false,
    watch: [requestId, currentActorId, currentActor],
    default: () => null
  }
)

const initialValues = computed(() => ({
  ...createEmptyTaskFormValues(),
  device_profile_id: participationRequest.value?.device_profile_id ?? '',
  status: 'assigned' as const
}))

const lockedDeviceProfiles = computed(() => {
  if (!participationRequest.value) {
    return []
  }

  return [
    {
      id: participationRequest.value.device_profile.id,
      name: participationRequest.value.device_profile.name,
      platform: participationRequest.value.device_profile.platform,
      device_model: participationRequest.value.device_profile.device_model,
      os_name: participationRequest.value.device_profile.os_name,
      install_channel: participationRequest.value.device_profile.install_channel,
      owner_account_id: participationRequest.value.device_profile.owner_account_id ?? null,
      updated_at: participationRequest.value.device_profile.updated_at
    }
  ]
})

async function handleSubmit(values: TaskFormValues): Promise<void> {
  if (!currentActorId.value) {
    submitError.value = '建立任務前，請先選擇目前操作帳號。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const createdTask = await createTaskFromParticipationRequest(
      requestId.value,
      {
        title: values.title.trim(),
        instruction_summary: values.instruction_summary.trim() || null,
        status: values.status
      },
      currentActorId.value
    )
    await router.push(`/tasks/${createdTask.id}`)
  } catch (submitFailure) {
    submitError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      '目前無法從這筆 participation request 建立任務。'
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
        <NuxtLink
          class="resource-shell__breadcrumb"
          :to="`/review/participation-requests/${requestId}`"
        >
          參與意圖詳情
        </NuxtLink>
        <h1 class="resource-shell__title">從參與意圖建立任務</h1>
        <p class="resource-shell__description">
          這個流程會沿用 participation request 內已接受的活動與裝置設定檔，只需要補上任務標題、說明與狀態。
        </p>
      </header>

      <CurrentActorSelector
        title="任務建立情境"
        description="請選擇目前操作的開發者帳號。系統會檢查這筆 participation request 是否屬於你擁有的活動。"
      />

      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="participation-request-task-create-actor-error"
      >
        <h2 class="resource-state__title">無法取得操作情境</h2>
        <p class="resource-state__description">{{ accountsError.message }}</p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshAccounts()">
            重試
          </button>
        </div>
      </section>

      <section
        v-else-if="accountsPending"
        class="resource-state"
        data-testid="participation-request-task-create-actor-loading"
      >
        <h2 class="resource-state__title">載入開發者情境中</h2>
        <p class="resource-state__description">正在確認目前操作帳號。</p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="participation-request-task-create-select-actor"
      >
        <h2 class="resource-state__title">請選擇開發者帳號</h2>
        <p class="resource-state__description">
          先選擇目前操作帳號，系統才知道能不能從這筆 participation request 建立任務。
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="participation-request-task-create-actor-missing"
      >
        <h2 class="resource-state__title">找不到已選擇的帳號</h2>
        <p class="resource-state__description">
          目前找不到你選擇的帳號，請重新選擇一筆可用的開發者帳號。
        </p>
      </section>

      <section
        v-else-if="!isDeveloperActor"
        class="resource-state"
        data-testid="participation-request-task-create-role-mismatch"
      >
        <h2 class="resource-state__title">建立任務需要開發者帳號</h2>
        <p class="resource-state__description">
          目前選到的是{{ formatAccountRoleLabel(currentActor.role) }}帳號。請切換到開發者帳號，再從這筆 participation request 建立任務。
        </p>
      </section>

      <section
        v-else-if="pending"
        class="resource-state"
        data-testid="participation-request-task-create-loading"
      >
        <h2 class="resource-state__title">載入 participation request 中</h2>
        <p class="resource-state__description">
          正在整理活動與裝置設定檔上下文。
        </p>
      </section>

      <section
        v-else-if="error || !participationRequest"
        class="resource-state"
        data-testid="participation-request-task-create-error"
      >
        <h2 class="resource-state__title">無法載入建立任務流程</h2>
        <p class="resource-state__description">
          {{ error?.message || '找不到指定的 participation request。' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試
          </button>
          <NuxtLink class="resource-action" :to="`/review/participation-requests/${requestId}`">
            返回參與意圖詳情
          </NuxtLink>
        </div>
      </section>

      <section
        v-else-if="participationRequest.linked_task_id"
        class="resource-state"
        data-testid="participation-request-task-create-linked"
      >
        <h2 class="resource-state__title">這筆參與意圖已建立對應任務</h2>
        <p class="resource-state__description">
          這筆 participation request 已在 {{ participationRequest.assignment_created_at || '稍早' }} 建立對應任務。
        </p>
        <div class="resource-state__actions">
          <NuxtLink class="resource-action" :to="`/tasks/${participationRequest.linked_task_id}`">
            查看對應任務
          </NuxtLink>
          <NuxtLink class="resource-action" :to="`/review/participation-requests/${requestId}`">
            返回參與意圖詳情
          </NuxtLink>
        </div>
      </section>

      <section
        v-else-if="participationRequest.status !== 'accepted'"
        class="resource-state"
        data-testid="participation-request-task-create-status-mismatch"
      >
        <h2 class="resource-state__title">只有已接受的參與意圖才能建立任務</h2>
        <p class="resource-state__description">
          目前這筆 participation request 的狀態是{{ participationRequest.status }}，請先完成接受流程。
        </p>
        <div class="resource-state__actions">
          <NuxtLink class="resource-action" :to="`/review/participation-requests/${requestId}`">
            返回參與意圖詳情
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="participation-request-task-create-panel"
      >
        <h2 class="resource-section__title">建立對應任務</h2>

        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            活動 {{ participationRequest.campaign_name }}
          </span>
          <span class="resource-shell__meta-chip">
            裝置 {{ participationRequest.device_profile_name }}
          </span>
        </div>

        <TaskForm
          :campaign-id="participationRequest.campaign_id"
          :actor-id="currentActorId"
          :initial-values="initialValues"
          :device-profiles="lockedDeviceProfiles"
          :lock-device-profile="true"
          :pending="submitting"
          :error-message="submitError"
          submit-label="建立對應任務"
          :cancel-to="`/review/participation-requests/${requestId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
