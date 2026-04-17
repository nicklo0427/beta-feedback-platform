<script setup lang="ts">
definePageMeta({
  path: '/campaigns/:campaignId/safety/new'
})

import { computed, ref } from 'vue'

import {
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { fetchCampaignDetail } from '~/features/campaigns/api'
import CampaignSafetyForm from '~/features/safety/CampaignSafetyForm.vue'
import { createCampaignSafety } from '~/features/safety/api'
import {
  buildCampaignSafetyCreatePayload,
  createEmptyCampaignSafetyFormValues
} from '~/features/safety/form'
import type { CampaignSafetyFormValues } from '~/features/safety/types'

const route = useRoute()
const router = useRouter()
useCurrentActorPersistence()

const campaignId = computed(() => String(route.params.campaignId))
const currentActorId = useCurrentActorId()
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
  if (!currentActorId.value) {
    submitError.value = '建立活動安全資訊前，請先選擇目前操作帳號。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    await createCampaignSafety(
      campaignId.value,
      buildCampaignSafetyCreatePayload(values),
      currentActorId.value
    )
    await router.push(`/campaigns/${campaignId.value}`)
  } catch (submitFailure) {
    submitError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      '目前無法儲存活動安全資訊。'
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
        <NuxtLink class="resource-shell__breadcrumb" :to="`/campaigns/${campaignId}`">
          活動詳情
        </NuxtLink>
        <h1 class="resource-shell__title">建立活動安全資訊</h1>
        <p class="resource-shell__description">
          為目前的活動建立最小來源標示與風險資訊，讓測試分發方式、風險等級與審核狀態可以被清楚辨識。
        </p>
        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            {{
              campaign
                ? `活動 ${campaign.name}`
                : `活動 ${campaignId}`
            }}
          </span>
          <span
            v-if="currentActorId"
            class="resource-shell__meta-chip"
          >
            actor {{ currentActorId }}
          </span>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="campaign-safety-create-loading"
      >
        <h2 class="resource-state__title">載入活動安全表單中</h2>
        <p class="resource-state__description">
          正在載入活動情境。
        </p>
      </section>

      <section
        v-else-if="error || !campaign"
        class="resource-state"
        data-testid="campaign-safety-create-error"
      >
        <h2 class="resource-state__title">無法載入活動安全建立表單</h2>
        <p class="resource-state__description">
          {{ error?.message || '目前無法載入活動安全建立表單。' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試
          </button>
          <NuxtLink class="resource-action" to="/campaigns">
            返回活動列表
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="campaign-safety-create-panel"
      >
        <h2 class="resource-section__title">新增安全設定</h2>
        <CampaignSafetyForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="建立安全設定"
          :cancel-to="`/campaigns/${campaignId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
