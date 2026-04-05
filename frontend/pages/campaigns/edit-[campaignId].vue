<script setup lang="ts">
definePageMeta({
  path: '/campaigns/:campaignId/edit'
})

import { computed, ref, watch } from 'vue'

import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import CampaignForm from '~/features/campaigns/CampaignForm.vue'
import { fetchCampaignDetail, updateCampaign } from '~/features/campaigns/api'
import {
  buildCampaignUpdatePayload,
  createEmptyCampaignFormValues,
  toCampaignFormValues
} from '~/features/campaigns/form'
import type { CampaignFormValues } from '~/features/campaigns/types'

const route = useRoute()
const router = useRouter()
useCurrentActorPersistence()

const campaignId = computed(() => String(route.params.campaignId))
const currentActorId = useCurrentActorId()
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
    submitError.value = '目前無法取得活動內容。'
    return
  }

  if (!currentActorId.value) {
    submitError.value = '更新活動前，請先選擇目前操作帳號。'
    return
  }

  const payload = buildCampaignUpdatePayload(values, initialValues.value)

  if (!payload) {
    submitError.value = '目前沒有可儲存的變更。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const updatedCampaign = await updateCampaign(
      campaignId.value,
      payload,
      currentActorId.value
    )
    await router.push(`/campaigns/${updatedCampaign.id}`)
  } catch (submitFailure) {
    submitError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      '目前無法更新活動。'
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
        <h1 class="resource-shell__title">編輯活動</h1>
        <p class="resource-shell__description">
          更新既有活動的最小欄位、目標平台與狀態，讓後續安全設定、資格條件與任務流程維持一致。
        </p>
      </header>

      <CurrentActorSelector
        title="活動操作帳號"
        description="選擇目前正在操作的開發者帳號。更新活動時，系統會用它驗證活動所屬專案的擁有權。"
      />

      <section
        v-if="pending"
        class="resource-state"
        data-testid="campaign-edit-loading"
      >
        <h2 class="resource-state__title">載入活動編輯表單中</h2>
        <p class="resource-state__description">
          正在從 API 載入既有活動。
        </p>
      </section>

      <section
        v-else-if="error || !campaign"
        class="resource-state"
        data-testid="campaign-edit-error"
      >
        <h2 class="resource-state__title">無法載入活動編輯表單</h2>
        <p class="resource-state__description">
          {{ error?.message || '找不到指定的活動。' }}
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
        data-testid="campaign-edit-panel"
      >
        <h2 class="resource-section__title">編輯 {{ campaign.name }}</h2>
        <CampaignForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="更新活動"
          :cancel-to="`/campaigns/${campaignId}`"
          allow-status-edit
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
