<script setup lang="ts">
definePageMeta({
  path: '/review/participation-requests/:requestId'
})

import { computed } from 'vue'

import ActivityTimelinePanel from '~/features/activity-events/ActivityTimelinePanel.vue'
import { fetchParticipationRequestTimeline } from '~/features/activity-events/api'
import { fetchAccounts } from '~/features/accounts/api'
import {
  getActorAwareReadErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import { formatCampaignStatusLabel } from '~/features/campaigns/types'
import { formatQualificationStatusLabel } from '~/features/eligibility/types'
import { useAppI18n } from '~/features/i18n/use-app-i18n'
import {
  formatParticipationAssignmentStatusLabel,
  formatParticipationRequestStatusLabel
} from '~/features/participation-requests/types'
import { fetchParticipationRequestDetail } from '~/features/participation-requests/api'
import { formatPlatformLabel } from '~/features/platform-display'

useCurrentActorPersistence()
const { locale, t } = useAppI18n()

const route = useRoute()
const requestId = computed(() => String(route.params.requestId))
const currentActorId = useCurrentActorId()

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('review-participation-detail-accounts', () => fetchAccounts(), {
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
    `review-participation-request-detail-${requestId.value}-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
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

const testerSummary = computed(
  () => participationRequest.value?.tester_account_summary.tester_summary ?? null
)
const canCreateTaskFromRequest = computed(
  () =>
    participationRequest.value?.status === 'accepted'
    && !participationRequest.value.linked_task_id
)
const detailErrorMessage = computed(() =>
  getActorAwareReadErrorMessage(error.value, t('participationRequestDetail.errorTitle'))
)
const {
  data: timelineResponse,
  pending: timelinePending,
  error: timelineError
} = useAsyncData(
  () =>
    `review-participation-request-timeline-${requestId.value}-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
  async () => {
    if (!currentActorId.value || !isDeveloperActor.value) {
      return {
        items: [],
        total: 0
      }
    }

    return fetchParticipationRequestTimeline(requestId.value, currentActorId.value)
  },
  {
    server: false,
    watch: [requestId, currentActorId, currentActor],
    default: () => ({
      items: [],
      total: 0
    })
  }
)
const timelineEvents = computed(() => timelineResponse.value.items)
const timelineErrorMessage = computed(() =>
  timelineError.value
    ? getActorAwareReadErrorMessage(timelineError.value, t('participationRequestDetail.timelineTitle'))
    : null
)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/review/participation-requests">
          {{ t('participationRequestDetail.queueBreadcrumb') }}
        </NuxtLink>
        <h1 class="resource-shell__title">{{ t('participationRequestDetail.title') }}</h1>
        <p class="resource-shell__description">
          {{ t('participationRequestDetail.description') }}
        </p>
      </header>

      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="participation-request-detail-actor-error"
      >
        <h2 class="resource-state__title">{{ t('participationRequestDetail.actorErrorTitle') }}</h2>
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
        data-testid="participation-request-detail-actor-loading"
      >
        <h2 class="resource-state__title">{{ t('participationRequestDetail.actorLoadingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('participationRequestDetail.actorLoadingDescription') }}
        </p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="participation-request-detail-select-actor"
      >
        <h2 class="resource-state__title">{{ t('participationRequestDetail.selectActorTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('participationRequestDetail.selectActorDescription') }}
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="participation-request-detail-actor-missing"
      >
        <h2 class="resource-state__title">{{ t('participationRequestDetail.actorMissingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('participationRequestDetail.actorMissingDescription') }}
        </p>
      </section>

      <section
        v-else-if="!isDeveloperActor"
        class="resource-state"
        data-testid="participation-request-detail-role-mismatch"
      >
        <h2 class="resource-state__title">{{ t('participationRequestDetail.roleMismatchTitle') }}</h2>
        <p class="resource-state__description">
          {{
            t('participationRequestDetail.roleMismatchDescription', {
              role: formatAccountRoleLabel(currentActor.role, locale)
            })
          }}
        </p>
      </section>

      <section
        v-else-if="pending"
        class="resource-state"
        data-testid="participation-request-detail-loading"
      >
        <h2 class="resource-state__title">{{ t('participationRequestDetail.loadingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('participationRequestDetail.loadingDescription') }}
        </p>
      </section>

      <section
        v-else-if="error || !participationRequest"
        class="resource-state"
        data-testid="participation-request-detail-error"
      >
        <h2 class="resource-state__title">{{ t('participationRequestDetail.errorTitle') }}</h2>
        <p class="resource-state__description">
          {{ detailErrorMessage }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            {{ t('common.retry') }}
          </button>
          <NuxtLink class="resource-action" to="/review/participation-requests">
            {{ t('participationRequestDetail.backToQueue') }}
          </NuxtLink>
        </div>
      </section>

      <template v-else>
        <div class="detail-layout" data-testid="participation-request-detail-layout">
          <div class="detail-layout__main">
        <section
          class="resource-section"
          data-testid="participation-request-detail-panel"
        >
          <span class="resource-section__eyebrow">{{ t('participationRequestDetail.eyebrow') }}</span>
          <h2 class="resource-section__title">{{ participationRequest.campaign_name }}</h2>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              :to="`/campaigns/${participationRequest.campaign_id}`"
            >
              {{ t('participationRequestDetail.viewCampaign') }}
            </NuxtLink>
            <NuxtLink
              v-if="canCreateTaskFromRequest"
              class="resource-action"
              data-testid="participation-request-create-task-link"
              :to="`/review/participation-requests/${participationRequest.id}/tasks/new`"
            >
              {{ t('participationRequestDetail.createTask') }}
            </NuxtLink>
            <NuxtLink
              v-else-if="participationRequest.linked_task_id"
              class="resource-action"
              data-testid="participation-request-linked-task-link"
              :to="`/tasks/${participationRequest.linked_task_id}`"
            >
              {{ t('participationRequestDetail.viewLinkedTask') }}
            </NuxtLink>
            <NuxtLink class="resource-action" to="/review/participation-requests">
              {{ t('participationRequestDetail.backToQueue') }}
            </NuxtLink>
          </div>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              {{ t('participationRequestDetail.statusLabel') }} {{ formatParticipationRequestStatusLabel(participationRequest.status, locale) }}
            </span>
            <span class="resource-shell__meta-chip">
              {{ t('participationRequestDetail.deviceLabel') }} {{ participationRequest.device_profile_name }}
            </span>
            <span class="resource-shell__meta-chip">
              {{ t('participationRequestDetail.taskBridgeLabel') }} {{ formatParticipationAssignmentStatusLabel(participationRequest.assignment_status, locale) }}
            </span>
          </div>
          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.requestIdLabel') }}</span>
              <span class="resource-key-value__value">{{ participationRequest.id }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.testerNoteLabel') }}</span>
              <span class="resource-key-value__value">
                {{ participationRequest.note || t('participationRequestDetail.testerNoteEmpty') }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.decisionNoteLabel') }}</span>
              <span class="resource-key-value__value">
                {{ participationRequest.decision_note || t('participationRequestDetail.decisionNoteEmpty') }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.createdAtLabel') }}</span>
              <span class="resource-key-value__value">{{ participationRequest.created_at }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.updatedAtLabel') }}</span>
              <span class="resource-key-value__value">{{ participationRequest.updated_at }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.decidedAtLabel') }}</span>
              <span class="resource-key-value__value">
                {{ participationRequest.decided_at || t('participationRequestDetail.undecided') }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.linkedTaskLabel') }}</span>
              <NuxtLink
                v-if="participationRequest.linked_task_id"
                class="resource-key-value__value"
                :to="`/tasks/${participationRequest.linked_task_id}`"
              >
                {{ participationRequest.linked_task_id }}
              </NuxtLink>
              <span v-else class="resource-key-value__value">
                {{ t('participationRequestDetail.linkedTaskEmpty') }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.assignmentCreatedAtLabel') }}</span>
              <span class="resource-key-value__value">
                {{ participationRequest.assignment_created_at || t('participationRequestDetail.linkedTaskEmpty') }}
              </span>
            </div>
          </div>
        </section>

        <ActivityTimelinePanel
          :title="t('participationRequestDetail.timelineTitle')"
          :description="t('participationRequestDetail.timelineDescription')"
          :pending="timelinePending"
          :error-message="timelineErrorMessage"
          :events="timelineEvents"
          :empty-message="t('participationRequestDetail.timelineEmpty')"
          test-id-prefix="participation-request-timeline"
        />

        <section
          class="resource-section"
          data-testid="participation-request-tester-panel"
        >
          <h2 class="resource-section__title">{{ t('participationRequestDetail.testerPanelTitle') }}</h2>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              :to="`/accounts/${participationRequest.tester_account.id}`"
            >
              {{ t('participationRequestDetail.viewAccount') }}
            </NuxtLink>
          </div>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              {{ participationRequest.tester_account.display_name }}
            </span>
            <span class="resource-shell__meta-chip">
              {{ formatAccountRoleLabel(participationRequest.tester_account.role, locale) }}
            </span>
          </div>
          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.accountIdLabel') }}</span>
              <span class="resource-key-value__value">{{ participationRequest.tester_account.id }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.localeLabel') }}</span>
              <span class="resource-key-value__value">
                {{ participationRequest.tester_account.locale || t('participationRequestDetail.notProvided') }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.bioLabel') }}</span>
              <span class="resource-key-value__value">
                {{ participationRequest.tester_account.bio || t('participationRequestDetail.notProvided') }}
              </span>
            </div>
            <div
              v-if="testerSummary"
              class="resource-key-value__row"
            >
              <span class="resource-key-value__label">{{ t('participationRequestDetail.ownedDeviceProfilesCount') }}</span>
              <span class="resource-key-value__value">{{ testerSummary.owned_device_profiles_count }}</span>
            </div>
            <div
              v-if="testerSummary"
              class="resource-key-value__row"
            >
              <span class="resource-key-value__label">{{ t('participationRequestDetail.assignedTasksCount') }}</span>
              <span class="resource-key-value__value">{{ testerSummary.assigned_tasks_count }}</span>
            </div>
            <div
              v-if="testerSummary"
              class="resource-key-value__row"
            >
              <span class="resource-key-value__label">{{ t('participationRequestDetail.submittedFeedbackCount') }}</span>
              <span class="resource-key-value__value">{{ testerSummary.submitted_feedback_count }}</span>
            </div>
          </div>
        </section>

        <section
          class="resource-section"
          data-testid="participation-request-device-profile-panel"
        >
          <h2 class="resource-section__title">{{ t('participationRequestDetail.deviceProfilePanelTitle') }}</h2>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              :to="`/device-profiles/${participationRequest.device_profile.id}`"
            >
              {{ t('participationRequestDetail.viewDeviceProfile') }}
            </NuxtLink>
          </div>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              {{ formatPlatformLabel(participationRequest.device_profile.platform, locale) }}
            </span>
            <span class="resource-shell__meta-chip">
              {{ t('participationRequestDetail.installChannelLabel') }} {{ participationRequest.device_profile.install_channel || t('participationRequestDetail.notProvided') }}
            </span>
          </div>
          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.deviceProfileIdLabel') }}</span>
              <span class="resource-key-value__value">{{ participationRequest.device_profile.id }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.deviceModelLabel') }}</span>
              <span class="resource-key-value__value">{{ participationRequest.device_profile.device_model }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.osLabel') }}</span>
              <span class="resource-key-value__value">
                {{ participationRequest.device_profile.os_name }} {{ participationRequest.device_profile.os_version || '' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.submissionRateLabel') }}</span>
              <span class="resource-key-value__value">
                {{ participationRequest.device_profile_reputation.submission_rate.toFixed(2) }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.tasksAssignedCount') }}</span>
              <span class="resource-key-value__value">{{ participationRequest.device_profile_reputation.tasks_assigned_count }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.feedbackSubmittedCount') }}</span>
              <span class="resource-key-value__value">{{ participationRequest.device_profile_reputation.feedback_submitted_count }}</span>
            </div>
          </div>
        </section>

          </div>

          <aside class="detail-layout__rail">

        <section
          class="resource-section"
          data-testid="participation-request-qualification-panel"
        >
          <span class="resource-section__eyebrow">{{ t('participationRequestDetail.qualificationEyebrow') }}</span>
          <h2 class="resource-section__title">{{ t('participationRequestDetail.qualificationPanelTitle') }}</h2>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              {{ t('participationRequestDetail.qualificationStatusLabel') }} {{ formatQualificationStatusLabel(participationRequest.qualification_snapshot.qualification_status, locale) }}
            </span>
          </div>
          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.matchedRuleLabel') }}</span>
              <span class="resource-key-value__value">
                {{ participationRequest.qualification_snapshot.matched_rule_id || t('participationRequestDetail.matchedRuleEmpty') }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.qualificationSummaryLabel') }}</span>
              <span class="resource-key-value__value">
                {{ participationRequest.qualification_snapshot.reason_summary || t('participationRequestDetail.qualificationSummaryEmpty') }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.reasonCodesLabel') }}</span>
              <span class="resource-key-value__value">
                {{
                  participationRequest.qualification_snapshot.reason_codes.length > 0
                    ? participationRequest.qualification_snapshot.reason_codes.join(', ')
                    : t('participationRequestDetail.reasonCodesEmpty')
                }}
              </span>
            </div>
          </div>
        </section>

        <section
          class="resource-section"
          data-testid="participation-request-campaign-panel"
        >
          <span class="resource-section__eyebrow">{{ t('participationRequestDetail.campaignEyebrow') }}</span>
          <h2 class="resource-section__title">{{ t('participationRequestDetail.campaignPanelTitle') }}</h2>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              :to="`/campaigns/${participationRequest.campaign.id}`"
            >
              {{ t('participationRequestDetail.viewCampaignDetail') }}
            </NuxtLink>
          </div>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              {{ formatCampaignStatusLabel(participationRequest.campaign.status, locale) }}
            </span>
            <span class="resource-shell__meta-chip">
              {{ t('participationRequestDetail.platformsLabel') }}
              {{
                participationRequest.campaign.target_platforms
                  .map((platform) => formatPlatformLabel(platform, locale))
                  .join(' / ')
              }}
            </span>
          </div>
          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.campaignIdLabel') }}</span>
              <span class="resource-key-value__value">{{ participationRequest.campaign.id }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('participationRequestDetail.versionLabel') }}</span>
              <span class="resource-key-value__value">
                {{ participationRequest.campaign.version_label || t('participationRequestDetail.versionEmpty') }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('campaignDetail.tasksClosedLabel') }}</span>
              <span class="resource-key-value__value">{{ participationRequest.campaign_reputation.tasks_closed_count }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('campaignDetail.feedbackReceivedLabel') }}</span>
              <span class="resource-key-value__value">{{ participationRequest.campaign_reputation.feedback_received_count }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('campaignDetail.closureRateLabel') }}</span>
              <span class="resource-key-value__value">
                {{ participationRequest.campaign_reputation.closure_rate.toFixed(2) }}
              </span>
            </div>
          </div>
        </section>
          </aside>
        </div>
      </template>
    </section>
  </main>
</template>
