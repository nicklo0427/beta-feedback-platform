<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import {
  getActorAwareReadErrorMessage,
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import {
  accountHasRole,
  formatAccountRolesLabel,
  normalizeAccountRoles
} from '~/features/accounts/types'
import {
  fetchMyParticipationRequests,
  withdrawParticipationRequest
} from '~/features/participation-requests/api'
import {
  formatParticipationAssignmentStatusLabel,
  formatParticipationRequestStatusLabel
} from '~/features/participation-requests/types'
import { useAppI18n } from '~/features/i18n/use-app-i18n'

useCurrentActorPersistence()

const { locale, t } = useAppI18n()
const currentActorId = useCurrentActorId()
const actionError = ref<string | null>(null)
const withdrawingRequestId = ref<string | null>(null)

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('my-participation-requests-accounts', () => fetchAccounts(), {
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
const isTesterActor = computed(() => accountHasRole(currentActor.value, 'tester'))

const {
  data: requestResponse,
  pending: requestsPending,
  error: requestsError,
  refresh: refreshRequests
} = useAsyncData(
  () =>
    `my-participation-requests-${currentActorId.value ?? 'none'}-${currentActorRolesKey.value}`,
  async () => {
    if (!currentActorId.value || !isTesterActor.value) {
      return {
        items: [],
        total: 0
      }
    }

    return fetchMyParticipationRequests(currentActorId.value)
  },
  {
    server: false,
    watch: [currentActorId, currentActor],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const participationRequests = computed(() => requestResponse.value.items)
const requestsErrorMessage = computed(() =>
  getActorAwareReadErrorMessage(
    requestsError.value,
    '目前無法載入我的參與申請。'
  )
)

async function handleWithdrawRequest(requestId: string): Promise<void> {
  actionError.value = null
  withdrawingRequestId.value = requestId

  try {
    if (!currentActorId.value) {
      actionError.value = t('myParticipationRequests.withdrawNoActor')
      return
    }

    await withdrawParticipationRequest(requestId, currentActorId.value)
    await refreshRequests()
  } catch (withdrawFailure) {
    actionError.value = getActorAwareMutationErrorMessage(
      withdrawFailure,
      t('myParticipationRequests.withdrawFallback')
    )
  } finally {
    withdrawingRequestId.value = null
  }
}

watch([currentActorId, currentActor], () => {
  actionError.value = null
  withdrawingRequestId.value = null
})
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header app-page-header">
        <NuxtLink class="resource-shell__breadcrumb" to="/dashboard">Dashboard</NuxtLink>
        <h1 class="resource-shell__title">{{ t('myParticipationRequests.title') }}</h1>
        <p class="resource-shell__description">
          {{ t('myParticipationRequests.description') }}
        </p>
        <div class="resource-state__actions app-page-actions">
          <NuxtLink class="resource-action" to="/my/eligible-campaigns">
            {{ t('myParticipationRequests.viewEligibleCampaigns') }}
          </NuxtLink>
          <NuxtLink class="resource-action" to="/my/tasks">
            {{ t('myParticipationRequests.viewMyTasks') }}
          </NuxtLink>
        </div>
      </header>
      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="my-participation-requests-actor-error"
      >
        <h2 class="resource-state__title">{{ t('myParticipationRequests.actorErrorTitle') }}</h2>
        <p class="resource-state__description">
          {{ accountsError.message }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshAccounts()">
            {{ t('common.retry') }}
          </button>
        </div>
      </section>

      <section
        v-else-if="accountsPending"
        class="resource-state"
        data-testid="my-participation-requests-actor-loading"
      >
        <h2 class="resource-state__title">{{ t('myParticipationRequests.actorLoadingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('myParticipationRequests.actorLoadingDescription') }}
        </p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="my-participation-requests-select-actor"
      >
        <h2 class="resource-state__title">{{ t('myParticipationRequests.selectActorTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('myParticipationRequests.selectActorDescription') }}
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="my-participation-requests-actor-missing"
      >
        <h2 class="resource-state__title">{{ t('myParticipationRequests.actorMissingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('myParticipationRequests.actorMissingDescription') }}
        </p>
      </section>

      <section
        v-else-if="!isTesterActor"
        class="resource-state"
        data-testid="my-participation-requests-role-mismatch"
      >
        <h2 class="resource-state__title">{{ t('myParticipationRequests.roleMismatchTitle') }}</h2>
        <p class="resource-state__description">
          {{
            t('myParticipationRequests.roleMismatchDescription', {
              role: formatAccountRolesLabel(currentActor, locale)
            })
          }}
        </p>
      </section>

      <template v-else>
        <section class="resource-section" data-testid="my-participation-requests-summary">
          <h2 class="resource-section__title">{{ t('myParticipationRequests.summaryTitle') }}</h2>
          <div class="app-page-summary-grid">
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">{{ t('myParticipationRequests.currentAccount') }}</span>
              <strong class="app-page-summary-card__value">{{ currentActor.display_name }}</strong>
              <span class="app-page-summary-card__description">{{ t('myParticipationRequests.currentAccountDescription') }}</span>
            </article>
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">{{ t('myParticipationRequests.requestsCount') }}</span>
              <strong class="app-page-summary-card__value">{{ requestResponse.total }}</strong>
              <span class="app-page-summary-card__description">{{ t('myParticipationRequests.requestsCountDescription') }}</span>
            </article>
          </div>
        </section>

        <section
          v-if="requestsPending"
          class="resource-state"
          data-testid="my-participation-requests-loading"
        >
          <h2 class="resource-state__title">{{ t('myParticipationRequests.loadingTitle') }}</h2>
          <p class="resource-state__description">
            {{ t('myParticipationRequests.loadingDescription') }}
          </p>
        </section>

        <section
          v-else-if="requestsError"
          class="resource-state"
          data-testid="my-participation-requests-error"
        >
          <h2 class="resource-state__title">{{ t('myParticipationRequests.errorTitle') }}</h2>
          <p class="resource-state__description">
            {{ requestsErrorMessage }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshRequests()">
              {{ t('common.retry') }}
            </button>
          </div>
        </section>

        <section
          v-else-if="participationRequests.length === 0"
          class="resource-state"
          data-testid="my-participation-requests-empty"
        >
          <h2 class="resource-state__title">{{ t('myParticipationRequests.emptyTitle') }}</h2>
          <p class="resource-state__description">
            {{ t('myParticipationRequests.emptyDescription') }}
          </p>
          <div class="resource-state__actions">
            <NuxtLink class="resource-action" to="/my/eligible-campaigns">
              {{ t('myParticipationRequests.viewEligibleCampaigns') }}
            </NuxtLink>
          </div>
        </section>

        <section
          v-else
          class="resource-section__body app-page-card-grid"
          data-testid="my-participation-requests-list"
        >
          <div
            v-if="actionError"
            class="resource-state"
            data-testid="my-participation-requests-action-error"
          >
            <h2 class="resource-state__title">{{ t('myParticipationRequests.actionErrorTitle') }}</h2>
            <p class="resource-state__description">
              {{ actionError }}
            </p>
          </div>

          <article
            v-for="request in participationRequests"
            :key="request.id"
            class="resource-card"
            :data-testid="`participation-request-card-${request.id}`"
          >
            <span class="resource-shell__breadcrumb">{{ t('myParticipationRequests.breadcrumb') }}</span>
            <h2 class="resource-card__title">{{ request.campaign_name }}</h2>
            <p class="resource-card__description">
              {{
                request.note
                  ? request.note
                  : t('myParticipationRequests.noteEmpty')
              }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">
                {{ t('myParticipationRequests.statusLabel') }} {{ formatParticipationRequestStatusLabel(request.status, locale) }}
              </span>
              <span class="resource-card__chip">
                {{ t('myParticipationRequests.deviceLabel') }} {{ request.device_profile_name }}
              </span>
              <span class="resource-card__chip">
                {{ t('myParticipationRequests.taskBridgeLabel') }} {{ formatParticipationAssignmentStatusLabel(request.assignment_status, locale) }}
              </span>
            </div>
            <div class="resource-card__meta">
              <span class="resource-card__chip">{{ t('myParticipationRequests.createdAtLabel') }} {{ request.created_at }}</span>
              <span class="resource-card__chip">{{ t('myParticipationRequests.updatedAtLabel') }} {{ request.updated_at }}</span>
            </div>
            <div
              v-if="request.decided_at || request.decision_note"
              class="resource-card__meta"
            >
              <span
                v-if="request.decided_at"
                class="resource-card__chip"
              >
                {{ t('myParticipationRequests.decidedAtLabel') }} {{ request.decided_at }}
              </span>
              <span
                v-if="request.decision_note"
                class="resource-card__chip"
              >
                {{ t('myParticipationRequests.decisionNoteLabel') }} {{ request.decision_note }}
              </span>
            </div>
            <div
              v-if="request.linked_task_id || request.status === 'accepted'"
              class="resource-card__meta"
            >
              <span
                v-if="request.assignment_created_at"
                class="resource-card__chip"
              >
                {{ t('myParticipationRequests.assignmentCreatedAtLabel') }} {{ request.assignment_created_at }}
              </span>
              <span
                v-else-if="request.status === 'accepted'"
                class="resource-card__chip"
              >
                {{ t('myParticipationRequests.acceptedAwaitingTask') }}
              </span>
            </div>
            <div class="resource-state__actions">
              <NuxtLink
                class="resource-action"
                :data-testid="`participation-request-campaign-link-${request.id}`"
                :to="`/campaigns/${request.campaign_id}`"
              >
                {{ t('myParticipationRequests.viewCampaign') }}
              </NuxtLink>
              <NuxtLink
                v-if="request.linked_task_id"
                class="resource-action"
                :data-testid="`participation-request-task-link-${request.id}`"
                :to="`/tasks/${request.linked_task_id}`"
              >
                {{ t('myParticipationRequests.viewLinkedTask') }}
              </NuxtLink>
              <button
                v-if="request.status === 'pending'"
                class="resource-action"
                type="button"
                :data-testid="`participation-request-withdraw-${request.id}`"
                :disabled="withdrawingRequestId === request.id"
                @click="handleWithdrawRequest(request.id)"
              >
                {{ withdrawingRequestId === request.id ? t('myParticipationRequests.withdrawing') : t('myParticipationRequests.withdraw') }}
              </button>
            </div>
          </article>
        </section>
      </template>
    </section>
  </main>
</template>
