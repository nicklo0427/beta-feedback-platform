<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import {
  CAMPAIGN_STATUSES,
  CAMPAIGN_TARGET_PLATFORM_OPTIONS,
  formatCampaignStatusLabel,
  type CampaignFormValues
} from '~/features/campaigns/types'
import { formatPlatformLabel } from '~/features/platform-display'

const props = withDefaults(
  defineProps<{
    initialValues: CampaignFormValues
    pending?: boolean
    errorMessage?: string | null
    submitLabel?: string
    cancelTo: string
    allowStatusEdit?: boolean
  }>(),
  {
    pending: false,
    errorMessage: null,
    submitLabel: '儲存活動',
    allowStatusEdit: false
  }
)

const emit = defineEmits<{
  submit: [values: CampaignFormValues]
}>()

const validationMessage = ref<string | null>(null)
const values = reactive<CampaignFormValues>({
  ...props.initialValues,
  target_platforms: [...props.initialValues.target_platforms]
})

watch(
  () => props.initialValues,
  (nextValues) => {
    values.name = nextValues.name
    values.description = nextValues.description
    values.target_platforms = [...nextValues.target_platforms]
    values.version_label = nextValues.version_label
    values.status = nextValues.status
    validationMessage.value = null
  },
  {
    immediate: true
  }
)

function hasTargetPlatform(platform: string): boolean {
  return values.target_platforms.includes(platform as typeof values.target_platforms[number])
}

function toggleTargetPlatform(platform: typeof CAMPAIGN_TARGET_PLATFORM_OPTIONS[number]): void {
  if (hasTargetPlatform(platform)) {
    values.target_platforms = values.target_platforms.filter(
      (candidate) => candidate !== platform
    )
    return
  }

  values.target_platforms = [...values.target_platforms, platform]
}

function validateForm(): boolean {
  if (!values.name.trim()) {
    validationMessage.value = '名稱為必填。'
    return false
  }

  if (values.target_platforms.length === 0) {
    validationMessage.value = '請至少選擇一個目標平台。'
    return false
  }

  validationMessage.value = null
  return true
}

function handleSubmit(): void {
  if (!validateForm()) {
    return
  }

  emit('submit', {
    ...values,
    target_platforms: [...values.target_platforms]
  })
}
</script>

<template>
  <form
    class="resource-form"
    data-testid="campaign-form"
    @submit.prevent="handleSubmit"
  >
    <div
      v-if="validationMessage || errorMessage"
      class="resource-form__error"
      data-testid="campaign-form-error"
    >
      {{ validationMessage || errorMessage }}
    </div>

    <section class="resource-form__section">
      <div>
        <h2 class="resource-form__section-title">活動基本資料</h2>
        <p class="resource-form__section-description">
          先建立活動名稱、版本標籤與描述，讓後續資格規則與任務指派有清楚的產品上下文。
        </p>
      </div>

      <div class="resource-form__section-grid">
        <label class="resource-field">
          <span class="resource-field__label">名稱</span>
          <input
            v-model="values.name"
            class="resource-input"
            data-testid="campaign-name-input"
            name="name"
            type="text"
            :disabled="pending"
          >
        </label>

        <label class="resource-field">
          <span class="resource-field__label">版本標籤</span>
          <input
            v-model="values.version_label"
            class="resource-input"
            data-testid="campaign-version-label-input"
            name="version_label"
            type="text"
            :disabled="pending"
          >
        </label>

        <label
          v-if="allowStatusEdit"
          class="resource-field"
        >
          <span class="resource-field__label">狀態</span>
          <select
            v-model="values.status"
            class="resource-select"
            data-testid="campaign-status-field"
            name="status"
            :disabled="pending"
          >
            <option
              v-for="status in CAMPAIGN_STATUSES"
              :key="status"
              :value="status"
            >
              {{ formatCampaignStatusLabel(status) }}
            </option>
          </select>
        </label>
      </div>

      <label class="resource-field">
        <span class="resource-field__label">說明</span>
        <textarea
          v-model="values.description"
          class="resource-textarea"
          data-testid="campaign-description-input"
          name="description"
          rows="4"
          :disabled="pending"
        />
      </label>
    </section>

    <section class="resource-form__section">
      <div>
        <h2 class="resource-form__section-title">目標平台</h2>
        <p class="resource-form__section-description">
          選擇這個活動預計覆蓋的平台，資格規則與裝置設定檔會以這裡為第一層篩選。
        </p>
      </div>

      <div class="resource-choice-grid">
        <label
          v-for="platform in CAMPAIGN_TARGET_PLATFORM_OPTIONS"
          :key="platform"
          class="resource-choice-card"
        >
          <input
            :checked="hasTargetPlatform(platform)"
            :disabled="pending"
            :data-testid="`campaign-platform-checkbox-${platform}`"
            :name="`target_platforms_${platform}`"
            type="checkbox"
            @change="toggleTargetPlatform(platform)"
          >
          <span class="resource-choice-card__content">
            <span class="resource-choice-card__label">{{ formatPlatformLabel(platform) }}</span>
            <span class="resource-choice-card__hint">納入活動資格與任務分派範圍。</span>
          </span>
        </label>
      </div>

      <label
        v-if="!allowStatusEdit"
        class="resource-field"
      >
        <span class="resource-field__label">初始狀態</span>
        <span class="resource-key-value__value" data-testid="campaign-status-default-note">
          新建立的活動預設會以 <strong>草稿</strong> 狀態開始。
        </span>
      </label>
    </section>

    <div class="resource-form__sticky-actions">
      <button
        class="resource-action"
        data-testid="campaign-submit"
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
