<script setup lang="ts">
import { computed } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import { formatAccountRoleLabel } from '~/features/accounts/types'

const {
  data: accountResponse,
  pending,
  error,
  refresh
} = useAsyncData('accounts-list', () => fetchAccounts(), {
  server: false,
  default: () => ({
    items: [],
    total: 0
  })
})

const accounts = computed(() => accountResponse.value.items)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/">首頁</NuxtLink>
        <h1 class="resource-shell__title">帳號列表</h1>
        <p class="resource-shell__description">
          這個頁面提供開發者與測試者的最小帳號資料，作為後續擁有權與依角色流程的基礎。
        </p>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="account-create-link"
            to="/accounts/new"
          >
            建立帳號
          </NuxtLink>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="accounts-loading"
      >
        <h2 class="resource-state__title">正在載入帳號</h2>
        <p class="resource-state__description">
          正在從 API 載入帳號列表。
        </p>
      </section>

      <section
        v-else-if="error"
        class="resource-state"
        data-testid="accounts-error"
      >
        <h2 class="resource-state__title">帳號列表暫時無法使用</h2>
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
        v-else-if="accounts.length === 0"
        class="resource-state"
        data-testid="accounts-empty"
      >
        <h2 class="resource-state__title">尚無帳號</h2>
        <p class="resource-state__description">
          目前 API 沒有回傳任何帳號。可以先建立最小的開發者 / 測試者基線，支撐下一階段的協作流程。
        </p>
        <div class="resource-state__actions">
          <NuxtLink
            class="resource-action"
            data-testid="account-empty-create-link"
            to="/accounts/new"
          >
            建立帳號
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-shell__grid"
        data-testid="accounts-list"
      >
        <NuxtLink
          v-for="account in accounts"
          :key="account.id"
          class="resource-card"
          :data-testid="`account-card-${account.id}`"
          :to="`/accounts/${account.id}`"
        >
          <span class="resource-shell__breadcrumb">帳號</span>
          <h2 class="resource-card__title">{{ account.display_name }}</h2>
          <p class="resource-card__description">
            {{ formatAccountRoleLabel(account.role) }}
          </p>
          <div class="resource-card__meta">
            <span class="resource-card__chip">更新時間 {{ account.updated_at }}</span>
          </div>
        </NuxtLink>
      </section>
    </section>
  </main>
</template>
