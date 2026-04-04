<script setup lang="ts">
import { computed } from 'vue'

import { fetchCampaigns } from '~/features/campaigns/api'
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
  () => fetchCampaigns(projectId.value),
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
        <NuxtLink class="resource-shell__breadcrumb" to="/projects">Projects</NuxtLink>
        <h1 class="resource-shell__title">Project Detail Shell</h1>
        <p class="resource-shell__description">
          這個頁面會顯示單一 Project 與其對應的 Campaign 區塊，作為後續 Task / Feedback 流程的前置頁面骨架。
        </p>
      </header>

      <section
        v-if="projectPending"
        class="resource-state"
        data-testid="project-detail-loading"
      >
        <h2 class="resource-state__title">Loading project detail</h2>
        <p class="resource-state__description">
          正在從 API 載入 Project detail。
        </p>
      </section>

      <section
        v-else-if="projectError || !project"
        class="resource-state"
        data-testid="project-detail-error"
      >
        <h2 class="resource-state__title">Project detail unavailable</h2>
        <p class="resource-state__description">
          {{ projectError?.message || 'The requested project could not be loaded.' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshProject()">
            Retry
          </button>
          <NuxtLink class="resource-action" to="/projects">
            Back to projects
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
              Edit project
            </NuxtLink>
          </div>
          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Project ID</span>
              <span class="resource-key-value__value">{{ project.id }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Updated At</span>
              <span class="resource-key-value__value">{{ project.updated_at }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Created At</span>
              <span class="resource-key-value__value">{{ project.created_at }}</span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Description</span>
              <span class="resource-key-value__value">
                {{ project.description || 'No project description provided yet.' }}
              </span>
            </div>
          </div>
        </section>

        <section class="resource-section" data-testid="project-campaigns-section">
          <h2 class="resource-section__title">Related Campaigns</h2>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              data-testid="campaign-create-link"
              :to="`/projects/${project.id}/campaigns/new`"
            >
              Create campaign
            </NuxtLink>
          </div>

          <div
            v-if="campaignsPending"
            class="resource-state"
            data-testid="project-campaigns-loading"
          >
            <h3 class="resource-state__title">Loading related campaigns</h3>
            <p class="resource-state__description">
              正在載入屬於這個 Project 的 Campaign list。
            </p>
          </div>

          <div
            v-else-if="campaignsError"
            class="resource-state"
            data-testid="project-campaigns-error"
          >
            <h3 class="resource-state__title">Campaigns unavailable</h3>
            <p class="resource-state__description">
              {{ campaignsError.message }}
            </p>
            <div class="resource-state__actions">
              <button class="resource-action" type="button" @click="refreshCampaigns()">
                Retry
              </button>
            </div>
          </div>

          <div
            v-else-if="campaigns.length === 0"
            class="resource-state"
            data-testid="project-campaigns-empty"
          >
            <h3 class="resource-state__title">No campaigns for this project</h3>
            <p class="resource-state__description">
              目前這個 Project 尚未有 Campaign，可在 backend 建立後由此頁直接呈現。
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
              <span class="resource-shell__breadcrumb">Campaign</span>
              <h3 class="resource-card__title">{{ campaign.name }}</h3>
              <p class="resource-card__description">
                {{ campaign.version_label || 'No version label yet.' }}
              </p>
              <div class="resource-card__meta">
                <span class="resource-card__chip">Status {{ campaign.status }}</span>
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
