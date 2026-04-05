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
          活動詳情
        </NuxtLink>
        <h1 class="resource-shell__title">資格條件規則詳情</h1>
        <p class="resource-shell__description">
          這個頁面先承接單一資格條件規則的核心欄位，提供後續條件管理與任務判斷流程可依附的最小詳情頁骨架。
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
            編輯資格條件規則
          </NuxtLink>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="eligibility-rule-detail-loading"
      >
        <h2 class="resource-state__title">載入資格條件規則詳情中</h2>
        <p class="resource-state__description">
          正在從 API 載入資格條件規則詳情。
        </p>
      </section>

      <section
        v-else-if="error || !eligibilityRule"
        class="resource-state"
        data-testid="eligibility-rule-detail-error"
      >
        <h2 class="resource-state__title">無法載入資格條件規則詳情</h2>
        <p class="resource-state__description">
          {{ error?.message || '找不到指定的資格條件規則。' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試
          </button>
          <NuxtLink class="resource-action" :to="`/campaigns/${campaignId}`">
            返回活動
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
            啟用中 {{ eligibilityRule.is_active ? '是' : '否' }}
          </span>
          <span class="resource-shell__meta-chip">
            活動 {{ eligibilityRule.campaign_id }}
          </span>
        </div>

        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">資格條件規則 ID</span>
            <span class="resource-key-value__value">{{ eligibilityRule.id }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">作業系統名稱</span>
            <span class="resource-key-value__value">
              {{ eligibilityRule.os_name || '目前尚未限制作業系統。' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">最低作業系統版本</span>
            <span class="resource-key-value__value">
              {{ eligibilityRule.os_version_min || '尚未提供。' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">最高作業系統版本</span>
            <span class="resource-key-value__value">
              {{ eligibilityRule.os_version_max || '尚未提供。' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">安裝渠道</span>
            <span class="resource-key-value__value">
              {{ eligibilityRule.install_channel || '目前尚未限制安裝渠道。' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">更新時間</span>
            <span class="resource-key-value__value">{{ eligibilityRule.updated_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">建立時間</span>
            <span class="resource-key-value__value">{{ eligibilityRule.created_at }}</span>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>
