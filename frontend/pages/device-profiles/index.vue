<script setup lang="ts">
import { computed } from 'vue'

import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
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
        <NuxtLink class="resource-shell__breadcrumb" to="/">首頁</NuxtLink>
        <h1 class="resource-shell__title">裝置設定檔</h1>
        <p class="resource-shell__description">
          這個頁面對齊 backend 的測試裝置設定檔 list / detail contract，先承接測試裝置資料的最小流程。
        </p>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="device-profile-create-link"
            to="/device-profiles/new"
          >
            建立裝置設定檔
          </NuxtLink>
        </div>
      </header>

      <CurrentActorSelector
        title="目前測試者"
        description="切換目前正在操作的測試者帳號，後續建立裝置設定檔時會帶入擁有者基線。"
      />

      <section
        v-if="pending"
        class="resource-state"
        data-testid="device-profiles-loading"
      >
        <h2 class="resource-state__title">載入裝置設定檔中</h2>
        <p class="resource-state__description">
          正在從 API 載入測試裝置設定檔清單。
        </p>
      </section>

      <section
        v-else-if="error"
        class="resource-state"
        data-testid="device-profiles-error"
      >
        <h2 class="resource-state__title">無法載入裝置設定檔</h2>
        <p class="resource-state__description">
          {{ error.message }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試
          </button>
        </div>
      </section>

      <section
        v-else-if="deviceProfiles.length === 0"
        class="resource-state"
        data-testid="device-profiles-empty"
      >
        <h2 class="resource-state__title">目前還沒有裝置設定檔</h2>
        <p class="resource-state__description">
          目前 API 沒有回傳任何測試裝置設定檔。建立資料後，這個頁面會直接承接清單結果。
        </p>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="device-profile-empty-create-link"
            to="/device-profiles/new"
          >
            建立第一筆裝置設定檔
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
          <span class="resource-shell__breadcrumb">裝置設定檔</span>
          <h2 class="resource-card__title">{{ deviceProfile.name }}</h2>
          <p class="resource-card__description">
            {{ deviceProfile.device_model }} · {{ deviceProfile.os_name }}
          </p>
          <div class="resource-card__meta">
            <span class="resource-card__chip">
              平台 {{ formatPlatformLabel(deviceProfile.platform) }}
            </span>
            <span
              v-if="deviceProfile.owner_account_id"
              class="resource-card__chip"
            >
              擁有者 {{ deviceProfile.owner_account_id }}
            </span>
            <span class="resource-card__chip">更新於 {{ deviceProfile.updated_at }}</span>
          </div>
        </NuxtLink>
      </section>
    </section>
  </main>
</template>
