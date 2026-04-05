<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import { formatPlatformLabel } from '~/features/platform-display'
import type { DeviceProfileListItem } from '~/features/device-profiles/types'
import {
  TASK_STATUSES,
  formatTaskStatusLabel,
  type TaskFormValues
} from '~/features/tasks/types'

const props = withDefaults(
  defineProps<{
    initialValues: TaskFormValues
    deviceProfiles: DeviceProfileListItem[]
    pending?: boolean
    errorMessage?: string | null
    submitLabel?: string
    cancelTo: string
  }>(),
  {
    pending: false,
    errorMessage: null,
    submitLabel: '儲存任務'
  }
)

const emit = defineEmits<{
  submit: [values: TaskFormValues]
}>()

const validationMessage = ref<string | null>(null)
const statusOptions = TASK_STATUSES
const values = reactive<TaskFormValues>({
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
  if (!values.title.trim()) {
    validationMessage.value = '標題為必填。'
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
    data-testid="task-form"
    @submit.prevent="handleSubmit"
  >
    <div
      v-if="validationMessage || errorMessage"
      class="resource-form__error"
      data-testid="task-form-error"
    >
      {{ validationMessage || errorMessage }}
    </div>

    <div class="resource-form__grid">
      <label class="resource-field">
        <span class="resource-field__label">標題</span>
        <input
          v-model="values.title"
          class="resource-input"
          data-testid="task-title-input"
          name="title"
          type="text"
          :disabled="pending"
        >
      </label>

      <label class="resource-field">
        <span class="resource-field__label">狀態</span>
        <select
          v-model="values.status"
          class="resource-select"
          data-testid="task-status-field"
          name="status"
          :disabled="pending"
        >
          <option
            v-for="status in statusOptions"
            :key="status"
            :value="status"
          >
            {{ formatTaskStatusLabel(status) }}
          </option>
        </select>
      </label>

      <label class="resource-field">
        <span class="resource-field__label">裝置設定檔</span>
        <select
          v-model="values.device_profile_id"
          class="resource-select"
          data-testid="task-device-profile-field"
          name="device_profile_id"
          :disabled="pending"
        >
          <option value="">尚未指派裝置設定檔</option>
          <option
            v-for="deviceProfile in deviceProfiles"
            :key="deviceProfile.id"
            :value="deviceProfile.id"
          >
            {{ deviceProfile.name }} ({{ formatPlatformLabel(deviceProfile.platform) }})
          </option>
        </select>
      </label>
    </div>

    <label class="resource-field">
      <span class="resource-field__label">任務說明摘要</span>
      <textarea
        v-model="values.instruction_summary"
        class="resource-textarea"
        data-testid="task-instruction-summary-input"
        name="instruction_summary"
        rows="5"
        :disabled="pending"
      />
    </label>

    <div class="resource-form__actions">
      <button
        class="resource-action"
        data-testid="task-submit"
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
