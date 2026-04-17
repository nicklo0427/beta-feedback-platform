<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import type { ProjectFormValues } from '~/features/projects/types'

const props = withDefaults(
  defineProps<{
    initialValues: ProjectFormValues
    pending?: boolean
    errorMessage?: string | null
    submitLabel?: string
    cancelTo: string
  }>(),
  {
    pending: false,
    errorMessage: null,
    submitLabel: '儲存專案'
  }
)

const emit = defineEmits<{
  submit: [values: ProjectFormValues]
}>()

const validationMessage = ref<string | null>(null)
const values = reactive<ProjectFormValues>({
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
  if (!values.name.trim()) {
    validationMessage.value = '名稱為必填。'
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
    data-testid="project-form"
    @submit.prevent="handleSubmit"
  >
    <div
      v-if="validationMessage || errorMessage"
      class="resource-form__error"
      data-testid="project-form-error"
    >
      {{ validationMessage || errorMessage }}
    </div>

    <section class="resource-form__section">
      <div>
        <h2 class="resource-form__section-title">基本資料</h2>
        <p class="resource-form__section-description">
          先定義專案名稱與範圍描述，後續活動會延續這個產品脈絡。
        </p>
      </div>

      <div class="resource-form__section-grid">
        <label class="resource-field">
          <span class="resource-field__label">名稱</span>
          <input
            v-model="values.name"
            class="resource-input"
            data-testid="project-name-input"
            name="name"
            type="text"
            :disabled="pending"
          >
        </label>
      </div>
    </section>

    <section class="resource-form__section">
      <div>
        <h2 class="resource-form__section-title">專案說明</h2>
        <p class="resource-form__section-description">
          用簡短文字說明這個專案的測試目標、產品範圍或目前版本情境。
        </p>
      </div>

      <label class="resource-field">
        <span class="resource-field__label">說明</span>
        <textarea
          v-model="values.description"
          class="resource-textarea"
          data-testid="project-description-input"
          name="description"
          rows="5"
          :disabled="pending"
        />
      </label>
    </section>

    <div class="resource-form__sticky-actions">
      <button
        class="resource-action"
        data-testid="project-submit"
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
