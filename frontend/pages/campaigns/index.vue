<script setup lang="ts">
import { computed } from 'vue'

import { fetchCampaigns } from '~/features/campaigns/api'
import { formatCampaignStatusLabel } from '~/features/campaigns/types'
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
      <header class="resource-shell__header app-page-header">
        <NuxtLink class="resource-shell__breadcrumb" to="/dashboard">Dashboard</NuxtLink>
        <h1 class="resource-shell__title">活動列表</h1>
        <p class="resource-shell__description">
          這個頁面對齊後端的活動列表與詳情契約，先承接 MVP 階段的活動列表、狀態與平台欄位。
        </p>
        <div class="app-page-summary-grid">
          <article class="app-page-summary-card">
            <span class="app-page-summary-card__label">活動數</span>
            <strong class="app-page-summary-card__value">{{ campaigns.length }}</strong>
            <span class="app-page-summary-card__description">活動列表現在會沿用與 workspace 頁一致的卡片節奏與 header hierarchy。</span>
          </article>
          <article class="app-page-summary-card">
            <span class="app-page-summary-card__label">頁面角色</span>
            <strong class="app-page-summary-card__value">Campaign catalog</strong>
            <span class="app-page-summary-card__description">保留 public discovery 的資料邏輯，但套進新的 app list template。</span>
          </article>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="campaigns-loading"
      >
        <h2 class="resource-state__title">載入活動中</h2>
        <p class="resource-state__description">
          正在從 API 載入活動列表。
        </p>
      </section>

      <section
        v-else-if="error"
        class="resource-state"
        data-testid="campaigns-error"
      >
        <h2 class="resource-state__title">無法載入活動</h2>
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
        v-else-if="campaigns.length === 0"
        class="resource-state"
        data-testid="campaigns-empty"
      >
        <h2 class="resource-state__title">目前還沒有活動</h2>
        <p class="resource-state__description">
          目前 API 沒有回傳任何活動。後續建立測試批次後，這個頁面會直接承接資料。
        </p>
      </section>

      <section
        v-else
        class="resource-shell__grid app-page-card-grid"
        data-testid="campaigns-list"
      >
        <NuxtLink
          v-for="campaign in campaigns"
          :key="campaign.id"
          class="resource-card"
          :data-testid="`campaign-card-${campaign.id}`"
          :to="`/campaigns/${campaign.id}`"
        >
          <span class="resource-shell__breadcrumb">活動</span>
          <h2 class="resource-card__title">{{ campaign.name }}</h2>
          <p class="resource-card__description">
            {{
              campaign.version_label
                ? `版本 ${campaign.version_label}`
                : '目前尚未提供版本標記。'
            }}
          </p>
          <div class="resource-card__meta">
            <span class="resource-card__chip">狀態 {{ formatCampaignStatusLabel(campaign.status) }}</span>
            <span class="resource-card__chip">專案 {{ campaign.project_id }}</span>
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
