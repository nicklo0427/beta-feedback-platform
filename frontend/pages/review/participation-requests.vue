<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import {
  getActorAwareReadErrorMessage,
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import {
  decideParticipationRequest,
  fetchReviewParticipationRequests
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
const decidingRequestId = ref<string | null>(null)
const decisionNoteDrafts = ref<Record<string, string>>({})

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('review-participation-requests-accounts', () => fetchAccounts(), {
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
  data: queueResponse,
  pending: queuePending,
  error: queueError,
  refresh: refreshQueue
} = useAsyncData(
  () =>
    `review-participation-requests-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
  async () => {
    if (!currentActorId.value || !isDeveloperActor.value) {
      return {
        items: [],
        total: 0
      }
    }

    return fetchReviewParticipationRequests(currentActorId.value)
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

const participationRequests = computed(() => queueResponse.value.items)
const pendingRequestsCount = computed(
  () => participationRequests.value.filter((request) => request.status === 'pending').length
)
const acceptedRequestsCount = computed(
  () =>
    participationRequests.value.filter(
      (request) => request.status === 'accepted' && request.assignment_status === 'not_assigned'
    ).length
)
const involvedCampaignCount = computed(
  () => new Set(participationRequests.value.map((request) => request.campaign_id)).size
)
const queueErrorMessage = computed(() =>
  getActorAwareReadErrorMessage(
    queueError.value,
    '目前無法載入參與申請審查列表。'
  )
)

async function handleDecision(
  requestId: string,
  status: 'accepted' | 'declined'
): Promise<void> {
  actionError.value = null
  decidingRequestId.value = requestId

  try {
    if (!currentActorId.value) {
      actionError.value = t('errors.mutation.missingActorContext')
      return
    }

    await decideParticipationRequest(
      requestId,
      {
        status,
        decision_note: decisionNoteDrafts.value[requestId]?.trim() || null
      },
      currentActorId.value
    )
    await refreshQueue()
  } catch (decisionFailure) {
    actionError.value = getActorAwareMutationErrorMessage(
      decisionFailure,
      t('reviewParticipation.actionErrorTitle')
    )
  } finally {
    decidingRequestId.value = null
  }
}

watch(participationRequests, (items) => {
  const nextDrafts: Record<string, string> = {}

  for (const request of items) {
    nextDrafts[request.id] =
      decisionNoteDrafts.value[request.id] ?? request.decision_note ?? ''
  }

  decisionNoteDrafts.value = nextDrafts
})

watch([currentActorId, currentActor], () => {
  actionError.value = null
  decidingRequestId.value = null
})
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header app-page-header">
        <NuxtLink class="resource-shell__breadcrumb" to="/dashboard">Dashboard</NuxtLink>
        <h1 class="resource-shell__title">{{ t('reviewParticipation.title') }}</h1>
        <p class="resource-shell__description">
          {{ t('reviewParticipation.description') }}
        </p>
      </header>
      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="participation-review-actor-error"
      >
        <h2 class="resource-state__title">{{ t('reviewParticipation.actorErrorTitle') }}</h2>
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
        data-testid="participation-review-actor-loading"
      >
        <h2 class="resource-state__title">{{ t('reviewParticipation.actorLoadingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('reviewParticipation.actorLoadingDescription') }}
        </p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="participation-review-select-actor"
      >
        <h2 class="resource-state__title">{{ t('reviewParticipation.selectActorTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('reviewParticipation.selectActorDescription') }}
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="participation-review-actor-missing"
      >
        <h2 class="resource-state__title">{{ t('reviewParticipation.actorMissingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('reviewParticipation.actorMissingDescription') }}
        </p>
      </section>

      <section
        v-else-if="!isDeveloperActor"
        class="resource-state"
        data-testid="participation-review-role-mismatch"
      >
        <h2 class="resource-state__title">{{ t('reviewParticipation.roleMismatchTitle') }}</h2>
        <p class="resource-state__description">
          {{
            t('reviewParticipation.roleMismatchDescription', {
              role: formatAccountRoleLabel(currentActor.role, locale)
            })
          }}
        </p>
      </section>

      <template v-else>
        <section class="resource-section" data-testid="participation-review-summary">
          <h2 class="resource-section__title">{{ t('reviewParticipation.summaryTitle') }}</h2>
          <div class="app-page-summary-grid">
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">{{ t('reviewParticipation.currentAccount') }}</span>
              <strong class="app-page-summary-card__value">{{ currentActor.display_name }}</strong>
              <span class="app-page-summary-card__description">{{ t('reviewParticipation.currentAccountDescription') }}</span>
            </article>
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">{{ t('reviewParticipation.queueCount') }}</span>
              <strong class="app-page-summary-card__value">{{ queueResponse.total }}</strong>
              <span class="app-page-summary-card__description">{{ t('reviewParticipation.queueCountDescription') }}</span>
            </article>
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">{{ t('reviewParticipation.pendingCount') }}</span>
              <strong class="app-page-summary-card__value">{{ pendingRequestsCount }}</strong>
              <span class="app-page-summary-card__description">{{ t('reviewParticipation.pendingCountDescription') }}</span>
            </article>
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">{{ t('reviewParticipation.acceptedCount') }}</span>
              <strong class="app-page-summary-card__value">{{ acceptedRequestsCount }}</strong>
              <span class="app-page-summary-card__description">{{ t('reviewParticipation.acceptedCountDescription') }}</span>
            </article>
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">{{ t('reviewParticipation.campaignCount') }}</span>
              <strong class="app-page-summary-card__value">{{ involvedCampaignCount }}</strong>
              <span class="app-page-summary-card__description">{{ t('reviewParticipation.campaignCountDescription') }}</span>
            </article>
          </div>
        </section>

        <section
          v-if="queuePending"
          class="resource-state"
          data-testid="participation-review-loading"
        >
          <h2 class="resource-state__title">{{ t('reviewParticipation.loadingTitle') }}</h2>
          <p class="resource-state__description">
            {{ t('reviewParticipation.loadingDescription') }}
          </p>
        </section>

        <section
          v-else-if="queueError"
          class="resource-state"
          data-testid="participation-review-error"
        >
          <h2 class="resource-state__title">{{ t('reviewParticipation.errorTitle') }}</h2>
          <p class="resource-state__description">
            {{ queueErrorMessage }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshQueue()">
              {{ t('common.retry') }}
            </button>
          </div>
        </section>

        <section
          v-else-if="participationRequests.length === 0"
          class="resource-state"
          data-testid="participation-review-empty"
        >
          <h2 class="resource-state__title">{{ t('reviewParticipation.emptyTitle') }}</h2>
          <p class="resource-state__description">
            {{ t('reviewParticipation.emptyDescription') }}
          </p>
        </section>

        <section
          v-else
          class="resource-section__body app-page-card-grid"
          data-testid="participation-review-list"
        >
          <div
            v-if="actionError"
            class="resource-state"
            data-testid="participation-review-action-error"
          >
            <h2 class="resource-state__title">{{ t('reviewParticipation.actionErrorTitle') }}</h2>
            <p class="resource-state__description">
              {{ actionError }}
            </p>
          </div>

          <article
            v-for="request in participationRequests"
            :key="request.id"
            class="resource-card"
            :data-testid="`review-participation-request-card-${request.id}`"
          >
            <span class="resource-shell__breadcrumb">{{ t('reviewParticipation.breadcrumb') }}</span>
            <h2 class="resource-card__title">{{ request.campaign_name }}</h2>
            <p class="resource-card__description">
              {{ t('reviewParticipation.testerSummary', { testerId: request.tester_account_id, deviceName: request.device_profile_name }) }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">
                {{ t('myParticipationRequests.statusLabel') }} {{ formatParticipationRequestStatusLabel(request.status, locale) }}
              </span>
              <span class="resource-card__chip">
                {{ t('myParticipationRequests.taskBridgeLabel') }} {{ formatParticipationAssignmentStatusLabel(request.assignment_status, locale) }}
              </span>
              <span class="resource-card__chip">{{ t('myParticipationRequests.createdAtLabel') }} {{ request.created_at }}</span>
              <span
                v-if="request.assignment_created_at"
                class="resource-card__chip"
              >
                {{ t('myParticipationRequests.assignmentCreatedAtLabel') }} {{ request.assignment_created_at }}
              </span>
            </div>
            <p
              v-if="request.note"
              class="resource-card__description"
            >
              {{ t('reviewParticipation.testerNote', { note: request.note }) }}
            </p>
            <p
              v-if="request.decision_note"
              class="resource-card__description"
            >
              {{ t('reviewParticipation.decisionNote', { note: request.decision_note }) }}
            </p>
            <label
              v-if="request.status === 'pending'"
              class="resource-field"
              :for="`participation-review-note-${request.id}`"
            >
              <span class="resource-field__label">{{ t('reviewParticipation.decisionNoteLabel') }}</span>
              <textarea
                :id="`participation-review-note-${request.id}`"
                v-model="decisionNoteDrafts[request.id]"
                class="resource-textarea"
                rows="3"
                :data-testid="`review-participation-decision-note-${request.id}`"
                :placeholder="t('reviewParticipation.decisionNotePlaceholder')"
              />
            </label>
            <div class="resource-state__actions">
              <NuxtLink
                class="resource-action"
                :data-testid="`review-participation-detail-link-${request.id}`"
                :to="`/review/participation-requests/${request.id}`"
              >
                {{ t('reviewParticipation.viewDetail') }}
              </NuxtLink>
              <NuxtLink
                class="resource-action"
                :data-testid="`review-participation-campaign-link-${request.id}`"
                :to="`/campaigns/${request.campaign_id}`"
              >
                {{ t('reviewParticipation.viewCampaign') }}
              </NuxtLink>
              <template v-if="request.status === 'pending'">
                <button
                  class="resource-action"
                  type="button"
                  :disabled="decidingRequestId === request.id"
                  :data-testid="`review-participation-accept-${request.id}`"
                  @click="handleDecision(request.id, 'accepted')"
                >
                  {{ decidingRequestId === request.id ? t('reviewParticipation.processing') : t('reviewParticipation.accept') }}
                </button>
                <button
                  class="resource-action"
                  type="button"
                  :disabled="decidingRequestId === request.id"
                  :data-testid="`review-participation-decline-${request.id}`"
                  @click="handleDecision(request.id, 'declined')"
                >
                  {{ decidingRequestId === request.id ? t('reviewParticipation.processing') : t('reviewParticipation.decline') }}
                </button>
              </template>
              <NuxtLink
                v-else-if="request.status === 'accepted' && !request.linked_task_id"
                class="resource-action"
                :data-testid="`review-participation-create-task-${request.id}`"
                :to="`/review/participation-requests/${request.id}/tasks/new`"
              >
                {{ t('reviewParticipation.createTask') }}
              </NuxtLink>
              <NuxtLink
                v-else-if="request.linked_task_id"
                class="resource-action"
                :data-testid="`review-participation-linked-task-${request.id}`"
                :to="`/tasks/${request.linked_task_id}`"
              >
                {{ t('reviewParticipation.viewLinkedTask') }}
              </NuxtLink>
            </div>
          </article>
        </section>
      </template>
    </section>
  </main>
</template>
