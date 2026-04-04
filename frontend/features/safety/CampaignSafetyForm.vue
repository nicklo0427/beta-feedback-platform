<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import {
  DISTRIBUTION_CHANNEL_OPTIONS,
  REVIEW_STATUS_OPTIONS,
  RISK_LEVEL_OPTIONS,
  formatDistributionChannelLabel,
  formatReviewStatusLabel,
  formatRiskLevelLabel,
  type CampaignSafetyFormValues
} from '~/features/safety/types'

const props = withDefaults(
  defineProps<{
    initialValues: CampaignSafetyFormValues
    pending?: boolean
    errorMessage?: string | null
    submitLabel?: string
    cancelTo: string
  }>(),
  {
    pending: false,
    errorMessage: null,
    submitLabel: 'Save safety profile'
  }
)

const emit = defineEmits<{
  submit: [values: CampaignSafetyFormValues]
}>()

const validationMessage = ref<string | null>(null)
const values = reactive<CampaignSafetyFormValues>({
  ...props.initialValues
})

watch(
  () => props.initialValues,
  (nextValues) => {
    Object.assign(values, nextValues)
    validationMessage.value = null
  },
  {
    immediate: true
  }
)

function validateForm(): boolean {
  if (!values.distribution_channel) {
    validationMessage.value = 'Distribution channel is required.'
    return false
  }

  if (!values.source_label.trim()) {
    validationMessage.value = 'Source label is required.'
    return false
  }

  if (!values.risk_level) {
    validationMessage.value = 'Risk level is required.'
    return false
  }

  validationMessage.value = null
  return true
}

function handleSubmit(): void {
  if (!validateForm()) {
    return
  }

  emit('submit', { ...values })
}
</script>

<template>
  <form
    class="resource-form"
    data-testid="campaign-safety-form"
    @submit.prevent="handleSubmit"
  >
    <div
      v-if="validationMessage || errorMessage"
      class="resource-form__error"
      data-testid="campaign-safety-form-error"
    >
      {{ validationMessage || errorMessage }}
    </div>

    <div class="resource-form__grid">
      <label class="resource-field">
        <span class="resource-field__label">Distribution Channel</span>
        <select
          v-model="values.distribution_channel"
          class="resource-select"
          data-testid="campaign-safety-distribution-channel-field"
          name="distribution_channel"
          :disabled="pending"
        >
          <option value="">Select a distribution channel</option>
          <option
            v-for="distributionChannel in DISTRIBUTION_CHANNEL_OPTIONS"
            :key="distributionChannel"
            :value="distributionChannel"
          >
            {{ formatDistributionChannelLabel(distributionChannel) }}
          </option>
        </select>
      </label>

      <label class="resource-field">
        <span class="resource-field__label">Source Label</span>
        <input
          v-model="values.source_label"
          class="resource-input"
          data-testid="campaign-safety-source-label-input"
          name="source_label"
          type="text"
          :disabled="pending"
        >
      </label>

      <label class="resource-field">
        <span class="resource-field__label">Source URL</span>
        <input
          v-model="values.source_url"
          class="resource-input"
          data-testid="campaign-safety-source-url-input"
          name="source_url"
          type="url"
          :disabled="pending"
        >
      </label>

      <label class="resource-field">
        <span class="resource-field__label">Risk Level</span>
        <select
          v-model="values.risk_level"
          class="resource-select"
          data-testid="campaign-safety-risk-level-field"
          name="risk_level"
          :disabled="pending"
        >
          <option value="">Select a risk level</option>
          <option
            v-for="riskLevel in RISK_LEVEL_OPTIONS"
            :key="riskLevel"
            :value="riskLevel"
          >
            {{ formatRiskLevelLabel(riskLevel) }}
          </option>
        </select>
      </label>

      <label class="resource-field">
        <span class="resource-field__label">Review Status</span>
        <select
          v-model="values.review_status"
          class="resource-select"
          data-testid="campaign-safety-review-status-field"
          name="review_status"
          :disabled="pending"
        >
          <option
            v-for="reviewStatus in REVIEW_STATUS_OPTIONS"
            :key="reviewStatus"
            :value="reviewStatus"
          >
            {{ formatReviewStatusLabel(reviewStatus) }}
          </option>
        </select>
      </label>
    </div>

    <label class="resource-field">
      <span class="resource-field__label">Risk Note</span>
      <textarea
        v-model="values.risk_note"
        class="resource-textarea"
        data-testid="campaign-safety-risk-note-input"
        name="risk_note"
        rows="4"
        :disabled="pending"
      />
    </label>

    <label class="resource-field">
      <span class="resource-field__label">Official Channel Only</span>
      <div class="resource-state__actions">
        <input
          v-model="values.official_channel_only"
          data-testid="campaign-safety-official-channel-only-input"
          name="official_channel_only"
          type="checkbox"
          :disabled="pending"
        >
        <span class="resource-key-value__value">
          Limit distribution to trusted official channels only.
        </span>
      </div>
    </label>

    <div class="resource-form__actions">
      <button
        class="resource-action"
        data-testid="campaign-safety-submit"
        type="submit"
        :disabled="pending"
      >
        {{ pending ? 'Saving...' : submitLabel }}
      </button>
      <NuxtLink class="resource-action" :to="cancelTo">
        Cancel
      </NuxtLink>
    </div>
  </form>
</template>
