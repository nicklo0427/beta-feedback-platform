<script setup lang="ts">
definePageMeta({
  path: '/review/participation-requests/:requestId/tasks/new'
})

import { computed, ref } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import {
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import {
  accountHasRole,
  formatAccountRolesLabel,
  normalizeAccountRoles
} from '~/features/accounts/types'
import { useAppI18n } from '~/features/i18n/use-app-i18n'
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
const { locale, t } = useAppI18n()
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
const currentActorRolesKey = computed(
  () => normalizeAccountRoles(currentActor.value ?? {}).join('|') || 'none'
)
const isDeveloperActor = computed(() => accountHasRole(currentActor.value, 'developer'))

const {
  data: participationRequest,
  pending,
  error,
  refresh
} = useAsyncData(
  () =>
    `participation-request-task-create-${requestId.value}-${currentActorId.value ?? 'none'}-${currentActorRolesKey.value}`,
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
    submitError.value = t('participationTaskCreate.submitNoActor')
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
      t('participationTaskCreate.errorFallback')
    )
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="app-shell" :data-locale="locale">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink
          class="resource-shell__breadcrumb"
          :to="`/review/participation-requests/${requestId}`"
        >
          {{ t('participationTaskCreate.breadcrumb') }}
        </NuxtLink>
        <h1 class="resource-shell__title">{{ t('participationTaskCreate.title') }}</h1>
        <p class="resource-shell__description">
          {{ t('participationTaskCreate.description') }}
        </p>
        <div class="resource-shell__meta">
          <span
            v-if="currentActor"
            class="resource-shell__meta-chip"
          >
            {{ t('participationTaskCreate.currentAccount') }} {{ currentActor.display_name }}
          </span>
          <span class="resource-shell__meta-chip">{{ t('participationTaskCreate.switchContextHint') }}</span>
        </div>
      </header>

      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="participation-request-task-create-actor-error"
      >
        <h2 class="resource-state__title">{{ t('participationTaskCreate.actorErrorTitle') }}</h2>
        <p class="resource-state__description">{{ accountsError.message }}</p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshAccounts()">
            {{ t('common.retry') }}
          </button>
        </div>
      </section>

      <section
        v-else-if="accountsPending"
        class="resource-state"
        data-testid="participation-request-task-create-actor-loading"
      >
        <h2 class="resource-state__title">{{ t('participationTaskCreate.actorLoadingTitle') }}</h2>
        <p class="resource-state__description">{{ t('participationTaskCreate.actorLoadingDescription') }}</p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="participation-request-task-create-select-actor"
      >
        <h2 class="resource-state__title">{{ t('participationTaskCreate.selectActorTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('participationTaskCreate.selectActorDescription') }}
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="participation-request-task-create-actor-missing"
      >
        <h2 class="resource-state__title">{{ t('participationTaskCreate.actorMissingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('participationTaskCreate.actorMissingDescription') }}
        </p>
      </section>

      <section
        v-else-if="!isDeveloperActor"
        class="resource-state"
        data-testid="participation-request-task-create-role-mismatch"
      >
        <h2 class="resource-state__title">{{ t('participationTaskCreate.roleMismatchTitle') }}</h2>
        <p class="resource-state__description">
          {{
            t('participationTaskCreate.roleMismatchDescription', {
              role: formatAccountRolesLabel(currentActor, locale)
            })
          }}
        </p>
      </section>

      <section
        v-else-if="pending"
        class="resource-state"
        data-testid="participation-request-task-create-loading"
      >
        <h2 class="resource-state__title">{{ t('participationTaskCreate.loadingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('participationTaskCreate.loadingDescription') }}
        </p>
      </section>

      <section
        v-else-if="error || !participationRequest"
        class="resource-state"
        data-testid="participation-request-task-create-error"
      >
        <h2 class="resource-state__title">{{ t('participationTaskCreate.errorTitle') }}</h2>
        <p class="resource-state__description">
          {{ error?.message || t('participationTaskCreate.errorFallback') }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            {{ t('common.retry') }}
          </button>
          <NuxtLink class="resource-action" :to="`/review/participation-requests/${requestId}`">
            {{ t('participationTaskCreate.backToDetail') }}
          </NuxtLink>
        </div>
      </section>

      <section
        v-else-if="participationRequest.linked_task_id"
        class="resource-state"
        data-testid="participation-request-task-create-linked"
      >
        <h2 class="resource-state__title">{{ t('participationTaskCreate.linkedTitle') }}</h2>
        <p class="resource-state__description">
          {{
            t('participationTaskCreate.linkedDescription', {
              when: participationRequest.assignment_created_at || t('participationTaskCreate.laterLabel')
            })
          }}
        </p>
        <div class="resource-state__actions">
          <NuxtLink class="resource-action" :to="`/tasks/${participationRequest.linked_task_id}`">
            {{ t('participationTaskCreate.viewLinkedTask') }}
          </NuxtLink>
          <NuxtLink class="resource-action" :to="`/review/participation-requests/${requestId}`">
            {{ t('participationTaskCreate.backToDetail') }}
          </NuxtLink>
        </div>
      </section>

      <section
        v-else-if="participationRequest.status !== 'accepted'"
        class="resource-state"
        data-testid="participation-request-task-create-status-mismatch"
      >
        <h2 class="resource-state__title">{{ t('participationTaskCreate.statusMismatchTitle') }}</h2>
        <p class="resource-state__description">
          {{
            t('participationTaskCreate.statusMismatchDescription', {
              status: participationRequest.status
            })
          }}
        </p>
        <div class="resource-state__actions">
          <NuxtLink class="resource-action" :to="`/review/participation-requests/${requestId}`">
            {{ t('participationTaskCreate.backToDetail') }}
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="participation-request-task-create-panel"
      >
        <h2 class="resource-section__title">{{ t('participationTaskCreate.panelTitle') }}</h2>

        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            {{ t('participationTaskCreate.campaignLabel') }} {{ participationRequest.campaign_name }}
          </span>
          <span class="resource-shell__meta-chip">
            {{ t('participationTaskCreate.deviceLabel') }} {{ participationRequest.device_profile_name }}
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
          :submit-label="t('participationTaskCreate.panelTitle')"
          :cancel-to="`/review/participation-requests/${requestId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
