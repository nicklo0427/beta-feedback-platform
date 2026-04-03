<script setup lang="ts">
import { computed } from 'vue'

import { fetchEligibilityRuleDetail } from '~/features/eligibility/api'
import { formatPlatformLabel } from '~/features/platform-display'

const route = useRoute()
const campaignId = computed(() => String(route.params.campaignId))
const eligibilityRuleId = computed(() => String(route.params.eligibilityRuleId))

const {
  data: eligibilityRule,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `eligibility-rule-detail-${eligibilityRuleId.value}`,
  () => fetchEligibilityRuleDetail(eligibilityRuleId.value),
  {
    server: false,
    watch: [eligibilityRuleId],
    default: () => null
  }
)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" :to="`/campaigns/${campaignId}`">
          Campaign Detail
        </NuxtLink>
        <h1 class="resource-shell__title">Eligibility Rule Detail Shell</h1>
        <p class="resource-shell__description">
          這個頁面先承接單一 eligibility rule 的核心欄位，提供後續條件管理與 task 判斷流程可依附的最小 detail shell。
        </p>
        <div
          v-if="eligibilityRule"
          class="resource-state__actions"
        >
          <NuxtLink
            class="resource-action"
            data-testid="eligibility-rule-edit-link"
            :to="`/campaigns/${campaignId}/eligibility-rules/${eligibilityRule.id}/edit`"
          >
            Edit eligibility rule
          </NuxtLink>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="eligibility-rule-detail-loading"
      >
        <h2 class="resource-state__title">Loading eligibility rule detail</h2>
        <p class="resource-state__description">
          正在從 API 載入 eligibility rule detail。
        </p>
      </section>

      <section
        v-else-if="error || !eligibilityRule"
        class="resource-state"
        data-testid="eligibility-rule-detail-error"
      >
        <h2 class="resource-state__title">Eligibility rule detail unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The requested eligibility rule could not be loaded.' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            Retry
          </button>
          <NuxtLink class="resource-action" :to="`/campaigns/${campaignId}`">
            Back to campaign
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="eligibility-rule-detail-panel"
      >
        <h2 class="resource-section__title">
          {{ formatPlatformLabel(eligibilityRule.platform) }}
        </h2>

        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            Active {{ eligibilityRule.is_active ? 'yes' : 'no' }}
          </span>
          <span class="resource-shell__meta-chip">
            Campaign {{ eligibilityRule.campaign_id }}
          </span>
        </div>

        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Eligibility Rule ID</span>
            <span class="resource-key-value__value">{{ eligibilityRule.id }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">OS Name</span>
            <span class="resource-key-value__value">
              {{ eligibilityRule.os_name || 'No OS restriction yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">OS Version Min</span>
            <span class="resource-key-value__value">
              {{ eligibilityRule.os_version_min || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">OS Version Max</span>
            <span class="resource-key-value__value">
              {{ eligibilityRule.os_version_max || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Install Channel</span>
            <span class="resource-key-value__value">
              {{ eligibilityRule.install_channel || 'No install channel restriction.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Updated At</span>
            <span class="resource-key-value__value">{{ eligibilityRule.updated_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Created At</span>
            <span class="resource-key-value__value">{{ eligibilityRule.created_at }}</span>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>
