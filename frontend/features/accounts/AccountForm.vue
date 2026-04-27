<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import {
  ACCOUNT_ROLE_OPTIONS,
  formatAccountRoleLabel,
  normalizeAccountRoles,
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
  ...props.initialValues,
  roles: [...props.initialValues.roles]
})

watch(
  () => props.initialValues,
  (nextValues) => {
    Object.assign(values, {
      ...nextValues,
      roles: [...nextValues.roles]
    })
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

  if (values.roles.length === 0) {
    validationMessage.value = '請至少選擇一種身份。'
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
    roles: normalizeAccountRoles({ roles: values.roles })
  })
}

function roleIsSelected(role: AccountFormValues['roles'][number]): boolean {
  return values.roles.includes(role)
}

function toggleRole(role: AccountFormValues['roles'][number]): void {
  if (props.pending) {
    return
  }

  if (roleIsSelected(role)) {
    values.roles = values.roles.filter((selectedRole) => selectedRole !== role)
    return
  }

  values.roles = normalizeAccountRoles({
    roles: [...values.roles, role]
  })
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

    <section class="resource-form__section">
      <div>
        <h2 class="resource-form__section-title">帳號識別</h2>
        <p class="resource-form__section-description">
          這些欄位會決定首頁、工作區與協作流程如何依角色顯示。
        </p>
      </div>

      <div class="resource-form__section-grid">
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

        <fieldset class="resource-field">
          <legend class="resource-field__label">身份</legend>
          <div
            class="resource-choice-grid"
            data-testid="account-role-options"
          >
            <label
              v-for="role in ACCOUNT_ROLE_OPTIONS"
              :key="role"
              class="resource-choice-card"
            >
              <input
                :checked="roleIsSelected(role)"
                :disabled="pending"
                :data-testid="`account-role-checkbox-${role}`"
                :name="`roles_${role}`"
                type="checkbox"
                @change="toggleRole(role)"
              >
              <span class="resource-choice-card__content">
                <span class="resource-choice-card__label">
                  {{ formatAccountRoleLabel(role) }}
                </span>
                <span class="resource-choice-card__hint">
                  {{
                    role === 'developer'
                      ? '可以發起試玩、管理活動並審閱回饋。'
                      : '可以加入試用、管理裝置並提交回饋。'
                  }}
                </span>
              </span>
            </label>
          </div>
        </fieldset>

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
    </section>

    <section class="resource-form__section">
      <div>
        <h2 class="resource-form__section-title">個人簡介</h2>
        <p class="resource-form__section-description">
          簡短描述這個帳號的背景，讓協作頁面更容易判讀使用情境。
        </p>
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
    </section>

    <div class="resource-form__sticky-actions">
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
