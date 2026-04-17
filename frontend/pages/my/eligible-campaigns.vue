<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import {
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import { fetchCampaigns } from '~/features/campaigns/api'
import { formatCampaignStatusLabel } from '~/features/campaigns/types'
import ParticipationRequestForm from '~/features/participation-requests/ParticipationRequestForm.vue'
import {
  createParticipationRequest
} from '~/features/participation-requests/api'
import { buildParticipationRequestCreatePayload, createEmptyParticipationRequestFormValues } from '~/features/participation-requests/form'
import type { ParticipationRequestFormValues } from '~/features/participation-requests/types'
import { useAppI18n } from '~/features/i18n/use-app-i18n'
import { formatPlatformLabel } from '~/features/platform-display'

useCurrentActorPersistence()

const { locale, t } = useAppI18n()
const currentActorId = useCurrentActorId()

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('my-eligible-campaigns-accounts', () => fetchAccounts(), {
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
  data: campaignResponse,
  pending: campaignsPending,
  error: campaignsError,
  refresh: refreshCampaigns
} = useAsyncData(
  () =>
    `my-eligible-campaigns-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
  async () => {
    if (!currentActorId.value || !isTesterActor.value) {
      return {
        items: [],
        total: 0
      }
    }

    return fetchCampaigns({
      qualifiedForMe: true,
      actorId: currentActorId.value
    })
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

const campaigns = computed(() => campaignResponse.value.items)
const submittingCampaignId = ref<string | null>(null)
const participationErrors = reactive<Record<string, string | null>>({})
const participationSuccesses = reactive<Record<string, string | null>>({})
const participationInitialValuesByCampaign = reactive<
  Record<string, ParticipationRequestFormValues>
>({})

function getParticipationInitialValues(
  campaignId: string
): ParticipationRequestFormValues {
  if (!participationInitialValuesByCampaign[campaignId]) {
    const campaign = campaigns.value.find((item) => item.id === campaignId)
    participationInitialValuesByCampaign[campaignId] =
      createEmptyParticipationRequestFormValues(
        campaign?.qualifying_device_profiles?.[0]?.id ?? ''
      )
  }

  return participationInitialValuesByCampaign[campaignId]
}

async function handleCreateParticipationRequest(
  campaignId: string,
  values: ParticipationRequestFormValues
): Promise<void> {
  participationErrors[campaignId] = null
  participationSuccesses[campaignId] = null
  submittingCampaignId.value = campaignId

  try {
    if (!currentActorId.value) {
      participationErrors[campaignId] = t('myEligibleCampaigns.submitParticipationNoActor')
      return
    }

    await createParticipationRequest(
      campaignId,
      buildParticipationRequestCreatePayload(values),
      currentActorId.value
    )
    participationSuccesses[campaignId] =
      t('myEligibleCampaigns.submitParticipationSuccess')
  } catch (submitFailure) {
    participationErrors[campaignId] = getActorAwareMutationErrorMessage(
      submitFailure,
      t('myEligibleCampaigns.submitParticipationFallback')
    )
  } finally {
    submittingCampaignId.value = null
  }
}

watch([currentActorId, currentActor], () => {
  submittingCampaignId.value = null

  for (const key of Object.keys(participationErrors)) {
    delete participationErrors[key]
  }

  for (const key of Object.keys(participationSuccesses)) {
    delete participationSuccesses[key]
  }

  for (const key of Object.keys(participationInitialValuesByCampaign)) {
    delete participationInitialValuesByCampaign[key]
  }
})
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header app-page-header">
        <NuxtLink class="resource-shell__breadcrumb" to="/dashboard">Dashboard</NuxtLink>
        <h1 class="resource-shell__title">{{ t('myEligibleCampaigns.title') }}</h1>
        <p class="resource-shell__description">
          {{ t('myEligibleCampaigns.description') }}
        </p>
        <div class="resource-state__actions app-page-actions">
          <NuxtLink class="resource-action" to="/campaigns">
            {{ t('myEligibleCampaigns.viewAllCampaigns') }}
          </NuxtLink>
          <NuxtLink class="resource-action" to="/my/tasks">
            {{ t('myEligibleCampaigns.viewMyTasks') }}
          </NuxtLink>
          <NuxtLink class="resource-action" to="/my/participation-requests">
            {{ t('myEligibleCampaigns.viewMyParticipationRequests') }}
          </NuxtLink>
          <NuxtLink class="resource-action" to="/device-profiles">
            {{ t('myEligibleCampaigns.viewDeviceProfiles') }}
          </NuxtLink>
        </div>
      </header>

      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="my-eligible-campaigns-actor-error"
      >
        <h2 class="resource-state__title">{{ t('myEligibleCampaigns.actorErrorTitle') }}</h2>
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
        data-testid="my-eligible-campaigns-actor-loading"
      >
        <h2 class="resource-state__title">{{ t('myEligibleCampaigns.actorLoadingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('myEligibleCampaigns.actorLoadingDescription') }}
        </p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="my-eligible-campaigns-select-actor"
      >
        <h2 class="resource-state__title">{{ t('myEligibleCampaigns.selectActorTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('myEligibleCampaigns.selectActorDescription') }}
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="my-eligible-campaigns-actor-missing"
      >
        <h2 class="resource-state__title">{{ t('myEligibleCampaigns.actorMissingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('myEligibleCampaigns.actorMissingDescription') }}
        </p>
      </section>

      <section
        v-else-if="!isTesterActor"
        class="resource-state"
        data-testid="my-eligible-campaigns-role-mismatch"
      >
        <h2 class="resource-state__title">{{ t('myEligibleCampaigns.roleMismatchTitle') }}</h2>
        <p class="resource-state__description">
          {{
            t('myEligibleCampaigns.roleMismatchDescription', {
              role: formatAccountRoleLabel(currentActor.role, locale)
            })
          }}
        </p>
      </section>

      <template v-else>
        <section class="resource-section" data-testid="my-eligible-campaigns-summary">
          <h2 class="resource-section__title">{{ t('myEligibleCampaigns.summaryTitle') }}</h2>
          <div class="app-page-summary-grid">
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">{{ t('myEligibleCampaigns.currentAccount') }}</span>
              <strong class="app-page-summary-card__value">{{ currentActor.display_name }}</strong>
              <span class="app-page-summary-card__description">確認這個 workspace 正在使用哪位測試者的資格上下文。</span>
            </article>
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">{{ t('myEligibleCampaigns.qualifiedCampaignsLabel') }}</span>
              <strong class="app-page-summary-card__value">{{ campaignResponse.total }}</strong>
              <span class="app-page-summary-card__description">活動卡片會保留 qualification 與 participation entry 的同一套版型。</span>
            </article>
          </div>
        </section>

        <section
          v-if="campaignsPending"
          class="resource-state"
          data-testid="my-eligible-campaigns-loading"
        >
          <h2 class="resource-state__title">{{ t('myEligibleCampaigns.loadingTitle') }}</h2>
          <p class="resource-state__description">
            {{ t('myEligibleCampaigns.loadingDescription') }}
          </p>
        </section>

        <section
          v-else-if="campaignsError"
          class="resource-state"
          data-testid="my-eligible-campaigns-error"
        >
          <h2 class="resource-state__title">{{ t('myEligibleCampaigns.errorTitle') }}</h2>
          <p class="resource-state__description">
            {{ campaignsError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshCampaigns()">
              {{ t('common.retry') }}
            </button>
          </div>
        </section>

        <section
          v-else-if="campaigns.length === 0"
          class="resource-state"
          data-testid="my-eligible-campaigns-empty"
        >
          <h2 class="resource-state__title">{{ t('myEligibleCampaigns.emptyTitle') }}</h2>
          <p class="resource-state__description">
            {{ t('myEligibleCampaigns.emptyDescription') }}
          </p>
          <div class="resource-state__actions">
            <NuxtLink class="resource-action" to="/device-profiles">
              {{ t('myEligibleCampaigns.viewDeviceProfiles') }}
            </NuxtLink>
            <NuxtLink class="resource-action" to="/campaigns">
              {{ t('myEligibleCampaigns.viewAllCampaigns') }}
            </NuxtLink>
          </div>
        </section>

        <section
          v-else
          class="resource-section__body app-page-card-grid"
          data-testid="my-eligible-campaigns-list"
        >
          <article
            v-for="campaign in campaigns"
            :key="campaign.id"
            class="resource-card"
            :data-testid="`my-eligible-campaign-card-${campaign.id}`"
          >
            <span class="resource-shell__breadcrumb">{{ t('myEligibleCampaigns.title') }}</span>
            <h2 class="resource-card__title">{{ campaign.name }}</h2>
            <p class="resource-card__description">
              {{
                campaign.qualification_summary
                  || t('myEligibleCampaigns.summaryEmpty')
              }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">{{ t('campaignDetail.statusLabel') }} {{ formatCampaignStatusLabel(campaign.status, locale) }}</span>
              <span class="resource-card__chip">{{ t('campaignDetail.projectIdLabel') }} {{ campaign.project_id }}</span>
            </div>
            <div class="resource-card__meta">
              <span
                v-for="platform in campaign.target_platforms"
              :key="platform"
              class="resource-card__chip"
              >
                {{ formatPlatformLabel(platform, locale) }}
              </span>
            </div>
            <div
              v-if="campaign.qualifying_device_profiles?.length"
              class="resource-card__meta"
              :data-testid="`my-eligible-campaign-chips-${campaign.id}`"
            >
              <span
                v-for="deviceProfile in campaign.qualifying_device_profiles"
                :key="deviceProfile.id"
                class="resource-card__chip"
              >
                {{ t('myEligibleCampaigns.matchedDevice', { name: deviceProfile.name }) }}
              </span>
            </div>
            <div class="resource-state__actions">
              <NuxtLink
                class="resource-action"
                :data-testid="`my-eligible-campaign-detail-link-${campaign.id}`"
                :to="`/campaigns/${campaign.id}`"
              >
                {{ t('myEligibleCampaigns.openCampaignDetail') }}
              </NuxtLink>
            </div>
            <ParticipationRequestForm
              v-if="campaign.qualifying_device_profiles?.length"
              :initial-values="getParticipationInitialValues(campaign.id)"
              :qualified-device-profiles="campaign.qualifying_device_profiles"
              :pending="submittingCampaignId === campaign.id"
              :error-message="participationErrors[campaign.id] || null"
              :success-message="participationSuccesses[campaign.id] || null"
              submit-label="送出參與意圖"
              :test-id-prefix="`eligible-campaign-participation-${campaign.id}`"
              @submit="handleCreateParticipationRequest(campaign.id, $event)"
            />
          </article>
        </section>
      </template>
    </section>
  </main>
</template>
