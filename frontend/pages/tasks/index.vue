<script setup lang="ts">
import { computed } from 'vue'

import { fetchTasks } from '~/features/tasks/api'
import { formatTaskStatusLabel, isTaskStatus } from '~/features/tasks/types'

const route = useRoute()

const campaignIdFilter = computed(() =>
  typeof route.query.campaign_id === 'string' ? route.query.campaign_id : undefined
)
const deviceProfileIdFilter = computed(() =>
  typeof route.query.device_profile_id === 'string'
    ? route.query.device_profile_id
    : undefined
)
const statusFilter = computed(() => {
  const value = route.query.status
  return isTaskStatus(value) ? value : undefined
})

const {
  data: taskResponse,
  pending,
  error,
  refresh
} = useAsyncData(
  () =>
    `tasks-list-${campaignIdFilter.value ?? 'all'}-${deviceProfileIdFilter.value ?? 'all'}-${statusFilter.value ?? 'all'}`,
  () =>
    fetchTasks({
      campaignId: campaignIdFilter.value,
      deviceProfileId: deviceProfileIdFilter.value,
      status: statusFilter.value
    }),
  {
    server: false,
    watch: [campaignIdFilter, deviceProfileIdFilter, statusFilter],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const tasks = computed(() => taskResponse.value.items)
const activeFilters = computed(() => [
  campaignIdFilter.value
    ? `活動 ${campaignIdFilter.value}`
    : null,
  deviceProfileIdFilter.value
    ? `裝置設定檔 ${deviceProfileIdFilter.value}`
    : null,
  statusFilter.value ? `狀態 ${formatTaskStatusLabel(statusFilter.value)}` : null
].filter(Boolean) as string[])
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/">首頁</NuxtLink>
        <h1 class="resource-shell__title">任務列表</h1>
        <p class="resource-shell__description">
          這個頁面對齊後端的任務列表與詳情契約，先承接任務清單、指派錨點與最小狀態流的頁面骨架。
        </p>
        <div
          class="resource-state__actions"
        >
          <NuxtLink
            class="resource-action"
            data-testid="tasks-my-inbox-link"
            to="/my/tasks"
          >
            開啟我的測試者收件匣
          </NuxtLink>
          <NuxtLink
            v-if="campaignIdFilter"
            class="resource-action"
            data-testid="tasks-create-link"
            :to="`/campaigns/${campaignIdFilter}/tasks/new`"
          >
            為此活動建立任務
          </NuxtLink>
        </div>
        <div v-if="activeFilters.length > 0" class="resource-shell__meta">
          <span
            v-for="filterLabel in activeFilters"
            :key="filterLabel"
            class="resource-shell__meta-chip"
          >
            {{ filterLabel }}
          </span>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="tasks-loading"
      >
        <h2 class="resource-state__title">載入任務中</h2>
        <p class="resource-state__description">
          正在從 API 載入任務列表。
        </p>
      </section>

      <section
        v-else-if="error"
        class="resource-state"
        data-testid="tasks-error"
      >
        <h2 class="resource-state__title">無法載入任務</h2>
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
        v-else-if="tasks.length === 0"
        class="resource-state"
        data-testid="tasks-empty"
      >
        <h2 class="resource-state__title">目前還沒有任務</h2>
        <p class="resource-state__description">
          目前 API 沒有回傳任何任務。後續建立任務後，這個頁面會直接承接清單結果。
        </p>
        <div
          v-if="campaignIdFilter"
          class="resource-state__actions"
        >
          <NuxtLink
            class="resource-action"
            data-testid="tasks-empty-create-link"
            :to="`/campaigns/${campaignIdFilter}/tasks/new`"
          >
            建立第一筆任務
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-shell__grid"
        data-testid="tasks-list"
      >
        <NuxtLink
          v-for="task in tasks"
          :key="task.id"
          class="resource-card"
          :data-testid="`task-card-${task.id}`"
          :to="`/tasks/${task.id}`"
        >
          <span class="resource-shell__breadcrumb">任務</span>
          <h2 class="resource-card__title">{{ task.title }}</h2>
          <p class="resource-card__description">
            {{
              task.device_profile_id
                ? `已指派給 ${task.device_profile_id}`
                : '目前尚未指派裝置設定檔。'
            }}
          </p>
          <div class="resource-card__meta">
            <span class="resource-card__chip">活動 {{ task.campaign_id }}</span>
            <span class="resource-card__chip">狀態 {{ formatTaskStatusLabel(task.status) }}</span>
            <span class="resource-card__chip">更新於 {{ task.updated_at }}</span>
          </div>
        </NuxtLink>
      </section>
    </section>
  </main>
</template>
