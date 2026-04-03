<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import {
  ELIGIBILITY_RULE_PLATFORM_OPTIONS,
  type EligibilityRuleFormValues
} from '~/features/eligibility/types'
import { formatPlatformLabel } from '~/features/platform-display'

const props = withDefaults(
  defineProps<{
    initialValues: EligibilityRuleFormValues
    pending?: boolean
    errorMessage?: string | null
    submitLabel?: string
    cancelTo: string
  }>(),
  {
    pending: false,
    errorMessage: null,
    submitLabel: 'Save eligibility rule'
  }
)

const emit = defineEmits<{
  submit: [values: EligibilityRuleFormValues]
}>()

const platformOptions = ELIGIBILITY_RULE_PLATFORM_OPTIONS
const validationMessage = ref<string | null>(null)
const values = reactive<EligibilityRuleFormValues>({
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
  if (!values.platform.trim()) {
    validationMessage.value = 'Platform is required.'
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
    data-testid="eligibility-rule-form"
    @submit.prevent="handleSubmit"
  >
    <div
      v-if="validationMessage || errorMessage"
      class="resource-form__error"
      data-testid="eligibility-rule-form-error"
    >
      {{ validationMessage || errorMessage }}
    </div>

    <div class="resource-form__grid">
      <label class="resource-field">
        <span class="resource-field__label">Platform</span>
        <select
          v-model="values.platform"
          class="resource-select"
          data-testid="eligibility-rule-platform-select"
          name="platform"
          :disabled="pending"
        >
          <option value="">Select a platform</option>
          <option
            v-for="platform in platformOptions"
            :key="platform"
            :value="platform"
          >
            {{ formatPlatformLabel(platform) }}
          </option>
        </select>
      </label>

      <label class="resource-field">
        <span class="resource-field__label">OS Name</span>
        <input
          v-model="values.os_name"
          class="resource-input"
          data-testid="eligibility-rule-os-name-input"
          name="os_name"
          type="text"
          :disabled="pending"
        >
      </label>

      <label class="resource-field">
        <span class="resource-field__label">OS Version Min</span>
        <input
          v-model="values.os_version_min"
          class="resource-input"
          data-testid="eligibility-rule-os-version-min-input"
          name="os_version_min"
          type="text"
          :disabled="pending"
        >
      </label>

      <label class="resource-field">
        <span class="resource-field__label">OS Version Max</span>
        <input
          v-model="values.os_version_max"
          class="resource-input"
          data-testid="eligibility-rule-os-version-max-input"
          name="os_version_max"
          type="text"
          :disabled="pending"
        >
      </label>

      <label class="resource-field">
        <span class="resource-field__label">Install Channel</span>
        <input
          v-model="values.install_channel"
          class="resource-input"
          data-testid="eligibility-rule-install-channel-input"
          name="install_channel"
          type="text"
          :disabled="pending"
        >
      </label>
    </div>

    <label class="resource-field">
      <span class="resource-field__label">Active Rule</span>
      <div class="resource-state__actions">
        <input
          v-model="values.is_active"
          data-testid="eligibility-rule-is-active-input"
          name="is_active"
          type="checkbox"
          :disabled="pending"
        >
        <span class="resource-key-value__value">
          Keep this rule enabled for participation checks.
        </span>
      </div>
    </label>

    <div class="resource-form__actions">
      <button
        class="resource-action"
        data-testid="eligibility-rule-submit"
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
