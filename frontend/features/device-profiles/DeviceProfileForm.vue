<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import {
  DEVICE_PROFILE_PLATFORM_OPTIONS,
  type DeviceProfileFormValues
} from '~/features/device-profiles/types'
import { formatPlatformLabel } from '~/features/platform-display'

const props = withDefaults(
  defineProps<{
    initialValues: DeviceProfileFormValues
    pending?: boolean
    errorMessage?: string | null
    submitLabel?: string
    cancelTo: string
  }>(),
  {
    pending: false,
    errorMessage: null,
    submitLabel: 'Save device profile'
  }
)

const emit = defineEmits<{
  submit: [values: DeviceProfileFormValues]
}>()

const platformOptions = DEVICE_PROFILE_PLATFORM_OPTIONS
const validationMessage = ref<string | null>(null)
const values = reactive<DeviceProfileFormValues>({
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
  const requiredFields: Array<{
    key: keyof Pick<
      DeviceProfileFormValues,
      'name' | 'platform' | 'device_model' | 'os_name'
    >
    label: string
  }> = [
    { key: 'name', label: 'Name' },
    { key: 'platform', label: 'Platform' },
    { key: 'device_model', label: 'Device model' },
    { key: 'os_name', label: 'OS name' }
  ]

  for (const field of requiredFields) {
    const rawValue = values[field.key]

    if (typeof rawValue !== 'string' || !rawValue.trim()) {
      validationMessage.value = `${field.label} is required.`
      return false
    }
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
    data-testid="device-profile-form"
    @submit.prevent="handleSubmit"
  >
    <div
      v-if="validationMessage || errorMessage"
      class="resource-form__error"
      data-testid="device-profile-form-error"
    >
      {{ validationMessage || errorMessage }}
    </div>

    <div class="resource-form__grid">
      <label class="resource-field">
        <span class="resource-field__label">Name</span>
        <input
          v-model="values.name"
          class="resource-input"
          data-testid="device-profile-name-input"
          name="name"
          type="text"
          :disabled="pending"
        >
      </label>

      <label class="resource-field">
        <span class="resource-field__label">Platform</span>
        <select
          v-model="values.platform"
          class="resource-select"
          data-testid="device-profile-platform-select"
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
        <span class="resource-field__label">Device Model</span>
        <input
          v-model="values.device_model"
          class="resource-input"
          data-testid="device-profile-device-model-input"
          name="device_model"
          type="text"
          :disabled="pending"
        >
      </label>

      <label class="resource-field">
        <span class="resource-field__label">OS Name</span>
        <input
          v-model="values.os_name"
          class="resource-input"
          data-testid="device-profile-os-name-input"
          name="os_name"
          type="text"
          :disabled="pending"
        >
      </label>

      <label class="resource-field">
        <span class="resource-field__label">OS Version</span>
        <input
          v-model="values.os_version"
          class="resource-input"
          data-testid="device-profile-os-version-input"
          name="os_version"
          type="text"
          :disabled="pending"
        >
      </label>

      <label class="resource-field">
        <span class="resource-field__label">Browser Name</span>
        <input
          v-model="values.browser_name"
          class="resource-input"
          data-testid="device-profile-browser-name-input"
          name="browser_name"
          type="text"
          :disabled="pending"
        >
      </label>

      <label class="resource-field">
        <span class="resource-field__label">Browser Version</span>
        <input
          v-model="values.browser_version"
          class="resource-input"
          data-testid="device-profile-browser-version-input"
          name="browser_version"
          type="text"
          :disabled="pending"
        >
      </label>

      <label class="resource-field">
        <span class="resource-field__label">Locale</span>
        <input
          v-model="values.locale"
          class="resource-input"
          data-testid="device-profile-locale-input"
          name="locale"
          type="text"
          :disabled="pending"
        >
      </label>
    </div>

    <label class="resource-field">
      <span class="resource-field__label">Notes</span>
      <textarea
        v-model="values.notes"
        class="resource-textarea"
        data-testid="device-profile-notes-input"
        name="notes"
        rows="5"
        :disabled="pending"
      />
    </label>

    <div class="resource-form__actions">
      <button
        class="resource-action"
        data-testid="device-profile-submit"
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
