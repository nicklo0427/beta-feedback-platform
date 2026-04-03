<script setup lang="ts">
definePageMeta({
  path: '/campaigns/:campaignId/eligibility-rules/new'
})

import { computed, ref } from 'vue'

import { createEligibilityRule } from '~/features/eligibility/api'
import EligibilityRuleForm from '~/features/eligibility/EligibilityRuleForm.vue'
import {
  buildEligibilityRuleCreatePayload,
  createEmptyEligibilityRuleFormValues
} from '~/features/eligibility/form'
import type { EligibilityRuleFormValues } from '~/features/eligibility/types'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
const campaignId = computed(() => String(route.params.campaignId))
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = createEmptyEligibilityRuleFormValues()

async function handleSubmit(values: EligibilityRuleFormValues): Promise<void> {
  submitError.value = null
  submitting.value = true

  try {
    await createEligibilityRule(campaignId.value, buildEligibilityRuleCreatePayload(values))
    await router.push(`/campaigns/${campaignId.value}`)
  } catch (error) {
    submitError.value =
      error instanceof ApiClientError
        ? error.message
        : 'Unable to save the eligibility rule right now.'
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
        <h1 class="resource-shell__title">Create Eligibility Rule</h1>
        <p class="resource-shell__description">
          為目前的 Campaign 建立最小資格條件，限定可參與測試的裝置平台、OS 與安裝渠道。
        </p>
        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">Campaign {{ campaignId }}</span>
        </div>
      </header>

      <section class="resource-section" data-testid="eligibility-rule-create-panel">
        <h2 class="resource-section__title">New Eligibility Rule</h2>
        <EligibilityRuleForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="Create eligibility rule"
          :cancel-to="`/campaigns/${campaignId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
