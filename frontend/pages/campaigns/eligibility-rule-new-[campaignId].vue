<script setup lang="ts">
definePageMeta({
  path: '/campaigns/:campaignId/eligibility-rules/new'
})

import { computed, ref } from 'vue'

import {
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { createEligibilityRule } from '~/features/eligibility/api'
import EligibilityRuleForm from '~/features/eligibility/EligibilityRuleForm.vue'
import {
  buildEligibilityRuleCreatePayload,
  createEmptyEligibilityRuleFormValues
} from '~/features/eligibility/form'
import type { EligibilityRuleFormValues } from '~/features/eligibility/types'

const route = useRoute()
const router = useRouter()
useCurrentActorPersistence()

const campaignId = computed(() => String(route.params.campaignId))
const currentActorId = useCurrentActorId()
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = createEmptyEligibilityRuleFormValues()

async function handleSubmit(values: EligibilityRuleFormValues): Promise<void> {
  if (!currentActorId.value) {
    submitError.value = '建立資格條件規則前，請先選擇目前操作帳號。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    await createEligibilityRule(
      campaignId.value,
      buildEligibilityRuleCreatePayload(values),
      currentActorId.value
    )
    await router.push(`/campaigns/${campaignId.value}`)
  } catch (error) {
    submitError.value = getActorAwareMutationErrorMessage(
      error,
      '目前無法儲存資格條件規則。'
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
        <h1 class="resource-shell__title">建立資格條件規則</h1>
        <p class="resource-shell__description">
          為目前的活動建立最小資格條件，限定可參與測試的裝置平台、作業系統與安裝渠道。
        </p>
        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">活動 {{ campaignId }}</span>
          <span
            v-if="currentActorId"
            class="resource-shell__meta-chip"
          >
            actor {{ currentActorId }}
          </span>
        </div>
      </header>

      <section class="resource-section" data-testid="eligibility-rule-create-panel">
        <h2 class="resource-section__title">新增資格條件規則</h2>
        <EligibilityRuleForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="建立資格條件規則"
          :cancel-to="`/campaigns/${campaignId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
