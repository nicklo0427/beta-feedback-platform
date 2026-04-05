<script setup lang="ts">
definePageMeta({
  path: '/campaigns/:campaignId/eligibility-rules/:eligibilityRuleId/edit'
})

import { computed, ref, watch } from 'vue'

import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import {
  fetchEligibilityRuleDetail,
  updateEligibilityRule
} from '~/features/eligibility/api'
import EligibilityRuleForm from '~/features/eligibility/EligibilityRuleForm.vue'
import {
  buildEligibilityRuleUpdatePayload,
  createEmptyEligibilityRuleFormValues,
  toEligibilityRuleFormValues
} from '~/features/eligibility/form'
import { formatPlatformLabel } from '~/features/platform-display'
import type { EligibilityRuleFormValues } from '~/features/eligibility/types'

const route = useRoute()
const router = useRouter()
useCurrentActorPersistence()

const campaignId = computed(() => String(route.params.campaignId))
const eligibilityRuleId = computed(() => String(route.params.eligibilityRuleId))
const currentActorId = useCurrentActorId()
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = ref(createEmptyEligibilityRuleFormValues())

const {
  data: eligibilityRule,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `eligibility-rule-edit-${eligibilityRuleId.value}`,
  () => fetchEligibilityRuleDetail(eligibilityRuleId.value),
  {
    server: false,
    watch: [eligibilityRuleId],
    default: () => null
  }
)

watch(
  eligibilityRule,
  (nextEligibilityRule) => {
    if (!nextEligibilityRule) {
      return
    }

    initialValues.value = toEligibilityRuleFormValues(nextEligibilityRule)
    submitError.value = null
  },
  {
    immediate: true
  }
)

async function handleSubmit(values: EligibilityRuleFormValues): Promise<void> {
  if (!eligibilityRule.value) {
    submitError.value = '目前無法取得資格條件規則內容。'
    return
  }

  if (!currentActorId.value) {
    submitError.value = '更新資格條件規則前，請先選擇目前操作帳號。'
    return
  }

  const payload = buildEligibilityRuleUpdatePayload(values, initialValues.value)

  if (!payload) {
    submitError.value = '目前沒有可儲存的變更。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const updatedEligibilityRule = await updateEligibilityRule(
      eligibilityRuleId.value,
      payload,
      currentActorId.value
    )
    await router.push(
      `/campaigns/${campaignId.value}/eligibility-rules/${updatedEligibilityRule.id}`
    )
  } catch (submitFailure) {
    submitError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      '目前無法更新資格條件規則。'
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
        <NuxtLink
          class="resource-shell__breadcrumb"
          :to="`/campaigns/${campaignId}/eligibility-rules/${eligibilityRuleId}`"
        >
          資格條件規則詳情
        </NuxtLink>
        <h1 class="resource-shell__title">編輯資格條件規則</h1>
        <p class="resource-shell__description">
          更新活動的最小資格條件，維持裝置平台、版本與安裝渠道限制的一致性。
        </p>
      </header>

      <CurrentActorSelector
        title="資格條件操作帳號"
        description="選擇目前正在操作的開發者帳號。更新資格條件規則時，系統會驗證活動擁有權。"
      />

      <section
        v-if="pending"
        class="resource-state"
        data-testid="eligibility-rule-edit-loading"
      >
        <h2 class="resource-state__title">載入資格條件規則編輯表單中</h2>
        <p class="resource-state__description">
          正在從 API 載入既有資格條件規則。
        </p>
      </section>

      <section
        v-else-if="error || !eligibilityRule"
        class="resource-state"
        data-testid="eligibility-rule-edit-error"
      >
        <h2 class="resource-state__title">無法載入資格條件規則編輯表單</h2>
        <p class="resource-state__description">
          {{ error?.message || '找不到指定的資格條件規則。' }}
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
        data-testid="eligibility-rule-edit-panel"
      >
        <h2 class="resource-section__title">
          編輯 {{ formatPlatformLabel(eligibilityRule.platform) }} 規則
        </h2>
        <EligibilityRuleForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="更新資格條件規則"
          :cancel-to="`/campaigns/${campaignId}/eligibility-rules/${eligibilityRuleId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
