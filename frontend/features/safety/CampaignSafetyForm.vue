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
    submitLabel: '儲存安全設定'
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
    validationMessage.value = '分發管道為必填。'
    return false
  }

  if (!values.source_label.trim()) {
    validationMessage.value = '來源標示為必填。'
    return false
  }

  if (!values.risk_level) {
    validationMessage.value = '風險等級為必填。'
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

    <section class="resource-form__section">
      <div>
        <h2 class="resource-form__section-title">來源與審核</h2>
        <p class="resource-form__section-description">
          定義這個活動的分發來源、風險等級與目前審核狀態。
        </p>
      </div>

      <div class="resource-form__section-grid">
        <label class="resource-field">
          <span class="resource-field__label">分發管道</span>
          <select
            v-model="values.distribution_channel"
            class="resource-select"
            data-testid="campaign-safety-distribution-channel-field"
            name="distribution_channel"
            :disabled="pending"
          >
            <option value="">請選擇分發管道</option>
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
          <span class="resource-field__label">來源標示</span>
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
          <span class="resource-field__label">來源網址</span>
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
          <span class="resource-field__label">風險等級</span>
          <select
            v-model="values.risk_level"
            class="resource-select"
            data-testid="campaign-safety-risk-level-field"
            name="risk_level"
            :disabled="pending"
          >
            <option value="">請選擇風險等級</option>
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
          <span class="resource-field__label">審核狀態</span>
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
    </section>

    <section class="resource-form__section">
      <div>
        <h2 class="resource-form__section-title">安全限制</h2>
        <p class="resource-form__section-description">
          補充風險說明，並決定是否要將分發方式限制在可信任的官方管道。
        </p>
      </div>

      <label class="resource-field">
        <span class="resource-field__label">風險說明</span>
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
        <span class="resource-field__label">僅限官方管道</span>
        <span class="resource-inline-toggle">
          <input
            v-model="values.official_channel_only"
            data-testid="campaign-safety-official-channel-only-input"
            name="official_channel_only"
            type="checkbox"
            :disabled="pending"
          >
          <span class="resource-inline-toggle__copy">
            <span class="resource-choice-card__label">限制為可信任官方來源</span>
            <span class="resource-choice-card__hint">避免非官方分發渠道混入活動。</span>
          </span>
        </span>
      </label>
    </section>

    <div class="resource-form__sticky-actions">
      <button
        class="resource-action"
        data-testid="campaign-safety-submit"
        type="submit"
        :disabled="pending"
      >
        {{ pending ? '儲存中...' : submitLabel }}
      </button>
      <NuxtLink class="resource-action" :to="cancelTo">
        取消
      </NuxtLink>
    </div>
  </form>
</template>
