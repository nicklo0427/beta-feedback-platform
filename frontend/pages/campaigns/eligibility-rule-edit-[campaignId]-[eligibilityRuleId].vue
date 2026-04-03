<script setup lang="ts">
definePageMeta({
  path: '/campaigns/:campaignId/eligibility-rules/:eligibilityRuleId/edit'
})

import { computed, ref, watch } from 'vue'

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
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
const campaignId = computed(() => String(route.params.campaignId))
const eligibilityRuleId = computed(() => String(route.params.eligibilityRuleId))
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
    submitError.value = 'Eligibility rule detail is unavailable.'
    return
  }

  const payload = buildEligibilityRuleUpdatePayload(values, initialValues.value)

  if (!payload) {
    submitError.value = 'No changes to save yet.'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const updatedEligibilityRule = await updateEligibilityRule(
      eligibilityRuleId.value,
      payload
    )
    await router.push(
      `/campaigns/${campaignId.value}/eligibility-rules/${updatedEligibilityRule.id}`
    )
  } catch (submitFailure) {
    submitError.value =
      submitFailure instanceof ApiClientError
        ? submitFailure.message
        : 'Unable to update the eligibility rule right now.'
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
          Eligibility Rule Detail
        </NuxtLink>
        <h1 class="resource-shell__title">Edit Eligibility Rule</h1>
        <p class="resource-shell__description">
          更新 Campaign 的最小資格條件，維持裝置平台、版本與安裝渠道限制的一致性。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="eligibility-rule-edit-loading"
      >
        <h2 class="resource-state__title">Loading eligibility rule edit form</h2>
        <p class="resource-state__description">
          正在從 API 載入既有 eligibility rule。
        </p>
      </section>

      <section
        v-else-if="error || !eligibilityRule"
        class="resource-state"
        data-testid="eligibility-rule-edit-error"
      >
        <h2 class="resource-state__title">Eligibility rule edit unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The requested eligibility rule could not be loaded.' }}
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
        data-testid="eligibility-rule-edit-panel"
      >
        <h2 class="resource-section__title">
          Edit {{ formatPlatformLabel(eligibilityRule.platform) }} Rule
        </h2>
        <EligibilityRuleForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="Update eligibility rule"
          :cancel-to="`/campaigns/${campaignId}/eligibility-rules/${eligibilityRuleId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
