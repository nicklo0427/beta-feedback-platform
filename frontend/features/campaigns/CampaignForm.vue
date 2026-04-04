<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import { CAMPAIGN_STATUSES, CAMPAIGN_TARGET_PLATFORM_OPTIONS, type CampaignFormValues } from '~/features/campaigns/types'
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
    submitLabel: 'Save campaign',
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
    validationMessage.value = 'Name is required.'
    return false
  }

  if (values.target_platforms.length === 0) {
    validationMessage.value = 'Select at least one target platform.'
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

    <div class="resource-form__grid">
      <label class="resource-field">
        <span class="resource-field__label">Name</span>
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
        <span class="resource-field__label">Version Label</span>
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
        <span class="resource-field__label">Status</span>
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
            {{ status }}
          </option>
        </select>
      </label>
    </div>

    <label class="resource-field">
      <span class="resource-field__label">Description</span>
      <textarea
        v-model="values.description"
        class="resource-textarea"
        data-testid="campaign-description-input"
        name="description"
        rows="4"
        :disabled="pending"
      />
    </label>

    <label class="resource-field">
      <span class="resource-field__label">Target Platforms</span>
      <div class="resource-state">
        <div class="resource-state__actions">
          <label
            v-for="platform in CAMPAIGN_TARGET_PLATFORM_OPTIONS"
            :key="platform"
            class="resource-key-value__value"
          >
            <input
              :checked="hasTargetPlatform(platform)"
              :disabled="pending"
              :data-testid="`campaign-platform-checkbox-${platform}`"
              :name="`target_platforms_${platform}`"
              type="checkbox"
              @change="toggleTargetPlatform(platform)"
            >
            {{ formatPlatformLabel(platform) }}
          </label>
        </div>
      </div>
    </label>

    <label
      v-if="!allowStatusEdit"
      class="resource-field"
    >
      <span class="resource-field__label">Initial Status</span>
      <span class="resource-key-value__value" data-testid="campaign-status-default-note">
        New campaigns start as <strong>draft</strong> by default.
      </span>
    </label>

    <div class="resource-form__actions">
      <button
        class="resource-action"
        data-testid="campaign-submit"
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
