<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import {
  FEEDBACK_CATEGORY_OPTIONS,
  FEEDBACK_RATING_OPTIONS,
  FEEDBACK_SEVERITY_OPTIONS,
  formatFeedbackCategoryLabel,
  formatFeedbackSeverityLabel,
  type FeedbackFormValues
} from '~/features/feedback/types'
import { useAppI18n } from '~/features/i18n/use-app-i18n'

const props = withDefaults(
  defineProps<{
    initialValues: FeedbackFormValues
    pending?: boolean
    errorMessage?: string | null
    submitLabel?: string
    cancelTo: string
  }>(),
  {
    pending: false,
    errorMessage: null,
    submitLabel: undefined
  }
)

const emit = defineEmits<{
  submit: [values: FeedbackFormValues]
}>()

const { locale, t } = useAppI18n()
const validationMessage = ref<string | null>(null)
const resolvedSubmitLabel = computed(() => props.submitLabel || t('common.saveFeedback'))
const values = reactive<FeedbackFormValues>({
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
  if (!values.summary.trim()) {
    validationMessage.value = t('feedbackForm.validationSummaryRequired')
    return false
  }

  if (!values.severity) {
    validationMessage.value = t('feedbackForm.validationSeverityRequired')
    return false
  }

  if (!values.category) {
    validationMessage.value = t('feedbackForm.validationCategoryRequired')
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
    data-testid="feedback-form"
    @submit.prevent="handleSubmit"
  >
    <div
      v-if="validationMessage || errorMessage"
      class="resource-form__error"
      data-testid="feedback-form-error"
    >
      {{ validationMessage || errorMessage }}
    </div>

    <section class="resource-form__section">
      <div>
        <h2 class="resource-form__section-title">{{ t('feedbackForm.summaryTitle') }}</h2>
        <p class="resource-form__section-description">
          {{ t('feedbackForm.summaryDescription') }}
        </p>
      </div>

      <div class="resource-form__section-grid">
        <label class="resource-field">
          <span class="resource-field__label">{{ t('feedbackForm.summaryLabel') }}</span>
          <input
            v-model="values.summary"
            class="resource-input"
            data-testid="feedback-summary-input"
            name="summary"
            type="text"
            :disabled="pending"
          >
        </label>

        <label class="resource-field">
          <span class="resource-field__label">{{ t('feedbackForm.ratingLabel') }}</span>
          <select
            v-model="values.rating"
            class="resource-select"
            data-testid="feedback-rating-field"
            name="rating"
            :disabled="pending"
          >
            <option value="">{{ t('feedbackForm.ratingEmpty') }}</option>
            <option
              v-for="rating in FEEDBACK_RATING_OPTIONS"
              :key="rating"
              :value="rating"
            >
              {{ rating }}
            </option>
          </select>
        </label>

        <label class="resource-field">
          <span class="resource-field__label">{{ t('feedbackForm.severityLabel') }}</span>
          <select
            v-model="values.severity"
            class="resource-select"
            data-testid="feedback-severity-field"
            name="severity"
            :disabled="pending"
          >
            <option value="">{{ t('feedbackForm.severityPlaceholder') }}</option>
            <option
              v-for="severity in FEEDBACK_SEVERITY_OPTIONS"
              :key="severity"
              :value="severity"
            >
              {{ formatFeedbackSeverityLabel(severity, locale) }}
            </option>
          </select>
        </label>

        <label class="resource-field">
          <span class="resource-field__label">{{ t('feedbackForm.categoryLabel') }}</span>
          <select
            v-model="values.category"
            class="resource-select"
            data-testid="feedback-category-field"
            name="category"
            :disabled="pending"
          >
            <option value="">{{ t('feedbackForm.categoryPlaceholder') }}</option>
            <option
              v-for="category in FEEDBACK_CATEGORY_OPTIONS"
              :key="category"
              :value="category"
            >
              {{ formatFeedbackCategoryLabel(category, locale) }}
            </option>
          </select>
        </label>
      </div>
    </section>

    <section class="resource-form__section">
      <div>
        <h2 class="resource-form__section-title">{{ t('feedbackForm.detailsTitle') }}</h2>
        <p class="resource-form__section-description">
          {{ t('feedbackForm.detailsDescription') }}
        </p>
      </div>

      <label class="resource-field">
        <span class="resource-field__label">{{ t('feedbackForm.reproductionStepsLabel') }}</span>
        <textarea
          v-model="values.reproduction_steps"
          class="resource-textarea"
          data-testid="feedback-reproduction-steps-input"
          name="reproduction_steps"
          rows="4"
          :disabled="pending"
        />
      </label>

      <label class="resource-field">
        <span class="resource-field__label">{{ t('feedbackForm.expectedResultLabel') }}</span>
        <textarea
          v-model="values.expected_result"
          class="resource-textarea"
          data-testid="feedback-expected-result-input"
          name="expected_result"
          rows="4"
          :disabled="pending"
        />
      </label>

      <label class="resource-field">
        <span class="resource-field__label">{{ t('feedbackForm.actualResultLabel') }}</span>
        <textarea
          v-model="values.actual_result"
          class="resource-textarea"
          data-testid="feedback-actual-result-input"
          name="actual_result"
          rows="4"
          :disabled="pending"
        />
      </label>

      <label class="resource-field">
        <span class="resource-field__label">{{ t('feedbackForm.noteLabel') }}</span>
        <textarea
          v-model="values.note"
          class="resource-textarea"
          data-testid="feedback-note-input"
          name="note"
          rows="4"
          :disabled="pending"
        />
      </label>
    </section>

    <div class="resource-form__sticky-actions">
      <button
        class="resource-action"
        data-testid="feedback-submit"
        type="submit"
        :disabled="pending"
      >
        {{ pending ? t('feedbackForm.saving') : resolvedSubmitLabel }}
      </button>
      <NuxtLink class="resource-action" :to="cancelTo">
        {{ t('feedbackForm.cancel') }}
      </NuxtLink>
    </div>
  </form>
</template>
