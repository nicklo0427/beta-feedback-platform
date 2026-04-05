<script setup lang="ts">
import { ref } from 'vue'

import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import DeviceProfileForm from '~/features/device-profiles/DeviceProfileForm.vue'
import { createDeviceProfile } from '~/features/device-profiles/api'
import {
  buildDeviceProfileCreatePayload,
  createEmptyDeviceProfileFormValues
} from '~/features/device-profiles/form'
import type { DeviceProfileFormValues } from '~/features/device-profiles/types'
import { ApiClientError } from '~/services/api/client'

const router = useRouter()
useCurrentActorPersistence()

const currentActorId = useCurrentActorId()
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = createEmptyDeviceProfileFormValues()

async function handleSubmit(values: DeviceProfileFormValues): Promise<void> {
  if (!currentActorId.value) {
    submitError.value = '請先選擇目前操作帳號，再建立裝置設定檔。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const createdDeviceProfile = await createDeviceProfile(
      buildDeviceProfileCreatePayload(values),
      currentActorId.value
    )
    await router.push(`/device-profiles/${createdDeviceProfile.id}`)
  } catch (error) {
    submitError.value =
      error instanceof ApiClientError
        ? error.message
        : '目前無法儲存裝置設定檔。'
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
          裝置設定檔
        </NuxtLink>
        <h1 class="resource-shell__title">建立裝置設定檔</h1>
        <p class="resource-shell__description">
          建立一筆最小的測試裝置設定檔，讓後續資格條件、任務指派與回饋情境可以直接引用。
        </p>
      </header>

      <CurrentActorSelector
        title="裝置設定檔擁有者"
        description="選擇目前正在操作的測試者帳號，建立後會自動寫入裝置設定檔的擁有者欄位。"
      />

      <section class="resource-section" data-testid="device-profile-create-panel">
        <h2 class="resource-section__title">新增裝置設定檔</h2>
        <DeviceProfileForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="建立裝置設定檔"
          cancel-to="/device-profiles"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
