<script setup lang="ts">
import { computed, watch } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import {
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'

const props = withDefaults(
  defineProps<{
    title?: string
    description?: string
  }>(),
  {
    title: '目前操作帳號',
    description:
      '切換目前正在操作的帳號，讓新建立的專案或裝置設定檔可以自動帶入擁有者資訊。'
  }
)

useCurrentActorPersistence()

const currentActorId = useCurrentActorId()
const {
  data: accountResponse,
  pending,
  error,
  refresh
} = useAsyncData('current-actor-accounts', () => fetchAccounts(), {
  server: false,
  default: () => ({
    items: [],
    total: 0
  })
})

const accounts = computed(() => accountResponse.value.items)
const selectedActorId = computed({
  get: () => currentActorId.value ?? '',
  set: (value: string) => {
    currentActorId.value = value || null
  }
})
const selectedAccount = computed(
  () => accounts.value.find((account) => account.id === currentActorId.value) ?? null
)

watch(
  accounts,
  (nextAccounts) => {
    if (!currentActorId.value) {
      return
    }

    const actorStillExists = nextAccounts.some(
      (account) => account.id === currentActorId.value
    )

    if (!actorStillExists) {
      currentActorId.value = null
    }
  },
  {
    immediate: true
  }
)
</script>

<template>
  <section class="resource-section" data-testid="current-actor-panel">
    <h2 class="resource-section__title">{{ title }}</h2>
    <p class="resource-state__description">
      {{ description }}
    </p>

    <div
      v-if="pending"
      class="resource-state"
      data-testid="current-actor-loading"
    >
      <h3 class="resource-state__title">正在載入帳號</h3>
      <p class="resource-state__description">
        正在載入可切換的目前操作帳號。
      </p>
    </div>

    <div
      v-else-if="error"
      class="resource-state"
      data-testid="current-actor-error"
    >
      <h3 class="resource-state__title">帳號切換器暫時無法使用</h3>
      <p class="resource-state__description">
        {{ error.message }}
      </p>
      <div class="resource-state__actions">
        <button class="resource-action" type="button" @click="refresh()">
          重試
        </button>
      </div>
    </div>

    <div
      v-else-if="accounts.length === 0"
      class="resource-state"
      data-testid="current-actor-empty"
    >
      <h3 class="resource-state__title">尚無帳號</h3>
      <p class="resource-state__description">
        先建立至少一筆開發者或測試者帳號，才能切換目前操作帳號。
      </p>
      <div class="resource-state__actions">
        <NuxtLink class="resource-action" to="/accounts/new">
          建立帳號
        </NuxtLink>
      </div>
    </div>

    <div
      v-else
      class="resource-section__body"
      data-testid="current-actor-ready"
    >
      <label class="resource-field">
        <span class="resource-field__label">已選取帳號</span>
        <select
          v-model="selectedActorId"
          class="resource-select"
          data-testid="current-actor-select"
          name="current_actor_id"
        >
          <option value="">未選擇目前操作帳號</option>
          <option
            v-for="account in accounts"
            :key="account.id"
            :value="account.id"
          >
            {{ account.display_name }} · {{ formatAccountRoleLabel(account.role) }}
          </option>
        </select>
      </label>

      <div class="resource-key-value" data-testid="current-actor-summary">
        <div class="resource-key-value__row">
          <span class="resource-key-value__label">帳號 ID</span>
          <span class="resource-key-value__value">
            {{ selectedAccount?.id || '尚未選擇目前操作帳號。' }}
          </span>
        </div>
        <div class="resource-key-value__row">
          <span class="resource-key-value__label">角色</span>
          <span class="resource-key-value__value">
            {{
              selectedAccount
                ? formatAccountRoleLabel(selectedAccount.role)
                : '建立有擁有者的資源前，請先選擇一筆帳號。'
            }}
          </span>
        </div>
      </div>
    </div>
  </section>
</template>
