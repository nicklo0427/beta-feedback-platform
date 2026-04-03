<script setup lang="ts">
import { ref } from 'vue'

import DeviceProfileForm from '~/features/device-profiles/DeviceProfileForm.vue'
import { createDeviceProfile } from '~/features/device-profiles/api'
import {
  buildDeviceProfileCreatePayload,
  createEmptyDeviceProfileFormValues
} from '~/features/device-profiles/form'
import type { DeviceProfileFormValues } from '~/features/device-profiles/types'
import { ApiClientError } from '~/services/api/client'

const router = useRouter()
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = createEmptyDeviceProfileFormValues()

async function handleSubmit(values: DeviceProfileFormValues): Promise<void> {
  submitError.value = null
  submitting.value = true

  try {
    const createdDeviceProfile = await createDeviceProfile(
      buildDeviceProfileCreatePayload(values)
    )
    await router.push(`/device-profiles/${createdDeviceProfile.id}`)
  } catch (error) {
    submitError.value =
      error instanceof ApiClientError
        ? error.message
        : 'Unable to save the device profile right now.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/device-profiles">
          Device Profiles
        </NuxtLink>
        <h1 class="resource-shell__title">Create Device Profile</h1>
        <p class="resource-shell__description">
          建立一筆最小的 Tester Device Profile，讓後續 eligibility、task assignment 與 feedback context 可以直接引用。
        </p>
      </header>

      <section class="resource-section" data-testid="device-profile-create-panel">
        <h2 class="resource-section__title">New Device Profile</h2>
        <DeviceProfileForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="Create device profile"
          cancel-to="/device-profiles"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
