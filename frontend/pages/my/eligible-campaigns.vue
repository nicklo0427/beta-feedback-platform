<script setup lang="ts">
import { computed } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import { fetchCampaigns } from '~/features/campaigns/api'
import { formatCampaignStatusLabel } from '~/features/campaigns/types'
import { formatPlatformLabel } from '~/features/platform-display'

useCurrentActorPersistence()

const currentActorId = useCurrentActorId()

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('my-eligible-campaigns-accounts', () => fetchAccounts(), {
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
const isTesterActor = computed(() => currentActor.value?.role === 'tester')

const {
  data: campaignResponse,
  pending: campaignsPending,
  error: campaignsError,
  refresh: refreshCampaigns
} = useAsyncData(
  () =>
    `my-eligible-campaigns-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
  async () => {
    if (!currentActorId.value || !isTesterActor.value) {
      return {
        items: [],
        total: 0
      }
    }

    return fetchCampaigns({
      qualifiedForMe: true,
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

const campaigns = computed(() => campaignResponse.value.items)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/">首頁</NuxtLink>
        <h1 class="resource-shell__title">符合資格的活動</h1>
        <p class="resource-shell__description">
          這個頁面提供測試者端最小的資格活動工作區，讓你可以看到目前有哪些活動符合自己擁有的裝置設定檔條件，並快速進入活動詳情。
        </p>
        <div class="resource-state__actions">
          <NuxtLink class="resource-action" to="/campaigns">
            查看所有活動
          </NuxtLink>
          <NuxtLink class="resource-action" to="/my/tasks">
            查看我的任務
          </NuxtLink>
          <NuxtLink class="resource-action" to="/device-profiles">
            查看裝置設定檔
          </NuxtLink>
        </div>
      </header>

      <CurrentActorSelector
        title="測試者資格工作區"
        description="選擇目前正在操作的測試者帳號，系統會依據這位測試者擁有的裝置設定檔推導目前符合資格的活動。"
      />

      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="my-eligible-campaigns-actor-error"
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
        data-testid="my-eligible-campaigns-actor-loading"
      >
        <h2 class="resource-state__title">載入測試者情境中</h2>
        <p class="resource-state__description">
          正在確認目前操作帳號與可用的資格活動工作區。
        </p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="my-eligible-campaigns-select-actor"
      >
        <h2 class="resource-state__title">請選擇測試者帳號</h2>
        <p class="resource-state__description">
          先選擇目前操作帳號，系統才知道要推導哪一位測試者目前符合資格的活動。
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="my-eligible-campaigns-actor-missing"
      >
        <h2 class="resource-state__title">找不到已選擇的帳號</h2>
        <p class="resource-state__description">
          目前找不到你選擇的帳號，請重新選擇一筆可用的測試者帳號。
        </p>
      </section>

      <section
        v-else-if="!isTesterActor"
        class="resource-state"
        data-testid="my-eligible-campaigns-role-mismatch"
      >
        <h2 class="resource-state__title">資格活動工作區需要測試者帳號</h2>
        <p class="resource-state__description">
          目前選到的是{{ formatAccountRoleLabel(currentActor.role) }}帳號。請切換到測試者帳號，再查看符合資格的活動。
        </p>
      </section>

      <template v-else>
        <section class="resource-section" data-testid="my-eligible-campaigns-summary">
          <h2 class="resource-section__title">資格活動總覽</h2>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              目前帳號 {{ currentActor.display_name }}
            </span>
            <span class="resource-shell__meta-chip">
              符合資格的活動 {{ campaignResponse.total }}
            </span>
          </div>
        </section>

        <section
          v-if="campaignsPending"
          class="resource-state"
          data-testid="my-eligible-campaigns-loading"
        >
          <h2 class="resource-state__title">載入符合資格的活動中</h2>
          <p class="resource-state__description">
            正在依據目前操作帳號與其擁有的裝置設定檔推導符合資格的活動。
          </p>
        </section>

        <section
          v-else-if="campaignsError"
          class="resource-state"
          data-testid="my-eligible-campaigns-error"
        >
          <h2 class="resource-state__title">無法載入符合資格的活動</h2>
          <p class="resource-state__description">
            {{ campaignsError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshCampaigns()">
              重試
            </button>
          </div>
        </section>

        <section
          v-else-if="campaigns.length === 0"
          class="resource-state"
          data-testid="my-eligible-campaigns-empty"
        >
          <h2 class="resource-state__title">目前還沒有符合資格的活動</h2>
          <p class="resource-state__description">
            目前這位測試者擁有的裝置設定檔尚未命中任何活動條件。你可以先補充裝置設定檔，或回到活動列表查看條件設定。
          </p>
          <div class="resource-state__actions">
            <NuxtLink class="resource-action" to="/device-profiles">
              查看裝置設定檔
            </NuxtLink>
            <NuxtLink class="resource-action" to="/campaigns">
              查看所有活動
            </NuxtLink>
          </div>
        </section>

        <section
          v-else
          class="resource-section__body"
          data-testid="my-eligible-campaigns-list"
        >
          <article
            v-for="campaign in campaigns"
            :key="campaign.id"
            class="resource-card"
            :data-testid="`my-eligible-campaign-card-${campaign.id}`"
          >
            <span class="resource-shell__breadcrumb">符合資格的活動</span>
            <h2 class="resource-card__title">{{ campaign.name }}</h2>
            <p class="resource-card__description">
              {{
                campaign.qualification_summary
                  || '目前這個活動已命中至少一個裝置設定檔。'
              }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">狀態 {{ formatCampaignStatusLabel(campaign.status) }}</span>
              <span class="resource-card__chip">專案 {{ campaign.project_id }}</span>
            </div>
            <div class="resource-card__meta">
              <span
                v-for="platform in campaign.target_platforms"
                :key="platform"
                class="resource-card__chip"
              >
                {{ formatPlatformLabel(platform) }}
              </span>
            </div>
            <div
              v-if="campaign.qualifying_device_profiles?.length"
              class="resource-card__meta"
              :data-testid="`my-eligible-campaign-chips-${campaign.id}`"
            >
              <span
                v-for="deviceProfile in campaign.qualifying_device_profiles"
                :key="deviceProfile.id"
                class="resource-card__chip"
              >
                命中裝置 {{ deviceProfile.name }}
              </span>
            </div>
            <div class="resource-state__actions">
              <NuxtLink
                class="resource-action"
                :data-testid="`my-eligible-campaign-detail-link-${campaign.id}`"
                :to="`/campaigns/${campaign.id}`"
              >
                開啟活動詳情
              </NuxtLink>
            </div>
          </article>
        </section>
      </template>
    </section>
  </main>
</template>
