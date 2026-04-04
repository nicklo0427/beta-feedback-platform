<script setup lang="ts">
import { computed } from 'vue'

import { fetchProjects } from '~/features/projects/api'

const {
  data: projectResponse,
  pending,
  error,
  refresh
} = useAsyncData('projects-list', () => fetchProjects(), {
  server: false,
  default: () => ({
    items: [],
    total: 0
  })
})

const projects = computed(() => projectResponse.value.items)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/">Home</NuxtLink>
        <h1 class="resource-shell__title">Projects Shell</h1>
        <p class="resource-shell__description">
          這個頁面對齊 backend 的 Project list / detail contract，先提供最小可承接資料流的頁面骨架。
        </p>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="project-create-link"
            to="/projects/new"
          >
            Create project
          </NuxtLink>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="projects-loading"
      >
        <h2 class="resource-state__title">Loading projects</h2>
        <p class="resource-state__description">
          正在從 API 載入 Project list。
        </p>
      </section>

      <section
        v-else-if="error"
        class="resource-state"
        data-testid="projects-error"
      >
        <h2 class="resource-state__title">Projects unavailable</h2>
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
        v-else-if="projects.length === 0"
        class="resource-state"
        data-testid="projects-empty"
      >
        <h2 class="resource-state__title">No projects yet</h2>
        <p class="resource-state__description">
          目前 API 沒有回傳任何 Project。後續可在 backend 建立資料後，直接用這個頁面承接。
        </p>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="project-empty-create-link"
            to="/projects/new"
          >
            Create project
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-shell__grid"
        data-testid="projects-list"
      >
        <NuxtLink
          v-for="project in projects"
          :key="project.id"
          class="resource-card"
          :data-testid="`project-card-${project.id}`"
          :to="`/projects/${project.id}`"
        >
          <span class="resource-shell__breadcrumb">Project</span>
          <h2 class="resource-card__title">{{ project.name }}</h2>
          <p class="resource-card__description">
            {{ project.description || 'No project description provided yet.' }}
          </p>
          <div class="resource-card__meta">
            <span class="resource-card__chip">Updated {{ project.updated_at }}</span>
          </div>
        </NuxtLink>
      </section>
    </section>
  </main>
</template>
