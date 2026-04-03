<script setup lang="ts">
import { computed } from 'vue'

import { fetchDeviceProfileDetail } from '~/features/device-profiles/api'

const route = useRoute()
const deviceProfileId = computed(() => String(route.params.deviceProfileId))

const {
  data: deviceProfile,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `device-profile-detail-${deviceProfileId.value}`,
  () => fetchDeviceProfileDetail(deviceProfileId.value),
  {
    server: false,
    watch: [deviceProfileId],
    default: () => null
  }
)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/device-profiles">
          Device Profiles
        </NuxtLink>
        <h1 class="resource-shell__title">Device Profile Detail Shell</h1>
        <p class="resource-shell__description">
          這個頁面先承接單一 Tester Device Profile 的核心欄位，提供後續 eligibility、task 與 feedback 流程可依附的裝置上下文。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="device-profile-detail-loading"
      >
        <h2 class="resource-state__title">Loading device profile detail</h2>
        <p class="resource-state__description">
          正在從 API 載入 Tester Device Profile detail。
        </p>
      </section>

      <section
        v-else-if="error || !deviceProfile"
        class="resource-state"
        data-testid="device-profile-detail-error"
      >
        <h2 class="resource-state__title">Device profile detail unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The requested device profile could not be loaded.' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            Retry
          </button>
          <NuxtLink class="resource-action" to="/device-profiles">
            Back to device profiles
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="device-profile-detail-panel"
      >
        <h2 class="resource-section__title">{{ deviceProfile.name }}</h2>

        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">Platform {{ deviceProfile.platform }}</span>
          <span class="resource-shell__meta-chip">{{ deviceProfile.device_model }}</span>
          <span class="resource-shell__meta-chip">{{ deviceProfile.os_name }}</span>
        </div>

        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Device Profile ID</span>
            <span class="resource-key-value__value">{{ deviceProfile.id }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Device Model</span>
            <span class="resource-key-value__value">{{ deviceProfile.device_model }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">OS Name</span>
            <span class="resource-key-value__value">{{ deviceProfile.os_name }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">OS Version</span>
            <span class="resource-key-value__value">
              {{ deviceProfile.os_version || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Browser Name</span>
            <span class="resource-key-value__value">
              {{ deviceProfile.browser_name || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Browser Version</span>
            <span class="resource-key-value__value">
              {{ deviceProfile.browser_version || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Locale</span>
            <span class="resource-key-value__value">
              {{ deviceProfile.locale || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Updated At</span>
            <span class="resource-key-value__value">{{ deviceProfile.updated_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Created At</span>
            <span class="resource-key-value__value">{{ deviceProfile.created_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Notes</span>
            <span class="resource-key-value__value">
              {{ deviceProfile.notes || 'No notes provided yet.' }}
            </span>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>
