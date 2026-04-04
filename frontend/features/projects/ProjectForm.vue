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
    submitLabel: 'Save project'
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
    validationMessage.value = 'Name is required.'
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

    <div class="resource-form__grid">
      <label class="resource-field">
        <span class="resource-field__label">Name</span>
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

    <label class="resource-field">
      <span class="resource-field__label">Description</span>
      <textarea
        v-model="values.description"
        class="resource-textarea"
        data-testid="project-description-input"
        name="description"
        rows="5"
        :disabled="pending"
      />
    </label>

    <div class="resource-form__actions">
      <button
        class="resource-action"
        data-testid="project-submit"
        type="submit"
        :disabled="pending"
      >
        {{ pending ? 'Saving...' : submitLabel }}
      </button>
      <NuxtLink class="resource-action" :to="cancelTo">
        Cancel
      </NuxtLink>
    </div>
  </form>
</template>
