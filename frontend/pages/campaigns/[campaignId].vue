<script setup lang="ts">
import { computed } from 'vue'

import { fetchCampaignDetail } from '~/features/campaigns/api'

const route = useRoute()
const campaignId = computed(() => String(route.params.campaignId))

const {
  data: campaign,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `campaign-detail-${campaignId.value}`,
  () => fetchCampaignDetail(campaignId.value),
  {
    server: false,
    watch: [campaignId],
    default: () => null
  }
)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/campaigns">Campaigns</NuxtLink>
        <h1 class="resource-shell__title">Campaign Detail Shell</h1>
        <p class="resource-shell__description">
          這個頁面先承接單一 Campaign 的核心欄位，包含所屬 Project、版本、平台與活動狀態。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="campaign-detail-loading"
      >
        <h2 class="resource-state__title">Loading campaign detail</h2>
        <p class="resource-state__description">
          正在從 API 載入 Campaign detail。
        </p>
      </section>

      <section
        v-else-if="error || !campaign"
        class="resource-state"
        data-testid="campaign-detail-error"
      >
        <h2 class="resource-state__title">Campaign detail unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The requested campaign could not be loaded.' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            Retry
          </button>
          <NuxtLink class="resource-action" to="/campaigns">
            Back to campaigns
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="campaign-detail-panel"
      >
        <h2 class="resource-section__title">{{ campaign.name }}</h2>

        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">Status {{ campaign.status }}</span>
          <span
            v-for="platform in campaign.target_platforms"
            :key="platform"
            class="resource-shell__meta-chip"
          >
            {{ platform }}
          </span>
        </div>

        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Campaign ID</span>
            <span class="resource-key-value__value">{{ campaign.id }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Project ID</span>
            <NuxtLink
              class="resource-key-value__value"
              :to="`/projects/${campaign.project_id}`"
            >
              {{ campaign.project_id }}
            </NuxtLink>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Version Label</span>
            <span class="resource-key-value__value">
              {{ campaign.version_label || 'No version label yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Updated At</span>
            <span class="resource-key-value__value">{{ campaign.updated_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Created At</span>
            <span class="resource-key-value__value">{{ campaign.created_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Description</span>
            <span class="resource-key-value__value">
              {{ campaign.description || 'No campaign description provided yet.' }}
            </span>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>
