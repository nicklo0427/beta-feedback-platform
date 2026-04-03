<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import {
  FEEDBACK_CATEGORY_OPTIONS,
  FEEDBACK_RATING_OPTIONS,
  FEEDBACK_SEVERITY_OPTIONS,
  type FeedbackFormValues
} from '~/features/feedback/types'

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
    submitLabel: 'Save feedback'
  }
)

const emit = defineEmits<{
  submit: [values: FeedbackFormValues]
}>()

const validationMessage = ref<string | null>(null)
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
    validationMessage.value = 'Summary is required.'
    return false
  }

  if (!values.severity) {
    validationMessage.value = 'Severity is required.'
    return false
  }

  if (!values.category) {
    validationMessage.value = 'Category is required.'
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

    <div class="resource-form__grid">
      <label class="resource-field">
        <span class="resource-field__label">Summary</span>
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
        <span class="resource-field__label">Rating</span>
        <select
          v-model="values.rating"
          class="resource-select"
          data-testid="feedback-rating-field"
          name="rating"
          :disabled="pending"
        >
          <option value="">Not provided</option>
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
        <span class="resource-field__label">Severity</span>
        <select
          v-model="values.severity"
          class="resource-select"
          data-testid="feedback-severity-field"
          name="severity"
          :disabled="pending"
        >
          <option value="">Select severity</option>
          <option
            v-for="severity in FEEDBACK_SEVERITY_OPTIONS"
            :key="severity"
            :value="severity"
          >
            {{ severity }}
          </option>
        </select>
      </label>

      <label class="resource-field">
        <span class="resource-field__label">Category</span>
        <select
          v-model="values.category"
          class="resource-select"
          data-testid="feedback-category-field"
          name="category"
          :disabled="pending"
        >
          <option value="">Select category</option>
          <option
            v-for="category in FEEDBACK_CATEGORY_OPTIONS"
            :key="category"
            :value="category"
          >
            {{ category }}
          </option>
        </select>
      </label>
    </div>

    <label class="resource-field">
      <span class="resource-field__label">Reproduction Steps</span>
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
      <span class="resource-field__label">Expected Result</span>
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
      <span class="resource-field__label">Actual Result</span>
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
      <span class="resource-field__label">Note</span>
      <textarea
        v-model="values.note"
        class="resource-textarea"
        data-testid="feedback-note-input"
        name="note"
        rows="4"
        :disabled="pending"
      />
    </label>

    <div class="resource-form__actions">
      <button
        class="resource-action"
        data-testid="feedback-submit"
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
