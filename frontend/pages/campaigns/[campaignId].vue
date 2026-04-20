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
import { fetchCampaignDetail } from '~/features/campaigns/api'
import { formatCampaignStatusLabel } from '~/features/campaigns/types'
import {
  fetchCampaignEligibilityRules,
  fetchCampaignQualificationResults
} from '~/features/eligibility/api'
import { formatQualificationStatusLabel } from '~/features/eligibility/types'
import { formatPlatformLabel } from '~/features/platform-display'
import { fetchCampaignReputation } from '~/features/reputation/api'
import ParticipationRequestForm from '~/features/participation-requests/ParticipationRequestForm.vue'
import {
  createParticipationRequest
} from '~/features/participation-requests/api'
import { buildParticipationRequestCreatePayload, createEmptyParticipationRequestFormValues } from '~/features/participation-requests/form'
import type { ParticipationRequestFormValues } from '~/features/participation-requests/types'
import { fetchCampaignSafety } from '~/features/safety/api'
import {
  formatDistributionChannelLabel,
  formatReviewStatusLabel,
  formatRiskLevelLabel
} from '~/features/safety/types'
import { fetchTasks } from '~/features/tasks/api'
import { formatTaskStatusLabel } from '~/features/tasks/types'
import { useAppI18n } from '~/features/i18n/use-app-i18n'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const campaignId = computed(() => String(route.params.campaignId))

useCurrentActorPersistence()
const { locale, t } = useAppI18n()

const currentActorId = useCurrentActorId()

const {
  data: campaign,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `campaign-detail-${campaignId.value}`,
  () => fetchCampaignDetail(campaignId.value),
  {
    server: false,
    watch: [campaignId],
    default: () => null
  }
)

