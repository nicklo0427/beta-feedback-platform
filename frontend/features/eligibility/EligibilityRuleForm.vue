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
    submitLabel: '儲存資格規則'
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
    validationMessage.value = '平台為必填。'
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

    <section class="resource-form__section">
      <div>
        <h2 class="resource-form__section-title">資格條件</h2>
        <p class="resource-form__section-description">
          這條規則會參與 qualification 判斷，欄位之間以 AND 組合；空白欄位代表不限制。
        </p>
      </div>

      <div class="resource-form__section-grid">
        <label class="resource-field">
          <span class="resource-field__label">平台</span>
          <select
            v-model="values.platform"
            class="resource-select"
            data-testid="eligibility-rule-platform-select"
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
          <span class="resource-field__label">作業系統名稱</span>
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
          <span class="resource-field__label">最低作業系統版本</span>
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
          <span class="resource-field__label">最高作業系統版本</span>
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
          <span class="resource-field__label">安裝管道</span>
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
    </section>

    <section class="resource-form__section">
      <div>
        <h2 class="resource-form__section-title">規則狀態</h2>
        <p class="resource-form__section-description">
          停用的規則會被 evaluator 忽略，保留作為歷史設定參考。
        </p>
      </div>

      <label class="resource-field">
        <span class="resource-field__label">啟用規則</span>
        <span class="resource-inline-toggle">
          <input
            v-model="values.is_active"
            data-testid="eligibility-rule-is-active-input"
            name="is_active"
            type="checkbox"
            :disabled="pending"
          >
          <span class="resource-inline-toggle__copy">
            <span class="resource-choice-card__label">作為當前資格判斷依據</span>
            <span class="resource-choice-card__hint">關閉後仍會保留在系統中，但不參與比對。</span>
          </span>
        </span>
      </label>
    </section>

    <div class="resource-form__sticky-actions">
      <button
        class="resource-action"
        data-testid="eligibility-rule-submit"
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
