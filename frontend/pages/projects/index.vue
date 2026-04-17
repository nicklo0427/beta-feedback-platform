<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import {
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { fetchProjects } from '~/features/projects/api'

useCurrentActorPersistence()

const currentActorId = useCurrentActorId()
const mineOnly = ref(false)
const {
  data: projectResponse,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `projects-list-${mineOnly.value ? 'mine' : 'all'}-${currentActorId.value ?? 'none'}`,
  () =>
    fetchProjects({
      mine: mineOnly.value,
      actorId: currentActorId.value
    }),
  {
    server: false,
    watch: [mineOnly, currentActorId],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const projects = computed(() => projectResponse.value.items)
const scopeLabel = computed(() => {
  if (mineOnly.value) {
    return '目前顯示我的專案'
  }

  return '目前顯示全部專案'
})

watch(currentActorId, (nextActorId) => {
  if (!nextActorId) {
    mineOnly.value = false
  }
})
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header app-page-header">
        <NuxtLink class="resource-shell__breadcrumb" to="/dashboard">Dashboard</NuxtLink>
        <h1 class="resource-shell__title">專案列表</h1>
        <p class="resource-shell__description">
          在新的產品化 shell 裡，這裡會承接專案清單、mine filter 與後續活動建立流程。
        </p>
        <div class="resource-state__actions app-page-actions">
          <NuxtLink
            class="resource-action"
            data-testid="project-create-link"
            to="/projects/new"
          >
            建立專案
          </NuxtLink>
          <button
            class="resource-action"
            data-testid="projects-mine-toggle"
            type="button"
            :disabled="!currentActorId"
            @click="mineOnly = !mineOnly"
          >
            {{ mineOnly ? '顯示全部專案' : '只顯示我的專案' }}
          </button>
        </div>
        <div class="app-page-summary-grid">
          <article class="app-page-summary-card">
            <span class="app-page-summary-card__label">顯示範圍</span>
            <strong class="app-page-summary-card__value">{{ scopeLabel }}</strong>
            <span class="app-page-summary-card__description">切換 mine filter 後，列表仍保留同一套 list page 節奏。</span>
          </article>
          <article class="app-page-summary-card">
            <span class="app-page-summary-card__label">專案數</span>
            <strong class="app-page-summary-card__value">{{ projects.length }}</strong>
            <span class="app-page-summary-card__description">由這裡直接往詳情與建立活動流程延伸。</span>
          </article>
          <article
            v-if="mineOnly && currentActorId"
            class="app-page-summary-card"
          >
            <span class="app-page-summary-card__label">目前 actor</span>
            <strong class="app-page-summary-card__value">{{ currentActorId }}</strong>
            <span class="app-page-summary-card__description">mine view 會沿用目前登入或 fallback actor 的 ownership context。</span>
          </article>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="projects-loading"
      >
        <h2 class="resource-state__title">正在載入專案</h2>
        <p class="resource-state__description">
          正在從 API 載入專案列表。
        </p>
      </section>

      <section
        v-else-if="error"
        class="resource-state"
        data-testid="projects-error"
      >
        <h2 class="resource-state__title">專案列表暫時無法使用</h2>
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
        v-else-if="projects.length === 0"
        class="resource-state"
        data-testid="projects-empty"
      >
        <h2 class="resource-state__title">尚無專案</h2>
        <p class="resource-state__description">
          目前 API 沒有回傳任何專案。後續可在後端建立資料後，直接用這個頁面承接。
        </p>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="project-empty-create-link"
            to="/projects/new"
          >
            建立專案
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-shell__grid app-page-card-grid"
        data-testid="projects-list"
      >
        <NuxtLink
          v-for="project in projects"
          :key="project.id"
          class="resource-card"
          :data-testid="`project-card-${project.id}`"
          :to="`/projects/${project.id}`"
        >
          <span class="resource-shell__breadcrumb">專案</span>
          <h2 class="resource-card__title">{{ project.name }}</h2>
          <p class="resource-card__description">
            {{ project.description || '尚未提供專案說明。' }}
          </p>
          <div class="resource-card__meta">
            <span
              v-if="project.owner_account_id"
              class="resource-card__chip"
            >
              擁有者 {{ project.owner_account_id }}
            </span>
            <span class="resource-card__chip">更新時間 {{ project.updated_at }}</span>
          </div>
        </NuxtLink>
      </section>
    </section>
  </main>
</template>
