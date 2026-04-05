<script setup lang="ts">
import { computed } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import { fetchProjects } from '~/features/projects/api'

useCurrentActorPersistence()

const currentActorId = useCurrentActorId()

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('my-projects-accounts', () => fetchAccounts(), {
  server: false,
  default: () => ({
    items: [],
    total: 0
  })
})

const accounts = computed(() => accountResponse.value.items)
const currentActor = computed(
  () => accounts.value.find((account) => account.id === currentActorId.value) ?? null
)
const isDeveloperActor = computed(() => currentActor.value?.role === 'developer')

const {
  data: projectResponse,
  pending: projectsPending,
  error: projectsError,
  refresh: refreshProjects
} = useAsyncData(
  () => `my-projects-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
  async () => {
    if (!currentActorId.value || !isDeveloperActor.value) {
      return {
        items: [],
        total: 0
      }
    }

    return fetchProjects({
      mine: true,
      actorId: currentActorId.value
    })
  },
  {
    server: false,
    watch: [currentActorId, currentActor],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const projects = computed(() => projectResponse.value.items)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/">首頁</NuxtLink>
        <h1 class="resource-shell__title">我的專案</h1>
        <p class="resource-shell__description">
          這個頁面提供開發者端最小的 owned workspace，讓你集中查看由目前操作帳號擁有的專案，並快速進入主流程的上游入口。
        </p>
        <div class="resource-state__actions">
          <NuxtLink class="resource-action" to="/projects">
            查看所有專案
          </NuxtLink>
          <NuxtLink class="resource-action" to="/my/campaigns">
            查看我的活動
          </NuxtLink>
          <NuxtLink class="resource-action" to="/projects/new">
            建立專案
          </NuxtLink>
        </div>
      </header>

      <CurrentActorSelector
        title="開發者專案工作區"
        description="選擇目前正在操作的開發者帳號，系統會依據擁有者資訊推導這位開發者的專案工作區。"
      />

      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="my-projects-actor-error"
      >
        <h2 class="resource-state__title">無法取得操作情境</h2>
        <p class="resource-state__description">
          {{ accountsError.message }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshAccounts()">
            重試
          </button>
        </div>
      </section>

      <section
        v-else-if="accountsPending"
        class="resource-state"
        data-testid="my-projects-actor-loading"
      >
        <h2 class="resource-state__title">載入開發者情境中</h2>
        <p class="resource-state__description">
          正在確認目前操作帳號與可用的開發者專案工作區。
        </p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="my-projects-select-actor"
      >
        <h2 class="resource-state__title">請選擇開發者帳號</h2>
        <p class="resource-state__description">
          先選擇目前操作帳號，系統才知道要推導哪一位開發者的專案工作區。
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="my-projects-actor-missing"
      >
        <h2 class="resource-state__title">找不到已選擇的帳號</h2>
        <p class="resource-state__description">
          目前找不到你選擇的帳號，請重新選擇一筆可用的開發者帳號。
        </p>
      </section>

      <section
        v-else-if="!isDeveloperActor"
        class="resource-state"
        data-testid="my-projects-role-mismatch"
      >
        <h2 class="resource-state__title">開發者工作區需要開發者帳號</h2>
        <p class="resource-state__description">
          目前選到的是{{ formatAccountRoleLabel(currentActor.role) }}帳號。請切換到開發者帳號，再查看我的專案。
        </p>
      </section>

      <template v-else>
        <section class="resource-section" data-testid="my-projects-summary">
          <h2 class="resource-section__title">我的專案總覽</h2>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              目前帳號 {{ currentActor.display_name }}
            </span>
            <span class="resource-shell__meta-chip">
              我的專案 {{ projectResponse.total }}
            </span>
          </div>
        </section>

        <section
          v-if="projectsPending"
          class="resource-state"
          data-testid="my-projects-loading"
        >
          <h2 class="resource-state__title">載入我的專案中</h2>
          <p class="resource-state__description">
            正在根據目前操作帳號與擁有者資訊推導開發者專案工作區。
          </p>
        </section>

        <section
          v-else-if="projectsError"
          class="resource-state"
          data-testid="my-projects-error"
        >
          <h2 class="resource-state__title">無法載入我的專案</h2>
          <p class="resource-state__description">
            {{ projectsError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshProjects()">
              重試
            </button>
          </div>
        </section>

        <section
          v-else-if="projects.length === 0"
          class="resource-state"
          data-testid="my-projects-empty"
        >
          <h2 class="resource-state__title">目前還沒有我的專案</h2>
          <p class="resource-state__description">
            目前這位開發者還沒有任何專案。你可以先建立一個專案，再從專案詳情延伸到活動與後續主流程。
          </p>
          <div class="resource-state__actions">
            <NuxtLink class="resource-action" to="/projects/new">
              建立專案
            </NuxtLink>
          </div>
        </section>

        <section
          v-else
          class="resource-section__body"
          data-testid="my-projects-list"
        >
          <article
            v-for="project in projects"
            :key="project.id"
            class="resource-card"
            :data-testid="`my-project-card-${project.id}`"
          >
            <span class="resource-shell__breadcrumb">我的專案</span>
            <h2 class="resource-card__title">{{ project.name }}</h2>
            <p class="resource-card__description">
              {{ project.description || '尚未提供專案說明。' }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">擁有者 {{ project.owner_account_id || '未設定' }}</span>
              <span class="resource-card__chip">更新時間 {{ project.updated_at }}</span>
            </div>
            <div class="resource-state__actions">
              <NuxtLink
                class="resource-action"
                :data-testid="`my-project-detail-link-${project.id}`"
                :to="`/projects/${project.id}`"
              >
                開啟專案詳情
              </NuxtLink>
              <NuxtLink
                class="resource-action"
                :data-testid="`my-project-create-campaign-link-${project.id}`"
                :to="`/projects/${project.id}/campaigns/new`"
              >
                在此專案建立活動
              </NuxtLink>
            </div>
          </article>
        </section>
      </template>
    </section>
  </main>
</template>
