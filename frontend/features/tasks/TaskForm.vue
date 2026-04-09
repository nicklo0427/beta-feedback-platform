<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import { formatQualificationStatusLabel } from '~/features/eligibility/types'
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
  change: [values: TaskFormValues]
}>()

const validationMessage = ref<string | null>(null)
const statusOptions = TASK_STATUSES
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
        : new Error('目前無法檢查這個裝置設定檔的活動資格。')
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
    return '請先選擇目前操作帳號，才能檢查這個裝置設定檔是否符合活動資格。'
  }

  if (!(qualificationPreviewError.value instanceof ApiClientError)) {
    return qualificationPreviewError.value?.message || '目前無法檢查這個裝置設定檔的活動資格。'
  }

  if (qualificationPreviewError.value.code === 'forbidden_actor_role') {
    return '目前操作帳號角色不符合檢查任務指派資格的條件。'
  }

  if (qualificationPreviewError.value.code === 'ownership_mismatch') {
    return '你不能替不屬於自己的活動檢查指派資格。'
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
    validationMessage.value = '標題為必填。'
    return false
  }

  if (
    selectedDeviceProfileId.value
    && qualificationPreview.value?.qualification_status === 'not_qualified'
  ) {
    validationMessage.value =
      qualificationPreview.value.reason_summary
      || '目前選擇的裝置設定檔不符合活動資格條件。'
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

    <section
      v-if="selectedDeviceProfileId"
      class="resource-section"
      data-testid="task-assignment-preview-section"
    >
      <h2 class="resource-section__title">指派資格檢查</h2>

      <section
        v-if="qualificationPreviewPending"
        class="resource-state"
        data-testid="task-assignment-preview-loading"
      >
        <h3 class="resource-state__title">檢查裝置設定檔資格中</h3>
        <p class="resource-state__description">
          正在確認這個裝置設定檔是否符合目前活動的資格條件。
        </p>
      </section>

      <section
        v-else-if="qualificationPreview"
        class="resource-section__body"
        data-testid="task-assignment-preview-panel"
      >
        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            狀態 {{ formatQualificationStatusLabel(qualificationPreview.qualification_status) }}
          </span>
          <span class="resource-shell__meta-chip">
            裝置 {{ qualificationPreview.device_profile_id }}
          </span>
          <span
            v-if="qualificationPreview.matched_rule_id"
            class="resource-shell__meta-chip"
          >
            命中規則 {{ qualificationPreview.matched_rule_id }}
          </span>
        </div>

        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">裝置設定檔</span>
            <span class="resource-key-value__value">
              {{ qualificationPreview.device_profile_name }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">資格說明</span>
            <span class="resource-key-value__value">
              {{ qualificationPreview.reason_summary || '目前沒有額外資格說明。' }}
            </span>
          </div>
        </div>
      </section>

      <section
        v-else-if="qualificationPreviewErrorMessage"
        class="resource-state"
        data-testid="task-assignment-preview-error"
      >
        <h3 class="resource-state__title">無法取得指派資格結果</h3>
        <p class="resource-state__description">
          {{ qualificationPreviewErrorMessage }}
        </p>
        <div class="resource-state__actions">
          <button
            class="resource-action"
            type="button"
            @click="refreshQualificationPreview()"
          >
            重試
          </button>
        </div>
      </section>

    </section>

    <div class="resource-form__actions">
      <button
        class="resource-action"
        data-testid="task-submit"
        type="submit"
        :disabled="pending || qualificationBlocksSubmit"
      >
        {{ pending ? '儲存中...' : submitLabel }}
      </button>
      <NuxtLink class="resource-action" :to="cancelTo">
        取消
      </NuxtLink>
    </div>
  </form>
</template>
