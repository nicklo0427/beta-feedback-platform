<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import type {
  ParticipationRequestFormValues,
  ParticipationRequestQualifiedDeviceProfileOption
} from './types'

const props = withDefaults(
  defineProps<{
    initialValues: ParticipationRequestFormValues
    qualifiedDeviceProfiles: ParticipationRequestQualifiedDeviceProfileOption[]
    pending?: boolean
    errorMessage?: string | null
    successMessage?: string | null
    submitLabel?: string
    testIdPrefix?: string
  }>(),
  {
    pending: false,
    errorMessage: null,
    successMessage: null,
    submitLabel: '送出參與意圖',
    testIdPrefix: 'participation-request'
  }
)

const emit = defineEmits<{
  submit: [values: ParticipationRequestFormValues]
}>()

const validationMessage = ref<string | null>(null)
const resolvedTestIdPrefix = computed(() => props.testIdPrefix)
const values = reactive<ParticipationRequestFormValues>({
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
  if (!values.device_profile_id.trim()) {
    validationMessage.value = '請先選擇要送出參與意圖的裝置設定檔。'
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
    :data-testid="`${resolvedTestIdPrefix}-form`"
    @submit.prevent="handleSubmit"
  >
    <div
      v-if="validationMessage || errorMessage"
      class="resource-form__error"
      :data-testid="`${resolvedTestIdPrefix}-error`"
    >
      {{ validationMessage || errorMessage }}
    </div>

    <div
      v-if="successMessage"
      class="resource-state"
      :data-testid="`${resolvedTestIdPrefix}-success`"
    >
      <p class="resource-state__description">
        {{ successMessage }}
      </p>
    </div>

    <div class="resource-form__grid">
      <label class="resource-field">
        <span class="resource-field__label">使用的裝置設定檔</span>
        <select
          v-model="values.device_profile_id"
          class="resource-select"
          :data-testid="`${resolvedTestIdPrefix}-device-profile-select`"
          name="device_profile_id"
          :disabled="pending"
        >
          <option value="">請選擇裝置設定檔</option>
          <option
            v-for="deviceProfile in qualifiedDeviceProfiles"
            :key="deviceProfile.id"
            :value="deviceProfile.id"
          >
            {{ deviceProfile.name }}
          </option>
        </select>
      </label>
    </div>

    <label class="resource-field">
      <span class="resource-field__label">想補充給開發者的說明</span>
      <textarea
        v-model="values.note"
        class="resource-textarea"
        :data-testid="`${resolvedTestIdPrefix}-note-input`"
        name="note"
        rows="4"
        :disabled="pending"
      />
    </label>

    <div class="resource-form__actions">
      <button
        class="resource-action"
        :data-testid="`${resolvedTestIdPrefix}-submit`"
        type="submit"
        :disabled="pending"
      >
        {{ pending ? '送出中...' : submitLabel }}
      </button>
    </div>
  </form>
</template>
