<script setup lang="ts">
definePageMeta({
  path: '/campaigns/:campaignId/safety/new'
})

import { computed, ref } from 'vue'

import { fetchCampaignDetail } from '~/features/campaigns/api'
import CampaignSafetyForm from '~/features/safety/CampaignSafetyForm.vue'
import { createCampaignSafety } from '~/features/safety/api'
import {
  buildCampaignSafetyCreatePayload,
  createEmptyCampaignSafetyFormValues
} from '~/features/safety/form'
import type { CampaignSafetyFormValues } from '~/features/safety/types'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
const campaignId = computed(() => String(route.params.campaignId))
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = createEmptyCampaignSafetyFormValues()

const {
  data: campaign,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `campaign-safety-create-${campaignId.value}`,
  () => fetchCampaignDetail(campaignId.value),
  {
    server: false,
    watch: [campaignId],
    default: () => null
  }
)

async function handleSubmit(values: CampaignSafetyFormValues): Promise<void> {
  submitError.value = null
  submitting.value = true

  try {
    await createCampaignSafety(campaignId.value, buildCampaignSafetyCreatePayload(values))
    await router.push(`/campaigns/${campaignId.value}`)
  } catch (submitFailure) {
    submitError.value =
      submitFailure instanceof ApiClientError
        ? submitFailure.message
        : 'Unable to save the campaign safety right now.'
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
        <h1 class="resource-shell__title">Create Campaign Safety</h1>
        <p class="resource-shell__description">
          為目前的 Campaign 建立最小來源標示與風險資訊，讓測試分發方式、風險等級與 review status 可以被清楚辨識。
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
        v-if="pending"
        class="resource-state"
        data-testid="campaign-safety-create-loading"
      >
        <h2 class="resource-state__title">Loading campaign safety form</h2>
        <p class="resource-state__description">
          正在載入 campaign context。
        </p>
      </section>

      <section
        v-else-if="error || !campaign"
        class="resource-state"
        data-testid="campaign-safety-create-error"
      >
        <h2 class="resource-state__title">Campaign safety create unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The campaign safety create form could not be loaded.' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            Retry
          </button>
          <NuxtLink class="resource-action" to="/campaigns">
            Back to campaigns
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="campaign-safety-create-panel"
      >
        <h2 class="resource-section__title">New Safety Profile</h2>
        <CampaignSafetyForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="Create safety profile"
          :cancel-to="`/campaigns/${campaignId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
