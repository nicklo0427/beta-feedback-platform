<script setup lang="ts">
definePageMeta({
  path: '/device-profiles/:deviceProfileId/edit'
})

import { computed, ref, watch } from 'vue'

import DeviceProfileForm from '~/features/device-profiles/DeviceProfileForm.vue'
import {
  fetchDeviceProfileDetail,
  updateDeviceProfile
} from '~/features/device-profiles/api'
import {
  buildDeviceProfileUpdatePayload,
  createEmptyDeviceProfileFormValues,
  toDeviceProfileFormValues
} from '~/features/device-profiles/form'
import type { DeviceProfileFormValues } from '~/features/device-profiles/types'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
const deviceProfileId = computed(() => String(route.params.deviceProfileId))
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = ref(createEmptyDeviceProfileFormValues())

const {
  data: deviceProfile,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `device-profile-edit-${deviceProfileId.value}`,
  () => fetchDeviceProfileDetail(deviceProfileId.value),
  {
    server: false,
    watch: [deviceProfileId],
    default: () => null
  }
)

watch(
  deviceProfile,
  (nextDeviceProfile) => {
    if (!nextDeviceProfile) {
      return
    }

    initialValues.value = toDeviceProfileFormValues(nextDeviceProfile)
    submitError.value = null
  },
  {
    immediate: true
  }
)

async function handleSubmit(values: DeviceProfileFormValues): Promise<void> {
  if (!deviceProfile.value) {
    submitError.value = '目前無法取得裝置設定檔內容。'
    return
  }

  const payload = buildDeviceProfileUpdatePayload(values, initialValues.value)

  if (!payload) {
    submitError.value = '目前沒有可儲存的變更。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const updatedDeviceProfile = await updateDeviceProfile(deviceProfileId.value, payload)
    await router.push(`/device-profiles/${updatedDeviceProfile.id}`)
  } catch (submitFailure) {
    submitError.value =
      submitFailure instanceof ApiClientError
        ? submitFailure.message
        : '目前無法更新裝置設定檔。'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" :to="`/device-profiles/${deviceProfileId}`">
          裝置設定檔詳情
        </NuxtLink>
        <h1 class="resource-shell__title">編輯裝置設定檔</h1>
        <p class="resource-shell__description">
          更新既有的測試裝置設定檔，維持後續資格條件、任務與回饋流程使用的裝置資訊一致。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="device-profile-edit-loading"
      >
        <h2 class="resource-state__title">載入裝置設定檔編輯表單中</h2>
        <p class="resource-state__description">
          正在從 API 載入既有裝置設定檔。
        </p>
      </section>

      <section
        v-else-if="error || !deviceProfile"
        class="resource-state"
        data-testid="device-profile-edit-error"
      >
        <h2 class="resource-state__title">無法載入裝置設定檔編輯表單</h2>
        <p class="resource-state__description">
          {{ error?.message || '找不到指定的裝置設定檔。' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試
          </button>
          <NuxtLink class="resource-action" to="/device-profiles">
            返回裝置設定檔列表
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="device-profile-edit-panel"
      >
        <h2 class="resource-section__title">編輯 {{ deviceProfile.name }}</h2>
        <DeviceProfileForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="更新裝置設定檔"
          :cancel-to="`/device-profiles/${deviceProfileId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
