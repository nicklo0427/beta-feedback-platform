<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import { useAppI18n } from '~/features/i18n/use-app-i18n'
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
    submitLabel: undefined,
    testIdPrefix: 'participation-request'
  }
)

const emit = defineEmits<{
  submit: [values: ParticipationRequestFormValues]
}>()

const { t } = useAppI18n()
const validationMessage = ref<string | null>(null)
const resolvedTestIdPrefix = computed(() => props.testIdPrefix)
const resolvedSubmitLabel = computed(() => props.submitLabel || t('common.submitParticipationRequest'))
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
    validationMessage.value = t('participationForm.validationDeviceProfileRequired')
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

    <section class="resource-form__section">
      <div>
        <h2 class="resource-form__section-title">{{ t('participationForm.title') }}</h2>
        <p class="resource-form__section-description">
          {{ t('participationForm.description') }}
        </p>
      </div>

      <div class="resource-form__section-grid">
        <label class="resource-field">
          <span class="resource-field__label">{{ t('participationForm.deviceProfileLabel') }}</span>
          <select
            v-model="values.device_profile_id"
            class="resource-select"
            :data-testid="`${resolvedTestIdPrefix}-device-profile-select`"
            name="device_profile_id"
            :disabled="pending"
          >
            <option value="">{{ t('participationForm.deviceProfilePlaceholder') }}</option>
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
        <span class="resource-field__label">{{ t('participationForm.noteLabel') }}</span>
        <textarea
          v-model="values.note"
          class="resource-textarea"
          :data-testid="`${resolvedTestIdPrefix}-note-input`"
          name="note"
          rows="4"
          :disabled="pending"
        />
      </label>
    </section>

    <div class="resource-form__sticky-actions">
      <button
        class="resource-action"
        :data-testid="`${resolvedTestIdPrefix}-submit`"
        type="submit"
        :disabled="pending"
      >
        {{ pending ? t('participationForm.submitting') : resolvedSubmitLabel }}
      </button>
    </div>
  </form>
</template>
