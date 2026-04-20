<script setup lang="ts">
import { computed } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import {
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import { fetchCampaigns } from '~/features/campaigns/api'
import { formatCampaignStatusLabel } from '~/features/campaigns/types'
import { formatPlatformLabel } from '~/features/platform-display'
import {
  formatParticipationAssignmentStatusLabel,
  formatParticipationRequestStatusLabel
} from '~/features/participation-requests/types'

useCurrentActorPersistence()

const currentActorId = useCurrentActorId()

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('my-campaigns-accounts', () => fetchAccounts(), {
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
  data: campaignResponse,
  pending: campaignsPending,
  error: campaignsError,
  refresh: refreshCampaigns
} = useAsyncData(
  () => `my-campaigns-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
  async () => {
    if (!currentActorId.value || !isDeveloperActor.value) {
      return {
        items: [],
        total: 0
      }
    }

    return fetchCampaigns({
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

const campaigns = computed(() => campaignResponse.value.items)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header app-page-header">
        <NuxtLink class="resource-shell__breadcrumb" to="/dashboard">Dashboard</NuxtLink>
        <h1 class="resource-shell__title">我的活動</h1>
        <p class="resource-shell__description">
          這個頁面提供開發者端最小的活動工作區，讓你可以集中查看由自己專案推導出的活動，並快速回到專案或活動詳情。
        </p>
        <div class="resource-state__actions app-page-actions">
          <NuxtLink class="resource-action" to="/campaigns">
            查看所有活動
          </NuxtLink>
          <NuxtLink class="resource-action" to="/my/projects">
            查看我的專案
          </NuxtLink>
          <NuxtLink class="resource-action" to="/review/feedback">
            查看審查佇列
          </NuxtLink>
        </div>
      </header>
      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="my-campaigns-actor-error"
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
        data-testid="my-campaigns-actor-loading"
      >
        <h2 class="resource-state__title">載入開發者情境中</h2>
        <p class="resource-state__description">
          正在確認目前操作帳號與可用的開發者活動工作區。
        </p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="my-campaigns-select-actor"
      >
        <h2 class="resource-state__title">請選擇開發者帳號</h2>
        <p class="resource-state__description">
          先選擇目前操作帳號，系統才知道要推導哪一位開發者的活動工作區。
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="my-campaigns-actor-missing"
      >
        <h2 class="resource-state__title">找不到已選擇的帳號</h2>
        <p class="resource-state__description">
          目前找不到你選擇的帳號，請重新選擇一筆可用的開發者帳號。
        </p>
      </section>

      <section
        v-else-if="!isDeveloperActor"
        class="resource-state"
        data-testid="my-campaigns-role-mismatch"
      >
        <h2 class="resource-state__title">開發者工作區需要開發者帳號</h2>
        <p class="resource-state__description">
          目前選到的是{{ formatAccountRoleLabel(currentActor.role) }}帳號。請切換到開發者帳號，再查看我的活動。
        </p>
      </section>

      <template v-else>
        <section class="resource-section" data-testid="my-campaigns-summary">
          <h2 class="resource-section__title">我的活動總覽</h2>
          <div class="app-page-summary-grid">
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">目前帳號</span>
              <strong class="app-page-summary-card__value">{{ currentActor.display_name }}</strong>
              <span class="app-page-summary-card__description">這裡聚焦你目前擁有專案所延伸出的活動集合。</span>
            </article>
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">我的活動</span>
              <strong class="app-page-summary-card__value">{{ campaignResponse.total }}</strong>
              <span class="app-page-summary-card__description">可直接延伸到參與申請審查與回饋審查流程。</span>
            </article>
          </div>
        </section>

        <section
          v-if="campaignsPending"
          class="resource-state"
          data-testid="my-campaigns-loading"
        >
          <h2 class="resource-state__title">載入我的活動中</h2>
          <p class="resource-state__description">
            正在根據目前操作帳號與其擁有的專案推導開發者活動工作區。
          </p>
        </section>

        <section
          v-else-if="campaignsError"
          class="resource-state"
          data-testid="my-campaigns-error"
        >
          <h2 class="resource-state__title">無法載入我的活動</h2>
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
          data-testid="my-campaigns-empty"
        >
          <h2 class="resource-state__title">目前還沒有我的活動</h2>
          <p class="resource-state__description">
            目前這位開發者擁有的專案下還沒有任何活動。你可以先回到我的專案，從專案詳情建立第一個活動。
          </p>
          <div class="resource-state__actions">
            <NuxtLink class="resource-action" to="/my/projects">
              查看我的專案
            </NuxtLink>
          </div>
        </section>

        <section
          v-else
          class="resource-section__body app-page-card-grid"
          data-testid="my-campaigns-list"
        >
          <article
            v-for="campaign in campaigns"
            :key="campaign.id"
            class="resource-card"
            :data-testid="`my-campaign-card-${campaign.id}`"
          >
            <span class="resource-shell__breadcrumb">我的活動</span>
            <h2 class="resource-card__title">{{ campaign.name }}</h2>
            <p class="resource-card__description">
              {{
                campaign.version_label
                  ? `版本 ${campaign.version_label}`
                  : '目前尚未提供版本標記。'
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
              v-if="campaign.participation_summary"
              class="resource-card__meta"
            >
              <span class="resource-card__chip">
                待處理 {{ campaign.participation_summary.pending_requests_count }}
              </span>
              <span class="resource-card__chip">
                已接受待建任務 {{ campaign.participation_summary.accepted_requests_count }}
              </span>
              <span class="resource-card__chip">
                已建立任務 {{ campaign.participation_summary.linked_tasks_count }}
              </span>
            </div>
            <div
              v-if="campaign.participation_summary && campaign.participation_summary.recent_participation_requests.length > 0"
              class="resource-key-value"
            >
              <div
                v-for="request in campaign.participation_summary.recent_participation_requests"
                :key="request.id"
                class="resource-key-value__row"
              >
                <span class="resource-key-value__label">最近候選人</span>
                <span class="resource-key-value__value">
                  {{
                    `${request.tester_account_display_name} / ${request.device_profile_name} / ${formatParticipationRequestStatusLabel(request.status)} / ${formatParticipationAssignmentStatusLabel(request.assignment_status)}`
                  }}
                </span>
              </div>
            </div>
            <p
              v-else-if="campaign.participation_summary"
              class="resource-card__description"
            >
              目前這個活動還沒有參與申請，候選人漏斗維持零狀態。
            </p>
            <div class="resource-state__actions">
              <NuxtLink
                class="resource-action"
                :data-testid="`my-campaign-detail-link-${campaign.id}`"
                :to="`/campaigns/${campaign.id}`"
              >
                開啟活動詳情
              </NuxtLink>
              <NuxtLink
                class="resource-action"
                :data-testid="`my-campaign-project-link-${campaign.id}`"
                :to="`/projects/${campaign.project_id}`"
              >
                查看上游專案
              </NuxtLink>
              <NuxtLink
                class="resource-action"
                :data-testid="`my-campaign-review-link-${campaign.id}`"
                to="/review/participation-requests"
              >
                查看參與申請審查
              </NuxtLink>
            </div>
          </article>
        </section>
      </template>
    </section>
  </main>
</template>