const {
  data: eligibilityRuleResponse,
  pending: eligibilityPending,
  error: eligibilityError,
  refresh: refreshEligibility
} = useAsyncData(
  () => `campaign-eligibility-${campaignId.value}-${currentActorId.value ?? 'none'}`,
  () => fetchCampaignEligibilityRules(campaignId.value, currentActorId.value),
  {
    server: false,
    watch: [campaignId, currentActorId],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const eligibilityRules = computed(() => eligibilityRuleResponse.value.items)

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('campaign-detail-accounts', () => fetchAccounts(), {
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
const isTesterActor = computed(() => currentActor.value?.role === 'tester')

const {
  data: qualificationResponse,
  pending: qualificationPending,
  error: qualificationError,
  refresh: refreshQualification
} = useAsyncData(
  () =>
    `campaign-qualification-${campaignId.value}-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
  async () => {
    if (!currentActorId.value || !isTesterActor.value) {
      return {
        items: [],
        total: 0
      }
    }

    return fetchCampaignQualificationResults(campaignId.value, currentActorId.value)
  },
  {
    server: false,
    watch: [campaignId, currentActorId, currentActor],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const qualificationResults = computed(() => qualificationResponse.value.items)
const qualifiedParticipationDeviceProfiles = computed(() =>
  qualificationResults.value
    .filter((result) => result.qualification_status === 'qualified')
    .map((result) => ({
      id: result.device_profile_id,
      name: result.device_profile_name
    }))
)
const participationInitialValues = computed(() =>
  createEmptyParticipationRequestFormValues(
    qualifiedParticipationDeviceProfiles.value[0]?.id ?? ''
  )
)
const qualificationErrorMessage = computed(() => {
  if (!(qualificationError.value instanceof ApiClientError)) {
    return qualificationError.value?.message || t('campaignDetail.qualificationErrorFallback')
  }

  if (qualificationError.value.code === 'missing_actor_context') {
    return t('campaignDetail.qualificationNoActor')
  }

  if (qualificationError.value.code === 'forbidden_actor_role') {
    return t('campaignDetail.qualificationForbiddenRole')
  }

  return qualificationError.value.message
})
const participationPending = ref(false)
const participationErrorMessage = ref<string | null>(null)
const participationSuccessMessage = ref<string | null>(null)

const {
  data: safety,
  pending: safetyPending,
  error: safetyError,
  refresh: refreshSafety
} = useAsyncData(
  () => `campaign-safety-${campaignId.value}-${currentActorId.value ?? 'none'}`,
  () => fetchCampaignSafety(campaignId.value, currentActorId.value),
  {
    server: false,
    watch: [campaignId, currentActorId],
    default: () => null
  }
)

const {
  data: taskResponse,
  pending: tasksPending,
  error: tasksError,
  refresh: refreshTasks
} = useAsyncData(
  () => `campaign-tasks-${campaignId.value}-${currentActorId.value ?? 'none'}`,
  () =>
    fetchTasks({
      campaignId: campaignId.value,
      actorId: currentActorId.value
    }),
  {
    server: false,
    watch: [campaignId, currentActorId],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const tasks = computed(() => taskResponse.value.items)

const {
  data: reputation,
  pending: reputationPending,
  error: reputationError,
  refresh: refreshReputation
} = useAsyncData(
  () => `campaign-reputation-${campaignId.value}-${currentActorId.value ?? 'none'}`,
  () => fetchCampaignReputation(campaignId.value, currentActorId.value),
  {
    server: false,
    watch: [campaignId, currentActorId],
    default: () => null
  }
)

const hasReputationSignals = computed(() => {
  if (!reputation.value) {
    return false
  }

  return (
    reputation.value.tasks_total_count > 0
    || reputation.value.tasks_closed_count > 0
    || reputation.value.feedback_received_count > 0
    || reputation.value.last_feedback_at !== null
  )
})

async function handleCreateParticipationRequest(
  values: ParticipationRequestFormValues
): Promise<void> {
  participationErrorMessage.value = null
  participationSuccessMessage.value = null
  participationPending.value = true

  try {
    if (!currentActorId.value) {
      participationErrorMessage.value = t('campaignDetail.participationNoActor')
      return
    }

    await createParticipationRequest(
      campaignId.value,
      buildParticipationRequestCreatePayload(values),
      currentActorId.value
    )
    participationSuccessMessage.value = t('campaignDetail.participationSuccess')
  } catch (submitFailure) {
    participationErrorMessage.value = getActorAwareMutationErrorMessage(
      submitFailure,
      t('campaignDetail.participationFallback')
    )
  } finally {
    participationPending.value = false
  }
}

watch([campaignId, currentActorId], () => {
  participationErrorMessage.value = null
  participationSuccessMessage.value = null
})
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/campaigns">{{ t('campaignDetail.breadcrumb') }}</NuxtLink>
        <h1 class="resource-shell__title">{{ t('campaignDetail.title') }}</h1>
        <p class="resource-shell__description">
          {{ t('campaignDetail.description') }}
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="campaign-detail-loading"
      >
          <h2 class="resource-state__title">{{ t('campaignDetail.loadingTitle') }}</h2>
          <p class="resource-state__description">
            {{ t('campaignDetail.loadingDescription') }}
          </p>
      </section>

      <section
        v-else-if="error || !campaign"
        class="resource-state"
        data-testid="campaign-detail-error"
      >
          <h2 class="resource-state__title">{{ t('campaignDetail.errorTitle') }}</h2>
          <p class="resource-state__description">
            {{ error?.message || t('campaignDetail.errorFallback') }}
          </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            {{ t('common.retry') }}
          </button>
          <NuxtLink class="resource-action" to="/campaigns">
            {{ t('campaignDetail.backToCampaigns') }}
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="campaign-detail-panel"
      >
        <h2 class="resource-section__title">{{ campaign.name }}</h2>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="campaign-edit-link"
            :to="`/campaigns/${campaign.id}/edit`"
          >
            {{ t('campaignDetail.editCampaign') }}
          </NuxtLink>
        </div>

        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">{{ t('campaignDetail.statusLabel') }} {{ formatCampaignStatusLabel(campaign.status, locale) }}</span>
          <span
            v-for="platform in campaign.target_platforms"
            :key="platform"
            class="resource-shell__meta-chip"
          >
            {{ formatPlatformLabel(platform) }}
          </span>
        </div>

        <div class="resource-key-value">
          <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('campaignDetail.campaignIdLabel') }}</span>
            <span class="resource-key-value__value">{{ campaign.id }}</span>
          </div>
          <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('campaignDetail.projectIdLabel') }}</span>
            <NuxtLink
              class="resource-key-value__value"
              :to="`/projects/${campaign.project_id}`"
            >
              {{ campaign.project_id }}
            </NuxtLink>
          </div>
          <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('campaignDetail.versionLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ campaign.version_label || t('campaignDetail.versionEmpty') }}
                </span>
          </div>
          <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('campaignDetail.updatedAtLabel') }}</span>
            <span class="resource-key-value__value">{{ campaign.updated_at }}</span>
          </div>
          <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('campaignDetail.createdAtLabel') }}</span>
            <span class="resource-key-value__value">{{ campaign.created_at }}</span>
          </div>
          <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('campaignDetail.descriptionLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ campaign.description || t('campaignDetail.descriptionEmpty') }}
                </span>
              </div>
            </div>
          </section>

      <section
        v-if="!pending && !error && campaign"
        class="resource-section"
        data-testid="campaign-reputation-section"
      >
        <h2 class="resource-section__title">{{ t('campaignDetail.reputationTitle') }}</h2>

        <div
          v-if="reputationPending"
          class="resource-state"
          data-testid="campaign-reputation-loading"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.reputationLoadingTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.reputationLoadingDescription') }}
          </p>
        </div>

        <div
          v-else-if="reputationError"
          class="resource-state"
          data-testid="campaign-reputation-error"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.reputationErrorTitle') }}</h3>
          <p class="resource-state__description">
            {{ getActorAwareReadErrorMessage(reputationError, t('campaignDetail.reputationErrorFallback')) }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshReputation()">
              {{ t('common.retry') }}
            </button>
          </div>
        </div>

        <div
          v-else-if="reputation && !hasReputationSignals"
          class="resource-state"
          data-testid="campaign-reputation-zero"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.reputationZeroTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.reputationZeroDescription') }}
          </p>
        </div>

        <div
          v-else-if="reputation"
          class="resource-section"
          data-testid="campaign-reputation-panel"
        >
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              {{ t('campaignDetail.closureRateLabel') }} {{ reputation.closure_rate.toFixed(2) }}
            </span>
            <span class="resource-shell__meta-chip">
              {{ t('campaignDetail.feedbackCountLabel') }} {{ reputation.feedback_received_count }}
            </span>
          </div>

          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('campaignDetail.tasksTotalLabel') }}</span>
              <span class="resource-key-value__value">
                {{ reputation.tasks_total_count }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('campaignDetail.tasksClosedLabel') }}</span>
              <span class="resource-key-value__value">
                {{ reputation.tasks_closed_count }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('campaignDetail.feedbackReceivedLabel') }}</span>
              <span class="resource-key-value__value">
                {{ reputation.feedback_received_count }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('campaignDetail.lastFeedbackAtLabel') }}</span>
              <span class="resource-key-value__value">
                {{ reputation.last_feedback_at || t('campaignDetail.lastFeedbackAtEmpty') }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('campaignDetail.updatedAtLabel') }}</span>
              <span class="resource-key-value__value">{{ reputation.updated_at }}</span>
            </div>
          </div>
        </div>
      </section>

      <section
        v-if="!pending && !error && campaign"
        class="resource-section"
        data-testid="campaign-safety-section"
      >
        <h2 class="resource-section__title">{{ t('campaignDetail.safetyTitle') }}</h2>

        <div
          v-if="safetyPending"
          class="resource-state"
          data-testid="campaign-safety-loading"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.safetyLoadingTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.safetyLoadingDescription') }}
          </p>
        </div>

        <div
          v-else-if="safetyError"
          class="resource-state"
          data-testid="campaign-safety-error"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.safetyErrorTitle') }}</h3>
          <p class="resource-state__description">
            {{ getActorAwareReadErrorMessage(safetyError, t('campaignDetail.safetyErrorFallback')) }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshSafety()">
              {{ t('common.retry') }}
            </button>
          </div>
        </div>

        <div
          v-else-if="!safety"
          class="resource-state"
          data-testid="campaign-safety-empty"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.safetyEmptyTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.safetyEmptyDescription') }}
          </p>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              data-testid="campaign-safety-create-link"
              :to="`/campaigns/${campaignId}/safety/new`"
            >
              {{ t('campaignDetail.createSafety') }}
            </NuxtLink>
          </div>
        </div>

        <div
          v-else
          class="resource-section"
          data-testid="campaign-safety-panel"
        >
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              data-testid="campaign-safety-edit-link"
              :to="`/campaigns/${campaignId}/safety/edit`"
            >
              {{ t('campaignDetail.editSafety') }}
            </NuxtLink>
          </div>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              {{ t('campaignDetail.riskLabel') }} {{ formatRiskLevelLabel(safety.risk_level, locale) }}
            </span>
            <span class="resource-shell__meta-chip">
              {{ t('campaignDetail.reviewStatusLabel') }} {{ formatReviewStatusLabel(safety.review_status, locale) }}
            </span>
            <span class="resource-shell__meta-chip">
              {{ t('campaignDetail.officialChannelOnlyLabel') }} {{ safety.official_channel_only ? t('campaignDetail.yes') : t('campaignDetail.no') }}
            </span>
          </div>

          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('campaignDetail.sourceLabelLabel') }}</span>
              <span class="resource-key-value__value">{{ safety.source_label }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('campaignDetail.distributionChannelLabel') }}</span>
              <span class="resource-key-value__value">
                {{ formatDistributionChannelLabel(safety.distribution_channel, locale) }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('campaignDetail.sourceUrlLabel') }}</span>
              <a
                v-if="safety.source_url"
                class="resource-key-value__value"
                :href="safety.source_url"
                target="_blank"
                rel="noreferrer"
              >
                {{ safety.source_url }}
              </a>
              <span v-else class="resource-key-value__value">
                {{ t('campaignDetail.sourceUrlEmpty') }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('campaignDetail.riskNoteLabel') }}</span>
              <span class="resource-key-value__value">
                {{ safety.risk_note || t('campaignDetail.riskNoteEmpty') }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">{{ t('campaignDetail.updatedAtLabel') }}</span>
              <span class="resource-key-value__value">{{ safety.updated_at }}</span>
            </div>
          </div>
        </div>
      </section>

      <section
        v-if="!pending && !error && campaign"
        class="resource-section"
        data-testid="campaign-eligibility-section"
      >
        <h2 class="resource-section__title">{{ t('campaignDetail.eligibilityTitle') }}</h2>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="eligibility-rule-create-link"
            :to="`/campaigns/${campaignId}/eligibility-rules/new`"
          >
            {{ t('campaignDetail.createEligibilityRule') }}
          </NuxtLink>
        </div>

        <div
          v-if="eligibilityPending"
          class="resource-state"
          data-testid="campaign-eligibility-loading"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.eligibilityLoadingTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.eligibilityLoadingDescription') }}
          </p>
        </div>

        <div
          v-else-if="eligibilityError"
          class="resource-state"
          data-testid="campaign-eligibility-error"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.eligibilityErrorTitle') }}</h3>
          <p class="resource-state__description">
            {{ getActorAwareReadErrorMessage(eligibilityError, t('campaignDetail.eligibilityErrorFallback')) }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshEligibility()">
              {{ t('common.retry') }}
            </button>
          </div>
        </div>

        <div
          v-else-if="eligibilityRules.length === 0"
          class="resource-state"
          data-testid="campaign-eligibility-empty"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.eligibilityEmptyTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.eligibilityEmptyDescription') }}
          </p>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              data-testid="eligibility-rule-empty-create-link"
              :to="`/campaigns/${campaignId}/eligibility-rules/new`"
            >
              {{ t('campaignDetail.createFirstEligibilityRule') }}
            </NuxtLink>
          </div>
        </div>

        <div
          v-else
          class="resource-section__body"
          data-testid="campaign-eligibility-list"
        >
          <NuxtLink
            v-for="eligibilityRule in eligibilityRules"
            :key="eligibilityRule.id"
            class="resource-card"
            :data-testid="`eligibility-rule-card-${eligibilityRule.id}`"
            :to="`/campaigns/${campaign.id}/eligibility-rules/${eligibilityRule.id}`"
          >
            <span class="resource-shell__breadcrumb">{{ t('campaignDetail.eligibilityBreadcrumb') }}</span>
            <h3 class="resource-card__title">
              {{ formatPlatformLabel(eligibilityRule.platform) }}
            </h3>
            <p class="resource-card__description">
              {{
                eligibilityRule.os_name
                  ? t('campaignDetail.osNameDescription', { osName: eligibilityRule.os_name })
                  : t('campaignDetail.osNameEmpty')
              }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">
                {{ t('campaignDetail.activeLabel') }} {{ eligibilityRule.is_active ? t('campaignDetail.yes') : t('campaignDetail.no') }}
              </span>
              <span class="resource-card__chip">
                {{
                  eligibilityRule.install_channel
                    ? `${t('campaignDetail.installChannelLabel')} ${eligibilityRule.install_channel}`
                    : t('campaignDetail.installChannelEmpty')
                }}
              </span>
            </div>
          </NuxtLink>
        </div>
      </section>

      <section
        v-if="!pending && !error && campaign"
        class="resource-section"
        data-testid="campaign-qualification-section"
      >
        <h2 class="resource-section__title">{{ t('campaignDetail.qualificationTitle') }}</h2>

        <section
          v-if="accountsError"
          class="resource-state"
          data-testid="campaign-qualification-actor-error"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.actorErrorTitle') }}</h3>
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
          data-testid="campaign-qualification-actor-loading"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.actorLoadingTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.qualificationActorLoadingDescription') }}
          </p>
        </section>

        <section
          v-else-if="!currentActorId"
          class="resource-state"
          data-testid="campaign-qualification-select-actor"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.qualificationSelectActorTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.qualificationSelectActorDescription') }}
          </p>
        </section>

        <section
          v-else-if="!currentActor"
          class="resource-state"
          data-testid="campaign-qualification-actor-missing"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.qualificationActorMissingTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.qualificationActorMissingDescription') }}
          </p>
        </section>

        <section
          v-else-if="!isTesterActor"
          class="resource-state"
          data-testid="campaign-qualification-role-mismatch"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.qualificationRoleMismatchTitle') }}</h3>
          <p class="resource-state__description">
            {{
              t('campaignDetail.qualificationRoleMismatchDescription', {
                role: formatAccountRoleLabel(currentActor.role, locale)
              })
            }}
          </p>
        </section>

        <template v-else>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              {{ t('campaignDetail.qualificationCurrentAccount') }} {{ currentActor.display_name }}
            </span>
            <span class="resource-shell__meta-chip">
              {{ t('campaignDetail.qualificationResultsLabel') }} {{ qualificationResponse.total }}
            </span>
          </div>

          <section
            v-if="qualificationPending"
            class="resource-state"
            data-testid="campaign-qualification-loading"
          >
            <h3 class="resource-state__title">{{ t('campaignDetail.qualificationLoadingTitle') }}</h3>
            <p class="resource-state__description">
              {{ t('campaignDetail.qualificationLoadingDescription') }}
            </p>
          </section>

          <section
            v-else-if="qualificationError"
            class="resource-state"
            data-testid="campaign-qualification-error"
          >
            <h3 class="resource-state__title">{{ t('campaignDetail.qualificationErrorTitle') }}</h3>
            <p class="resource-state__description">
              {{ qualificationErrorMessage }}
            </p>
            <div class="resource-state__actions">
              <button class="resource-action" type="button" @click="refreshQualification()">
                {{ t('common.retry') }}
              </button>
            </div>
          </section>

          <section
            v-else-if="qualificationResults.length === 0"
            class="resource-state"
            data-testid="campaign-qualification-empty"
          >
            <h3 class="resource-state__title">{{ t('campaignDetail.qualificationEmptyTitle') }}</h3>
            <p class="resource-state__description">
              {{ t('campaignDetail.qualificationEmptyDescription') }}
            </p>
            <div class="resource-state__actions">
              <NuxtLink class="resource-action" to="/device-profiles/new">
                {{ t('campaignDetail.createDeviceProfile') }}
              </NuxtLink>
            </div>
          </section>

          <section
            v-else
            class="resource-section__body"
            data-testid="campaign-qualification-list"
          >
            <article
              v-for="result in qualificationResults"
              :key="result.device_profile_id"
              class="resource-card"
              :data-testid="`campaign-qualification-result-${result.device_profile_id}`"
            >
              <span class="resource-shell__breadcrumb">{{ t('campaignDetail.qualificationBreadcrumb') }}</span>
              <h3 class="resource-card__title">{{ result.device_profile_name }}</h3>
              <p class="resource-card__description">
                {{ result.reason_summary || t('campaignDetail.qualificationSummaryEmpty') }}
              </p>
              <div class="resource-card__meta">
                <span class="resource-card__chip">
                  {{ t('campaignDetail.qualificationStatusLabel') }} {{ formatQualificationStatusLabel(result.qualification_status, locale) }}
                </span>
                <span class="resource-card__chip">
                  {{ t('campaignDetail.qualificationDeviceLabel') }} {{ result.device_profile_id }}
                </span>
                <span
                  v-if="result.matched_rule_id"
                  class="resource-card__chip"
                >
                  {{ t('campaignDetail.matchedRuleLabel') }} {{ result.matched_rule_id }}
                </span>
              </div>
            </article>
          </section>
        </template>
      </section>

      <section
        v-if="!pending && !error && campaign"
        class="resource-section"
        data-testid="campaign-participation-section"
      >
        <h2 class="resource-section__title">{{ t('campaignDetail.participationTitle') }}</h2>

        <div class="resource-state__actions">
          <NuxtLink class="resource-action" to="/my/participation-requests">
            {{ t('campaignDetail.viewMyParticipationRequests') }}
          </NuxtLink>
        </div>

        <section
          v-if="accountsError"
          class="resource-state"
          data-testid="campaign-participation-actor-error"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.actorErrorTitle') }}</h3>
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
          data-testid="campaign-participation-actor-loading"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.actorLoadingTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.participationActorLoadingDescription') }}
          </p>
        </section>

        <section
          v-else-if="!currentActorId"
          class="resource-state"
          data-testid="campaign-participation-select-actor"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.participationSelectActorTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.participationSelectActorDescription') }}
          </p>
        </section>

        <section
          v-else-if="!currentActor"
          class="resource-state"
          data-testid="campaign-participation-actor-missing"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.participationActorMissingTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.participationActorMissingDescription') }}
          </p>
        </section>

        <section
          v-else-if="!isTesterActor"
          class="resource-state"
          data-testid="campaign-participation-role-mismatch"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.participationRoleMismatchTitle') }}</h3>
          <p class="resource-state__description">
            {{
              t('campaignDetail.participationRoleMismatchDescription', {
                role: formatAccountRoleLabel(currentActor.role, locale)
              })
            }}
          </p>
        </section>

        <section
          v-else-if="qualificationPending"
          class="resource-state"
          data-testid="campaign-participation-loading"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.participationLoadingTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.participationLoadingDescription') }}
          </p>
        </section>

        <section
          v-else-if="qualificationError"
          class="resource-state"
          data-testid="campaign-participation-error"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.participationErrorTitle') }}</h3>
          <p class="resource-state__description">
            {{ qualificationErrorMessage }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshQualification()">
                {{ t('common.retry') }}
            </button>
          </div>
        </section>

        <section
          v-else-if="qualifiedParticipationDeviceProfiles.length === 0"
          class="resource-state"
          data-testid="campaign-participation-empty"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.participationEmptyTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.participationEmptyDescription') }}
          </p>
          <div class="resource-state__actions">
            <NuxtLink class="resource-action" to="/device-profiles">
              {{ t('myEligibleCampaigns.viewDeviceProfiles') }}
            </NuxtLink>
          </div>
        </section>

        <section
          v-else
          class="resource-section"
          data-testid="campaign-participation-panel"
        >
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              {{ t('campaignDetail.eligibleDevicesLabel') }} {{ qualifiedParticipationDeviceProfiles.length }}
            </span>
            <span class="resource-shell__meta-chip">
              {{ t('campaignDetail.qualificationCurrentAccount') }} {{ currentActor.display_name }}
            </span>
          </div>

          <ParticipationRequestForm
            :initial-values="participationInitialValues"
            :qualified-device-profiles="qualifiedParticipationDeviceProfiles"
            :pending="participationPending"
            :error-message="participationErrorMessage"
            :success-message="participationSuccessMessage"
            :submit-label="t('common.submitParticipationRequest')"
            test-id-prefix="campaign-participation"
            @submit="handleCreateParticipationRequest"
          />
        </section>
      </section>

      <section
        v-if="!pending && !error && campaign"
        class="resource-section"
        data-testid="campaign-tasks-section"
      >
        <h2 class="resource-section__title">{{ t('campaignDetail.tasksTitle') }}</h2>

        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="campaign-task-create-link"
            :to="`/campaigns/${campaign.id}/tasks/new`"
          >
            {{ t('campaignDetail.createTask') }}
          </NuxtLink>
          <NuxtLink
            class="resource-action"
            data-testid="campaign-tasks-link"
            :to="`/tasks?campaign_id=${campaign.id}`"
          >
            {{ t('campaignDetail.viewCampaignTasks') }}
          </NuxtLink>
        </div>

        <div
          v-if="tasksPending"
          class="resource-state"
          data-testid="campaign-tasks-loading"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.tasksLoadingTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.tasksLoadingDescription') }}
          </p>
        </div>

        <div
          v-else-if="tasksError"
          class="resource-state"
          data-testid="campaign-tasks-error"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.tasksErrorTitle') }}</h3>
          <p class="resource-state__description">
            {{ getActorAwareReadErrorMessage(tasksError, t('campaignDetail.tasksErrorFallback')) }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshTasks()">
              {{ t('common.retry') }}
            </button>
          </div>
        </div>

        <div
          v-else-if="tasks.length === 0"
          class="resource-state"
          data-testid="campaign-tasks-empty"
        >
          <h3 class="resource-state__title">{{ t('campaignDetail.tasksEmptyTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('campaignDetail.tasksEmptyDescription') }}
          </p>
        </div>

        <div
          v-else
          class="resource-section__body"
          data-testid="campaign-tasks-list"
        >
          <NuxtLink
            v-for="task in tasks"
            :key="task.id"
            class="resource-card"
            :data-testid="`campaign-task-card-${task.id}`"
            :to="`/tasks/${task.id}`"
          >
            <span class="resource-shell__breadcrumb">{{ t('campaignDetail.taskBreadcrumb') }}</span>
            <h3 class="resource-card__title">{{ task.title }}</h3>
            <p class="resource-card__description">
              {{
                task.device_profile_id
                  ? t('campaignDetail.taskAssignedTo', { deviceProfileId: task.device_profile_id })
                  : t('campaignDetail.taskAssignmentEmpty')
              }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">{{ t('campaignDetail.statusLabel') }} {{ formatTaskStatusLabel(task.status, locale) }}</span>
              <span class="resource-card__chip">{{ t('campaignDetail.updatedAtLabel') }} {{ task.updated_at }}</span>
            </div>
          </NuxtLink>
        </div>
      </section>

      <NuxtPage />
    </section>
  </main>
</template>
