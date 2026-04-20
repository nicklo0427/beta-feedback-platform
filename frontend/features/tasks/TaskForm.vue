<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import { formatQualificationStatusLabel } from '~/features/eligibility/types'
import { useAppI18n } from '~/features/i18n/use-app-i18n'
import { formatPlatformLabel } from '~/features/platform-display'
import { fetchTaskAssignmentQualificationPreview } from '~/features/tasks/api'
import type { DeviceProfileListItem } from '~/features/device-profiles/types'
import {
  TASK_STATUSES,
  formatTaskStatusLabel,
  type TaskAssignmentQualificationPreview,
  type TaskFormValues
} from '~/features/tasks/types'
import { ApiClientError } from '~/services/api/client'

const props = withDefaults(
  defineProps<{
    campaignId: string
    actorId?: string | null
    initialValues: TaskFormValues
    deviceProfiles: DeviceProfileListItem[]
    lockDeviceProfile?: boolean
    pending?: boolean
    errorMessage?: string | null
    submitLabel?: string
    cancelTo: string
  }>(),
  {
    lockDeviceProfile: false,
    pending: false,
    errorMessage: null,
    submitLabel: undefined
  }
)

const emit = defineEmits<{
  submit: [values: TaskFormValues]
  change: [values: TaskFormValues]
}>()

const { locale, t } = useAppI18n()
const validationMessage = ref<string | null>(null)
const statusOptions = TASK_STATUSES
const resolvedSubmitLabel = computed(() => props.submitLabel || t('common.saveTask'))
const values = reactive<TaskFormValues>({
  ...props.initialValues
})
const selectedDeviceProfileId = computed(() => values.device_profile_id.trim())

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

watch(
  values,
  (nextValues) => {
    emit('change', { ...nextValues })
  },
  {
    deep: true,
    immediate: true
  }
)

const qualificationPreview = ref<TaskAssignmentQualificationPreview | null>(null)
const qualificationPreviewPending = ref(false)
const qualificationPreviewError = ref<Error | null>(null)
let qualificationPreviewRequestId = 0

function resetQualificationPreview(): void {
  qualificationPreview.value = null
  qualificationPreviewPending.value = false
  qualificationPreviewError.value = null
}

async function loadQualificationPreview(): Promise<void> {
  const actorId = props.actorId ?? null
  const deviceProfileId = selectedDeviceProfileId.value

  if (!deviceProfileId || !actorId) {
    resetQualificationPreview()
    return
  }

  const requestId = ++qualificationPreviewRequestId
  qualificationPreviewPending.value = true
  qualificationPreviewError.value = null

  try {
    const preview = await fetchTaskAssignmentQualificationPreview(
      props.campaignId,
      deviceProfileId,
      actorId
    )

    if (requestId !== qualificationPreviewRequestId) {
      return
    }

    qualificationPreviewError.value = null
    qualificationPreview.value = preview
  } catch (error) {
    if (requestId !== qualificationPreviewRequestId) {
      return
    }

    qualificationPreview.value = null
    qualificationPreviewError.value =
      error instanceof Error
        ? error
        : new Error(t('taskForm.qualificationErrorGeneric'))
  } finally {
    if (requestId === qualificationPreviewRequestId) {
      qualificationPreviewPending.value = false
    }
  }
}

async function refreshQualificationPreview(): Promise<void> {
  await loadQualificationPreview()
}

watch(
  [() => props.campaignId, () => props.actorId, selectedDeviceProfileId],
  async () => {
    await loadQualificationPreview()
  },
  {
    immediate: true
  }
)

const qualificationPreviewErrorMessage = computed(() => {
  if (!selectedDeviceProfileId.value) {
    return null
  }

  if (qualificationPreview.value) {
    return null
  }

  if (!props.actorId) {
    return t('taskForm.qualificationErrorNoActor')
  }

  if (!(qualificationPreviewError.value instanceof ApiClientError)) {
    return qualificationPreviewError.value?.message || t('taskForm.qualificationErrorGeneric')
  }

  if (qualificationPreviewError.value.code === 'forbidden_actor_role') {
    return t('taskForm.qualificationErrorForbiddenRole')
  }

  if (qualificationPreviewError.value.code === 'ownership_mismatch') {
    return t('taskForm.qualificationErrorOwnershipMismatch')
  }

  return qualificationPreviewError.value.message
})

const qualificationBlocksSubmit = computed(() => {
  if (!selectedDeviceProfileId.value) {
    return false
  }

  if (qualificationPreviewPending.value) {
    return true
  }

  return qualificationPreview.value?.qualification_status === 'not_qualified'
})

