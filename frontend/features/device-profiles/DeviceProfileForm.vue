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
    submitLabel: '儲存裝置設定檔'
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
    { key: 'name', label: '名稱' },
    { key: 'platform', label: '平台' },
    { key: 'device_model', label: '裝置型號' },
    { key: 'os_name', label: '作業系統名稱' }
  ]

  for (const field of requiredFields) {
    const rawValue = values[field.key]

    if (typeof rawValue !== 'string' || !rawValue.trim()) {
      validationMessage.value = `${field.label}為必填。`
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
        <span class="resource-field__label">名稱</span>
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
        <span class="resource-field__label">平台</span>
        <select
          v-model="values.platform"
          class="resource-select"
          data-testid="device-profile-platform-select"
          name="platform"
          :disabled="pending"
        >
          <option value="">請選擇平台</option>
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
        <span class="resource-field__label">裝置型號</span>
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
        <span class="resource-field__label">作業系統名稱</span>
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
        <span class="resource-field__label">安裝來源 / 發佈渠道</span>
        <input
          v-model="values.install_channel"
          class="resource-input"
          data-testid="device-profile-install-channel-input"
          name="install_channel"
          type="text"
          :disabled="pending"
        >
      </label>

      <label class="resource-field">
        <span class="resource-field__label">作業系統版本</span>
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
        <span class="resource-field__label">瀏覽器名稱</span>
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
        <span class="resource-field__label">瀏覽器版本</span>
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
        <span class="resource-field__label">語系</span>
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
      <span class="resource-field__label">備註</span>
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
        {{ pending ? '儲存中...' : submitLabel }}
      </button>
      <NuxtLink class="resource-action" :to="cancelTo">
        取消
      </NuxtLink>
    </div>
  </form>
</template>
