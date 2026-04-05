<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import {
  ACCOUNT_ROLE_OPTIONS,
  formatAccountRoleLabel,
  type AccountFormValues
} from '~/features/accounts/types'

const props = withDefaults(
  defineProps<{
    initialValues: AccountFormValues
    pending?: boolean
    errorMessage?: string | null
    submitLabel?: string
    cancelTo: string
  }>(),
  {
    pending: false,
    errorMessage: null,
    submitLabel: '儲存帳號'
  }
)

const emit = defineEmits<{
  submit: [values: AccountFormValues]
}>()

const validationMessage = ref<string | null>(null)
const values = reactive<AccountFormValues>({
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
  if (!values.display_name.trim()) {
    validationMessage.value = '顯示名稱為必填。'
    return false
  }

  if (!values.role.trim()) {
    validationMessage.value = '角色為必填。'
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
    data-testid="account-form"
    @submit.prevent="handleSubmit"
  >
    <div
      v-if="validationMessage || errorMessage"
      class="resource-form__error"
      data-testid="account-form-error"
    >
      {{ validationMessage || errorMessage }}
    </div>

    <div class="resource-form__grid">
      <label class="resource-field">
        <span class="resource-field__label">顯示名稱</span>
        <input
          v-model="values.display_name"
          class="resource-input"
          data-testid="account-display-name-input"
          name="display_name"
          type="text"
          :disabled="pending"
        >
      </label>

      <label class="resource-field">
        <span class="resource-field__label">角色</span>
        <select
          v-model="values.role"
          class="resource-select"
          data-testid="account-role-select"
          name="role"
          :disabled="pending"
        >
          <option value="">請選擇角色</option>
          <option
            v-for="role in ACCOUNT_ROLE_OPTIONS"
            :key="role"
            :value="role"
          >
            {{ formatAccountRoleLabel(role) }}
          </option>
        </select>
      </label>

      <label class="resource-field">
        <span class="resource-field__label">語系</span>
        <input
          v-model="values.locale"
          class="resource-input"
          data-testid="account-locale-input"
          name="locale"
          type="text"
          :disabled="pending"
        >
      </label>
    </div>

    <label class="resource-field">
      <span class="resource-field__label">簡介</span>
      <textarea
        v-model="values.bio"
        class="resource-textarea"
        data-testid="account-bio-input"
        name="bio"
        rows="5"
        :disabled="pending"
      />
    </label>

    <div class="resource-form__actions">
      <button
        class="resource-action"
        data-testid="account-submit"
        type="button"
        :disabled="pending"
        @click="handleSubmit"
      >
        {{ pending ? '儲存中...' : submitLabel }}
      </button>
      <NuxtLink class="resource-action" :to="cancelTo">
        取消
      </NuxtLink>
    </div>
  </form>
</template>
