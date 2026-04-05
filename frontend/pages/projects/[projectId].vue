<script setup lang="ts">
import { computed } from 'vue'

import { fetchCampaigns } from '~/features/campaigns/api'
import { formatCampaignStatusLabel } from '~/features/campaigns/types'
import { formatPlatformLabel } from '~/features/platform-display'
import { fetchProjectDetail } from '~/features/projects/api'

const route = useRoute()
const projectId = computed(() => String(route.params.projectId))

const {
  data: project,
  pending: projectPending,
  error: projectError,
  refresh: refreshProject
} = useAsyncData(
  () => `project-detail-${projectId.value}`,
  () => fetchProjectDetail(projectId.value),
  {
    server: false,
    watch: [projectId],
    default: () => null
  }
)

const {
  data: campaignResponse,
  pending: campaignsPending,
  error: campaignsError,
  refresh: refreshCampaigns
} = useAsyncData(
  () => `project-campaigns-${projectId.value}`,
  () =>
    fetchCampaigns({
      projectId: projectId.value
    }),
  {
    server: false,
    watch: [projectId],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const campaigns = computed(() => campaignResponse.value.items)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/projects">專案列表</NuxtLink>
        <h1 class="resource-shell__title">專案詳情</h1>
        <p class="resource-shell__description">
          這個頁面會顯示單一專案與其對應的活動區塊，作為後續任務與回饋流程的前置頁面骨架。
        </p>
      </header>

      <section
        v-if="projectPending"
        class="resource-state"
        data-testid="project-detail-loading"
      >
        <h2 class="resource-state__title">正在載入專案詳情</h2>
        <p class="resource-state__description">
          正在從 API 載入專案詳情。
        </p>
      </section>

      <section
        v-else-if="projectError || !project"
        class="resource-state"
        data-testid="project-detail-error"
      >
        <h2 class="resource-state__title">專案詳情暫時無法使用</h2>
        <p class="resource-state__description">
          {{ projectError?.message || '無法載入指定的專案。' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshProject()">
            重試
          </button>
          <NuxtLink class="resource-action" to="/projects">
            返回專案列表
          </NuxtLink>
        </div>
      </section>

      <template v-else>
        <section class="resource-section" data-testid="project-detail-panel">
          <h2 class="resource-section__title">{{ project.name }}</h2>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              data-testid="project-edit-link"
              :to="`/projects/${project.id}/edit`"
            >
            編輯專案
            </NuxtLink>
          </div>
          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">專案 ID</span>
              <span class="resource-key-value__value">{{ project.id }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">更新時間</span>
              <span class="resource-key-value__value">{{ project.updated_at }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">擁有者帳號</span>
              <span class="resource-key-value__value">
                {{ project.owner_account_id || '尚未建立擁有者資訊。' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">建立時間</span>
              <span class="resource-key-value__value">{{ project.created_at }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">說明</span>
              <span class="resource-key-value__value">
                {{ project.description || '尚未提供專案說明。' }}
              </span>
            </div>
          </div>
        </section>

        <section class="resource-section" data-testid="project-campaigns-section">
          <h2 class="resource-section__title">相關活動</h2>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              data-testid="campaign-create-link"
              :to="`/projects/${project.id}/campaigns/new`"
            >
              建立活動
            </NuxtLink>
          </div>

          <div
            v-if="campaignsPending"
            class="resource-state"
            data-testid="project-campaigns-loading"
          >
          <h3 class="resource-state__title">正在載入相關活動</h3>
          <p class="resource-state__description">
              正在載入屬於這個專案的活動列表。
          </p>
          </div>

          <div
            v-else-if="campaignsError"
            class="resource-state"
            data-testid="project-campaigns-error"
          >
            <h3 class="resource-state__title">活動列表暫時無法使用</h3>
            <p class="resource-state__description">
              {{ campaignsError.message }}
            </p>
            <div class="resource-state__actions">
              <button class="resource-action" type="button" @click="refreshCampaigns()">
                重試
              </button>
            </div>
          </div>

          <div
            v-else-if="campaigns.length === 0"
            class="resource-state"
            data-testid="project-campaigns-empty"
          >
          <h3 class="resource-state__title">這個專案尚無活動</h3>
          <p class="resource-state__description">
              目前這個專案尚未有活動，可在後端建立後由此頁直接呈現。
          </p>
          </div>

          <div
            v-else
            class="resource-section__body"
            data-testid="project-campaigns-list"
          >
            <NuxtLink
              v-for="campaign in campaigns"
              :key="campaign.id"
              class="resource-card"
              :data-testid="`project-campaign-card-${campaign.id}`"
              :to="`/campaigns/${campaign.id}`"
            >
              <span class="resource-shell__breadcrumb">活動</span>
              <h3 class="resource-card__title">{{ campaign.name }}</h3>
              <p class="resource-card__description">
                {{ campaign.version_label || '尚未提供版本標籤。' }}
              </p>
              <div class="resource-card__meta">
                <span class="resource-card__chip">狀態 {{ formatCampaignStatusLabel(campaign.status) }}</span>
                <span
                  v-for="platform in campaign.target_platforms"
                  :key="platform"
                  class="resource-card__chip"
                >
                  {{ formatPlatformLabel(platform) }}
                </span>
              </div>
            </NuxtLink>
          </div>
        </section>
      </template>
    </section>
  </main>
</template>
