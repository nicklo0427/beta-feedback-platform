<script setup lang="ts">
definePageMeta({
  path: '/campaigns/:campaignId/safety/edit'
})

import { computed, ref, watch } from 'vue'

import CampaignSafetyForm from '~/features/safety/CampaignSafetyForm.vue'
import {
  fetchCampaignSafetyDetail,
  updateCampaignSafety
} from '~/features/safety/api'
import {
  buildCampaignSafetyUpdatePayload,
  createEmptyCampaignSafetyFormValues,
  toCampaignSafetyFormValues
} from '~/features/safety/form'
import type { CampaignSafetyFormValues } from '~/features/safety/types'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
const campaignId = computed(() => String(route.params.campaignId))
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = ref(createEmptyCampaignSafetyFormValues())

const {
  data: safety,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `campaign-safety-edit-${campaignId.value}`,
  () => fetchCampaignSafetyDetail(campaignId.value),
  {
    server: false,
    watch: [campaignId],
    default: () => null
  }
)

watch(
  safety,
  (nextSafety) => {
    if (!nextSafety) {
      return
    }

    initialValues.value = toCampaignSafetyFormValues(nextSafety)
    submitError.value = null
  },
  {
    immediate: true
  }
)

async function handleSubmit(values: CampaignSafetyFormValues): Promise<void> {
  if (!safety.value) {
    submitError.value = 'Campaign safety detail is unavailable.'
    return
  }

  const payload = buildCampaignSafetyUpdatePayload(values, initialValues.value)

  if (!payload) {
    submitError.value = 'No changes to save yet.'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    await updateCampaignSafety(campaignId.value, payload)
    await router.push(`/campaigns/${campaignId.value}`)
  } catch (submitFailure) {
    submitError.value =
      submitFailure instanceof ApiClientError
        ? submitFailure.message
        : 'Unable to update the campaign safety right now.'
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
        <h1 class="resource-shell__title">Edit Campaign Safety</h1>
        <p class="resource-shell__description">
          更新既有 Campaign 的來源標示與風險資訊，維持分發安全原則與 review 狀態一致。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="campaign-safety-edit-loading"
      >
        <h2 class="resource-state__title">Loading campaign safety edit form</h2>
        <p class="resource-state__description">
          正在從 API 載入既有 campaign safety。
        </p>
      </section>

      <section
        v-else-if="error || !safety"
        class="resource-state"
        data-testid="campaign-safety-edit-error"
      >
        <h2 class="resource-state__title">Campaign safety edit unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The requested campaign safety could not be loaded.' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            Retry
          </button>
          <NuxtLink class="resource-action" :to="`/campaigns/${campaignId}`">
            Back to campaign
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="campaign-safety-edit-panel"
      >
        <h2 class="resource-section__title">Edit Safety Profile</h2>
        <CampaignSafetyForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="Update safety profile"
          :cancel-to="`/campaigns/${campaignId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