function validateForm(): boolean {
  if (!values.title.trim()) {
    validationMessage.value = t('taskForm.validationTitleRequired')
    return false
  }

  if (props.lockDeviceProfile && !selectedDeviceProfileId.value) {
    validationMessage.value = t('taskForm.validationDeviceProfileRequired')
    return false
  }

  if (
    selectedDeviceProfileId.value
    && qualificationPreview.value?.qualification_status === 'not_qualified'
  ) {
    validationMessage.value =
      qualificationPreview.value.reason_summary
      || t('taskForm.validationQualificationFailed')
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

    <section class="resource-form__section">
      <div>
        <h2 class="resource-form__section-title">{{ t('taskForm.basicTitle') }}</h2>
        <p class="resource-form__section-description">
          {{ t('taskForm.basicDescription') }}
        </p>
      </div>

      <div class="resource-form__section-grid">
        <label class="resource-field">
          <span class="resource-field__label">{{ t('taskForm.titleLabel') }}</span>
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
          <span class="resource-field__label">{{ t('taskForm.statusLabel') }}</span>
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
              {{ formatTaskStatusLabel(status, locale) }}
            </option>
          </select>
        </label>

        <label class="resource-field">
          <span class="resource-field__label">{{ t('taskForm.deviceProfileLabel') }}</span>
          <select
            v-model="values.device_profile_id"
            class="resource-select"
            data-testid="task-device-profile-field"
            name="device_profile_id"
            :disabled="pending || lockDeviceProfile"
          >
            <option v-if="!lockDeviceProfile" value="">
              {{ t('taskForm.unassignedDeviceProfile') }}
            </option>
            <option
              v-for="deviceProfile in deviceProfiles"
              :key="deviceProfile.id"
              :value="deviceProfile.id"
            >
              {{ deviceProfile.name }} ({{ formatPlatformLabel(deviceProfile.platform, locale) }})
            </option>
          </select>
        </label>
      </div>

      <label class="resource-field">
        <span class="resource-field__label">{{ t('taskForm.instructionSummaryLabel') }}</span>
        <textarea
          v-model="values.instruction_summary"
          class="resource-textarea"
          data-testid="task-instruction-summary-input"
          name="instruction_summary"
          rows="5"
          :disabled="pending"
        />
      </label>
    </section>

    <section
      v-if="selectedDeviceProfileId"
      class="resource-form__section"
      data-testid="task-assignment-preview-section"
    >
      <div>
        <h2 class="resource-form__section-title">{{ t('taskForm.qualificationTitle') }}</h2>
        <p class="resource-form__section-description">
          {{ t('taskForm.qualificationDescription') }}
        </p>
      </div>

      <section
        v-if="qualificationPreviewPending"
        class="resource-state"
        data-testid="task-assignment-preview-loading"
      >
        <h3 class="resource-state__title">{{ t('taskForm.qualificationLoadingTitle') }}</h3>
        <p class="resource-state__description">
          {{ t('taskForm.qualificationLoadingDescription') }}
        </p>
      </section>

      <section
        v-else-if="qualificationPreview"
        class="resource-section__body"
        data-testid="task-assignment-preview-panel"
      >
        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            {{ t('taskForm.qualificationStatusLabel') }}
            {{ formatQualificationStatusLabel(qualificationPreview.qualification_status, locale) }}
          </span>
          <span class="resource-shell__meta-chip">
            {{ t('taskForm.qualificationDeviceLabel') }} {{ qualificationPreview.device_profile_id }}
          </span>
          <span
            v-if="qualificationPreview.matched_rule_id"
            class="resource-shell__meta-chip"
          >
            {{ t('taskForm.qualificationMatchedRuleLabel') }} {{ qualificationPreview.matched_rule_id }}
          </span>
        </div>

        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">{{ t('taskForm.qualificationProfileLabel') }}</span>
            <span class="resource-key-value__value">
              {{ qualificationPreview.device_profile_name }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">{{ t('taskForm.qualificationSummaryLabel') }}</span>
            <span class="resource-key-value__value">
              {{ qualificationPreview.reason_summary || t('taskForm.qualificationSummaryEmpty') }}
            </span>
          </div>
        </div>
      </section>

      <section
        v-else-if="qualificationPreviewErrorMessage"
        class="resource-state"
        data-testid="task-assignment-preview-error"
      >
        <h3 class="resource-state__title">{{ t('taskForm.qualificationErrorTitle') }}</h3>
        <p class="resource-state__description">
          {{ qualificationPreviewErrorMessage }}
        </p>
        <div class="resource-state__actions">
          <button
            class="resource-action"
            type="button"
            @click="refreshQualificationPreview()"
          >
            {{ t('common.retry') }}
          </button>
        </div>
      </section>

    </section>

    <div class="resource-form__sticky-actions">
      <button
        class="resource-action"
        data-testid="task-submit"
        type="submit"
        :disabled="pending || qualificationBlocksSubmit"
      >
        {{ pending ? t('taskForm.saving') : resolvedSubmitLabel }}
      </button>
      <NuxtLink class="resource-action" :to="cancelTo">
        {{ t('taskForm.cancel') }}
      </NuxtLink>
    </div>
  </form>
</template>
