<script setup lang="ts">
definePageMeta({
  path: '/campaigns/:campaignId/edit'
})

import { computed, ref, watch } from 'vue'

import CampaignForm from '~/features/campaigns/CampaignForm.vue'
import { fetchCampaignDetail, updateCampaign } from '~/features/campaigns/api'
import {
  buildCampaignUpdatePayload,
  createEmptyCampaignFormValues,
  toCampaignFormValues
} from '~/features/campaigns/form'
import type { CampaignFormValues } from '~/features/campaigns/types'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
const campaignId = computed(() => String(route.params.campaignId))
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = ref(createEmptyCampaignFormValues())

const {
  data: campaign,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `campaign-edit-${campaignId.value}`,
  () => fetchCampaignDetail(campaignId.value),
  {
    server: false,
    watch: [campaignId],
    default: () => null
  }
)

watch(
  campaign,
  (nextCampaign) => {
    if (!nextCampaign) {
      return
    }

    initialValues.value = toCampaignFormValues(nextCampaign)
    submitError.value = null
  },
  {
    immediate: true
  }
)

async function handleSubmit(values: CampaignFormValues): Promise<void> {
  if (!campaign.value) {
    submitError.value = 'Campaign detail is unavailable.'
    return
  }

  const payload = buildCampaignUpdatePayload(values, initialValues.value)

  if (!payload) {
    submitError.value = 'No changes to save yet.'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const updatedCampaign = await updateCampaign(campaignId.value, payload)
    await router.push(`/campaigns/${updatedCampaign.id}`)
  } catch (submitFailure) {
    submitError.value =
      submitFailure instanceof ApiClientError
        ? submitFailure.message
        : 'Unable to update the campaign right now.'
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
        <h1 class="resource-shell__title">Edit Campaign</h1>
        <p class="resource-shell__description">
          更新既有 Campaign 的最小欄位、target platforms 與 status，讓後續 safety、eligibility 與 task 流程維持一致。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="campaign-edit-loading"
      >
        <h2 class="resource-state__title">Loading campaign edit form</h2>
        <p class="resource-state__description">
          正在從 API 載入既有 Campaign。
        </p>
      </section>

      <section
        v-else-if="error || !campaign"
        class="resource-state"
        data-testid="campaign-edit-error"
      >
        <h2 class="resource-state__title">Campaign edit unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The requested campaign could not be loaded.' }}
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
        data-testid="campaign-edit-panel"
      >
        <h2 class="resource-section__title">Edit {{ campaign.name }}</h2>
        <CampaignForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="Update campaign"
          :cancel-to="`/campaigns/${campaignId}`"
          allow-status-edit
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
