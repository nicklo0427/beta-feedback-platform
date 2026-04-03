<script setup lang="ts">
import { computed } from 'vue'

import { fetchDeviceProfiles } from '~/features/device-profiles/api'
import { formatPlatformLabel } from '~/features/platform-display'

const {
  data: deviceProfileResponse,
  pending,
  error,
  refresh
} = useAsyncData('device-profiles-list', () => fetchDeviceProfiles(), {
  server: false,
  default: () => ({
    items: [],
    total: 0
  })
})

const deviceProfiles = computed(() => deviceProfileResponse.value.items)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/">Home</NuxtLink>
        <h1 class="resource-shell__title">Device Profiles Shell</h1>
        <p class="resource-shell__description">
          這個頁面對齊 backend 的 Tester Device Profile list / detail contract，先承接測試裝置資料的最小殼層流程。
        </p>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="device-profile-create-link"
            to="/device-profiles/new"
          >
            Create device profile
          </NuxtLink>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="device-profiles-loading"
      >
        <h2 class="resource-state__title">Loading device profiles</h2>
        <p class="resource-state__description">
          正在從 API 載入 Tester Device Profile list。
        </p>
      </section>

      <section
        v-else-if="error"
        class="resource-state"
        data-testid="device-profiles-error"
      >
        <h2 class="resource-state__title">Device profiles unavailable</h2>
        <p class="resource-state__description">
          {{ error.message }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            Retry
          </button>
        </div>
      </section>

      <section
        v-else-if="deviceProfiles.length === 0"
        class="resource-state"
        data-testid="device-profiles-empty"
      >
        <h2 class="resource-state__title">No device profiles yet</h2>
        <p class="resource-state__description">
          目前 API 沒有回傳任何 Tester Device Profile。後續建立資料後，這個頁面會直接承接清單結果。
        </p>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="device-profile-empty-create-link"
            to="/device-profiles/new"
          >
            Create the first device profile
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-shell__grid"
        data-testid="device-profiles-list"
      >
        <NuxtLink
          v-for="deviceProfile in deviceProfiles"
          :key="deviceProfile.id"
          class="resource-card"
          :data-testid="`device-profile-card-${deviceProfile.id}`"
          :to="`/device-profiles/${deviceProfile.id}`"
        >
          <span class="resource-shell__breadcrumb">Device Profile</span>
          <h2 class="resource-card__title">{{ deviceProfile.name }}</h2>
          <p class="resource-card__description">
            {{ deviceProfile.device_model }} · {{ deviceProfile.os_name }}
          </p>
          <div class="resource-card__meta">
            <span class="resource-card__chip">
              Platform {{ formatPlatformLabel(deviceProfile.platform) }}
            </span>
            <span class="resource-card__chip">Updated {{ deviceProfile.updated_at }}</span>
          </div>
        </NuxtLink>
      </section>
    </section>
  </main>
</template>
