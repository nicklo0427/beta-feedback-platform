<script setup lang="ts">
import { computed } from 'vue'

import { fetchCampaigns } from '~/features/campaigns/api'
import { formatPlatformLabel } from '~/features/platform-display'

const {
  data: campaignResponse,
  pending,
  error,
  refresh
} = useAsyncData('campaigns-list', () => fetchCampaigns(), {
  server: false,
  default: () => ({
    items: [],
    total: 0
  })
})

const campaigns = computed(() => campaignResponse.value.items)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/">Home</NuxtLink>
        <h1 class="resource-shell__title">Campaigns Shell</h1>
        <p class="resource-shell__description">
          這個頁面對齊 backend 的 Campaign list / detail contract，先承接 MVP 階段的活動列表、狀態與平台欄位。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="campaigns-loading"
      >
        <h2 class="resource-state__title">Loading campaigns</h2>
        <p class="resource-state__description">
          正在從 API 載入 Campaign list。
        </p>
      </section>

      <section
        v-else-if="error"
        class="resource-state"
        data-testid="campaigns-error"
      >
        <h2 class="resource-state__title">Campaigns unavailable</h2>
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
        v-else-if="campaigns.length === 0"
        class="resource-state"
        data-testid="campaigns-empty"
      >
        <h2 class="resource-state__title">No campaigns yet</h2>
        <p class="resource-state__description">
          目前 API 沒有回傳任何 Campaign。後續建立測試批次後，這個頁面會直接承接資料。
        </p>
      </section>

      <section
        v-else
        class="resource-shell__grid"
        data-testid="campaigns-list"
      >
        <NuxtLink
          v-for="campaign in campaigns"
          :key="campaign.id"
          class="resource-card"
          :data-testid="`campaign-card-${campaign.id}`"
          :to="`/campaigns/${campaign.id}`"
        >
          <span class="resource-shell__breadcrumb">Campaign</span>
          <h2 class="resource-card__title">{{ campaign.name }}</h2>
          <p class="resource-card__description">
            {{
              campaign.version_label
                ? `Version ${campaign.version_label}`
                : 'No version label yet.'
            }}
          </p>
          <div class="resource-card__meta">
            <span class="resource-card__chip">Status {{ campaign.status }}</span>
            <span class="resource-card__chip">Project {{ campaign.project_id }}</span>
          </div>
          <div class="resource-card__meta">
            <span
              v-for="platform in campaign.target_platforms"
              :key="platform"
              class="resource-card__chip"
            >
              {{ formatPlatformLabel(platform) }}
            </span>
          </div>
        </NuxtLink>
      </section>
    </section>
  </main>
</template>
