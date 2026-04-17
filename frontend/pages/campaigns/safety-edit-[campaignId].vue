<script setup lang="ts">
definePageMeta({
  path: '/campaigns/:campaignId/safety/edit'
})

import { computed, ref, watch } from 'vue'

import {
  getActorAwareReadErrorMessage,
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
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

const route = useRoute()
const router = useRouter()
useCurrentActorPersistence()

const campaignId = computed(() => String(route.params.campaignId))
const currentActorId = useCurrentActorId()
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
  () => fetchCampaignSafetyDetail(campaignId.value, currentActorId.value),
  {
    server: false,
    watch: [campaignId, currentActorId],
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
    submitError.value = '目前無法取得活動安全資訊。'
    return
  }

  if (!currentActorId.value) {
    submitError.value = '更新活動安全資訊前，請先選擇目前操作帳號。'
    return
  }

  const payload = buildCampaignSafetyUpdatePayload(values, initialValues.value)

  if (!payload) {
    submitError.value = '目前沒有可儲存的變更。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    await updateCampaignSafety(campaignId.value, payload, currentActorId.value)
    await router.push(`/campaigns/${campaignId.value}`)
  } catch (submitFailure) {
    submitError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      '目前無法更新活動安全資訊。'
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
        <h1 class="resource-shell__title">編輯活動安全資訊</h1>
        <p class="resource-shell__description">
          更新既有活動的來源標示與風險資訊，維持分發安全原則與審核狀態一致。
        </p>
        <div class="resource-shell__meta">
          <span
            v-if="currentActorId"
            class="resource-shell__meta-chip"
          >
            actor {{ currentActorId }}
          </span>
          <span class="resource-shell__meta-chip">操作情境由右上 shell 控制</span>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="campaign-safety-edit-loading"
      >
        <h2 class="resource-state__title">載入活動安全編輯表單中</h2>
        <p class="resource-state__description">
          正在從 API 載入既有活動安全資訊。
        </p>
      </section>

      <section
        v-else-if="error || !safety"
        class="resource-state"
        data-testid="campaign-safety-edit-error"
      >
        <h2 class="resource-state__title">無法載入活動安全編輯表單</h2>
        <p class="resource-state__description">
          {{ getActorAwareReadErrorMessage(error, '找不到指定的活動安全資訊。') }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試
          </button>
          <NuxtLink class="resource-action" :to="`/campaigns/${campaignId}`">
            返回活動
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="campaign-safety-edit-panel"
      >
        <h2 class="resource-section__title">編輯安全設定</h2>
        <CampaignSafetyForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="更新安全設定"
          :cancel-to="`/campaigns/${campaignId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
